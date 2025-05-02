import argparse
import traceback
import json
import logging
import os
import threading
import time
from datetime import datetime, timedelta

import websocket

from prophecy_lineage_extractor import messages
from prophecy_lineage_extractor.constants import (
    PROPHECY_PAT, LONG_SLEEP_TIME, SLEEP_TIME,
)
from prophecy_lineage_extractor.graphql import checkout_branch
from prophecy_lineage_extractor.utils import (
    safe_env_variable, get_ws_url,
    get_monitor_time, send_email
)
from prophecy_lineage_extractor.writer import get_writer
from prophecy_lineage_extractor.ws_handler import WorkflowMessageHandler


class PipelineProcessor:
    def __init__(self, project_id, branch, output_dir, send_email, recursive_extract, run_for_all, fmt='excel', pipeline_id_str=None):
        self.project_id = project_id
        pipeline_id_list = []
        for pipeline_id in pipeline_id_str.split(","):
            if pipeline_id.startswith(f"{project_id}/pipelines"):
                pipeline_id_list.append(pipeline_id)
            else:
                pipeline_id_list.append(f"{project_id}/pipelines/{pipeline_id}")
        self.pipeline_id_list = pipeline_id_list
        self.branch = branch
        self.output_dir = output_dir
        self.send_email = send_email
        self.recursive_extract = recursive_extract.lower() == "true"
        self.last_meaningful_message_time = datetime.now()
        self.workflow_msg_handler = None
        self.ws = None
        self.run_for_all = run_for_all.lower() == "true"
        self.writer = get_writer(fmt)(
                project_id=self.project_id,
                output_dir=self.output_dir,
                run_for_all=self.run_for_all
            )
        self.KEEP_RUNNING = True

    def update_monitoring_time(self):
        self.last_meaningful_message_time = datetime.now()
        logging.warning(
            f"[MONITORING]: Updating idle time, current idle time"
            f"= {datetime.now() - self.last_meaningful_message_time}"
        )

    def on_error(self, ws, error):
        logging.error(f"Error: {str(error)}\nTraceback:\n{traceback.format_exc()}")
        ws.close()
        exit(1)


    def on_close(self, ws, close_status_code, close_msg):
        logging.info("### WebSocket closed ###")

    def on_message(self, ws, message):
        logging.info(f"\n\n### RECEIVED a message### ")
        try:
            json_msg = json.loads(message)
            if "method" in json_msg: # import json  json.dumps(json_msg, indent=2)
                method = json_msg["method"]
                logging.warning(f"method: {method}")
                # debug(json_msg, f'on_msg_{method.replace("/", "__")}')
                if method == "properties/didOpen":
                    self.update_monitoring_time()
                    self.workflow_msg_handler.handle_did_open(ws, json_msg)
                elif method == "properties/didUpdate":
                    self.update_monitoring_time()
                    self.workflow_msg_handler.handle_did_update(ws, json_msg)
                elif method in ["properties/publishDiagnostics", "window/logMessage", "ping"]:
                    pass
                elif method == "error":
                    logging.error(f"Error occurred:\n {json_msg['params']['msg']}")
                    raise Exception(f"Error occurred and we got method='Error'\n {json_msg}")
                else:
                    import pdb
                    pdb.set_trace()
                    raise Exception("method is not found in message", json_msg)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON message: {e}")
            raise e

    def on_open(self, ws):
        self.writer.delete_temp_files()
        logging.info(f"\n\n### SENDING INIT PIPELINE for {self.project_id} ### ")
        # for pipeline_id in self.pipeline_id_list:
        ws.send(messages.init_pipeline(self.project_id, self.pipeline_id_list[0]))
        time.sleep(LONG_SLEEP_TIME)
        self.workflow_msg_handler = WorkflowMessageHandler(self.writer, self.project_id, self.pipeline_id_list, self.run_for_all, self.recursive_extract)

    def end_ws(self):
        try:
            output_file = self.writer.write(self.workflow_msg_handler.pipeline_dataset_map)
            logging.info(f"Excel report generated")
            if self.send_email:
                send_email(self.project_id, output_file, self.pipeline_id_list)
                logging.info(f"Excel report sent as mail for project_id = {self.project_id} ")
            else:
                logging.info(f"Excel report not sent as mail")

        except Exception as e:
            logging.error(f"Error during WebSocket processing: {e}")
            raise e
        finally:
            self.ws.close()

    def monitor_ws(self):
        logging.info("Monitor thread started.")
        time.sleep(SLEEP_TIME)
        monitor_time = get_monitor_time()
        logging.info(f"[MONITORING] Monitor Time: {monitor_time} seconds")
        while self.ws.keep_running:
            # global KEEP_RUNNING
            if (len(set(self.workflow_msg_handler.datasets_processed)) >= self.workflow_msg_handler.total_index and self.workflow_msg_handler.total_index != -1):
                self.KEEP_RUNNING = False
            if datetime.now() - self.last_meaningful_message_time > timedelta(seconds=monitor_time):
                logging.warning(f"[MONITORING]: No meaningful messages received in the last {monitor_time} seconds, closing websocket")
                self.end_ws()
            elif not self.KEEP_RUNNING:
                logging.warning(f"[MONITORING]: Task Ended. KEEP_RUNNING = {self.KEEP_RUNNING}; Accordingly we are closing websocket.\nTemp Files Processed = {json.dumps(self.workflow_msg_handler.datasets_processed, indent=2)}\nDatasets To Process = {json.dumps(self.workflow_msg_handler.datasets_to_process, indent=2)}")
                self.end_ws()
            else:
                logging.warning(
                    f"[MONITORING]: KEEP_RUNNING={self.KEEP_RUNNING}, Idle time"
                    f"""{datetime.now() - self.last_meaningful_message_time} seconds / {get_monitor_time()} seconds;\n
                         datasets_processed = {len(self.workflow_msg_handler.datasets_processed)} OUT OF {self.workflow_msg_handler.total_index}
                    """,
                )
                if not self.KEEP_RUNNING:
                    logging.warning("COMPLETED REQUIRED TASK: Please end")
                    self.end_ws()
            time.sleep(SLEEP_TIME)
        logging.info("Monitor thread ended.")

    def run_websocket(self):
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(
            get_ws_url(),
            header={"X-Auth-Token": safe_env_variable(PROPHECY_PAT)},
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

        monitor_thread = threading.Thread(target=self.monitor_ws, daemon=True)
        monitor_thread.start()

        self.ws.run_forever()

    def process(self):
        checkout_branch(self.project_id, self.branch)
        logging.info("Starting WebSocket thread..")
        ws_thread = threading.Thread(target=self.run_websocket, daemon=True)
        ws_thread.start()
        ws_thread.join()

def main():
    parser = argparse.ArgumentParser(description="Prophecy Lineage Extractor")
    parser.add_argument("--project-id", type=str, required=True, help="Prophecy Project ID")
    parser.add_argument("--pipeline-id", type=str, required=True, nargs='+', help="Prophecy Pipeline ID(s)")
    parser.add_argument("--send-email", action="store_true", help="Enable verbose output")
    parser.add_argument("--branch", type=str, default="default", help="Branch to run lineage extractor on")
    parser.add_argument("--recursive_extract", type=str, default="true", help="Whether to Recursively include Upstream Source Transformations")
    parser.add_argument("--run_for_all", type=str, default="false", help="Whether to Create Project Level Sheet")
    parser.add_argument("--output-dir", type=str, required=True, help="Output directory inside the project")
    parser.add_argument("--fmt", type=str, required=False, help="What format to write to")
    parser.add_argument("--log-level", type=str, default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Set the logging level")

    args = parser.parse_args()

    # Configure logging with the specified log level
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logging.info(f"Logging level set to {args.log_level}")

    for pipeline_id_str in args.pipeline_id:
        # for pipeline_id in pipeline_id_str.split(","):
        pipeline_output_dir = os.path.join(args.output_dir)
        os.makedirs(pipeline_output_dir, exist_ok=True)
        print(f"pipeline_id={pipeline_id_str}")
        processor = PipelineProcessor(
            project_id=args.project_id,
            branch=args.branch,
            output_dir=pipeline_output_dir,
            send_email=args.send_email,
            recursive_extract=args.recursive_extract,
            run_for_all = args.run_for_all,
            fmt=args.fmt if args.fmt else 'excel',
            pipeline_id_str=pipeline_id_str,
        )
        processor.process()

if __name__ == "__main__":
    main()