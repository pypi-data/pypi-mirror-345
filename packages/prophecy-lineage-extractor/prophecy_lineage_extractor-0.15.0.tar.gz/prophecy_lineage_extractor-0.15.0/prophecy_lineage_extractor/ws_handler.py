import logging
import os
import time
import traceback

import pandas as pd
import sqlparse
from collections import defaultdict


from prophecy_lineage_extractor import messages
from prophecy_lineage_extractor.constants import (
    PIPELINE_ID,
    DB_COL,
    TABLE_COL,
    COLNAME_COL,
    UPSTREAM_TRANSFORMATION_COL,
    LONG_SLEEP_TIME,
    SLEEP_TIME,
    CATALOG_COL,
    PROCESS_NAME_COL,
    INBOUND_COL
)
from prophecy_lineage_extractor.graphql import get_dataset_info_from_id
from prophecy_lineage_extractor.utils import (
    format_sql, debug,
    get_safe_datasetId, get_prophecy_name
)


class WorkflowMessageHandler:

    def __init__(self, writer, project_id, pipeline_ids, run_for_all = False, recursive_extract = False):
        self.datasets_processed = []
        self.project_id = project_id
        self.pipeline_ids = pipeline_ids
        self.pipeline_dataset_map = {}
        self.datasets_to_process = []
        self.writer = writer
        self.run_for_all = run_for_all
        self.recursive_extract = recursive_extract
        self.total_index = -1
        self.new_set_of_datasets = []

    def _get_lineage_for_given_pipeline(self, json_msg, datasets):
        # debug(json_msg, 'dataset_info', pause = True)
        if (self.run_for_all):
            self.pipeline_ids = [
                process_str for process_str, process_json in
                    json_msg.get("params", {})\
                        .get("lineage", {})\
                        .get("graph", {})\
                        .get("processes", {}).items() if "pipeline" in process_str]
            self.recursive_extract = True
        connections = json_msg.get("params", {})\
            .get("lineage", {})\
            .get("graph", {})\
            .get("connections")
        # Initialize with proper data structures
        # Initialize with automatic key handling
        pipeline_dataset_map = defaultdict(dict)
        dataset_connection_map = defaultdict(str)  # Handles missing keys
        new_set_of_datasets = list()
        total_index = 0
        for connection in connections:
            src = connection.get("source")
            target = connection.get("target")
            # Handle source->target relationships

            if src in self.pipeline_ids:
                if target in datasets:
                    pipeline_dataset_map[src].update({target: "OUTBOUND"} )
                    new_set_of_datasets.append(target)
                    dataset_connection_map[target] = "OUTBOUND"  # Now using defaultdict
                    total_index += 1

            # Handle target->source relationships
            if target in self.pipeline_ids:
                if src in datasets:
                    pipeline_dataset_map[target].update({ src:"INBOUND" })
                    new_set_of_datasets.append(src)
                    dataset_connection_map[src] = "INBOUND"
                    total_index += 1


        # Convert to regular dicts if needed
        self.pipeline_dataset_map.update(dict(pipeline_dataset_map))
        self.new_set_of_datasets += list(new_set_of_datasets)
        if self.total_index == -1:
            self.total_index = total_index
        else:
            self.total_index += total_index
        return list(set(new_set_of_datasets))


    def _get_dataset_from_summary_view(self, json_msg):
        logging.info("viewType is summaryView, getting datasets")
        # Step 2: Extract all datasets from `processes`
        processes = (
            json_msg.get("params", {})
            .get("lineage", {})
            .get("graph", {})
            .get("processes", {})
        )
        # Filter out all entries with component "Dataset" and collect their names
        datasets = [
            info["id"] for info in processes.values() if info.get("component") == "Dataset"
        ]
        logging.info(f"All datasets Total {len(datasets)}:\n {datasets}")
        return datasets


    def _get_lineage_from_detailed_view(self, data):
        logging.info("viewType is detailedDatasetView, getting lineage")
        # Access columns data
        columns = data.get("value", {}).get("dataset", {}).get("columns", [])
        datasetId = data.get("value", {}).get("dataset", {}).get("id", "NA")
        # Extract lineage information for each column
        # Prepare data for DataFrame
        debug(data, 'detailed_view')
        # json_msg.get("value", {}).get("dataset", {}).get("columns", [])
        # [len(column.get("upstreamTransformations", [])) for column in json_msg.get("value", {}).get("dataset", {}).get("columns", [])]
        # [column.get("upstreamTransformations", []) for column in json_msg.get("value", {}).get("dataset", {}).get("columns", [])]
        for pipeline_id in self.pipeline_ids:
            # import pdb
            # pdb.set_trace()
            lineage_data = []
            if self.pipeline_dataset_map[pipeline_id].get(datasetId) is None:
                continue
            for column in columns:
                column_name = column.get("name")
                # to at least add one row for every column
                # if upstream transformations are empty add self as passthrough column
                catalog_name, database_name, table_name = get_dataset_info_from_id(datasetId)
                # self.datasets_to_process
                if (len(column.get("upstreamTransformations", [])) == 0 or
                (self.pipeline_dataset_map[pipeline_id].get(datasetId) == "INBOUND") and
                not self.recursive_extract):
                    lineage_data.append(
                        {
                            # "dataset_id": str(datasetId).split("/")[2],
                            INBOUND_COL: self.pipeline_dataset_map[pipeline_id].get(datasetId),
                            CATALOG_COL: catalog_name if catalog_name else "NA",
                            DB_COL: database_name,
                            TABLE_COL: table_name,
                            COLNAME_COL: column_name,
                            PROCESS_NAME_COL: 'SOURCE',
                            UPSTREAM_TRANSFORMATION_COL: column_name,
                            # "downstream_transformation": ""
                        }
                    )
                    continue

                # Upstream transformations
                for upstream in column.get("upstreamTransformations", []) :
                    # import pdb
                    # pdb.set_trace()
                    # as default pass through value
                    trnsf_pipeline_id = upstream.get("pipeline", {}).get("id", "Unknown")

                    if (trnsf_pipeline_id != pipeline_id and
                            (self.pipeline_dataset_map[pipeline_id].get(datasetId) == "INBOUND" and
                             self.run_for_all == "true")):
                        logging.info(
                            f"skipping transformation for column {column_name} as this belongs to different pipeline: {upstream}"
                        )
                        continue
                    transformations = upstream.get("transformations", [])
                    for transformation in transformations:
                        process_name = transformation.get("processName", "Unknown")
                        if trnsf_pipeline_id != pipeline_id or self.recursive_extract or self.run_for_all:
                            process_name = f"{trnsf_pipeline_id}:{process_name}"
                        # TODO: get expression language from project metadata and then apply this formatting
                        transformation_str = format_sql(
                            transformation.get("transformation", "")
                        )
                        # upstream_transformation = f"{process_name}: {transformation_str}"
                        upstream_transformation = f"{transformation_str}"
                        lineage_data.append(
                            {
                                # "dataset_id": str(datasetId).split("/")[2],
                                INBOUND_COL: self.pipeline_dataset_map[pipeline_id].get(datasetId),
                                CATALOG_COL: catalog_name,
                                DB_COL: database_name,
                                TABLE_COL: table_name,
                                COLNAME_COL: column_name,
                                PROCESS_NAME_COL: process_name,
                                UPSTREAM_TRANSFORMATION_COL: upstream_transformation,
                                # "downstream_transformation": ""
                            }
                        )

            df = pd.DataFrame(lineage_data)
            fl_nm = f"lineage_{self.project_id}_{get_prophecy_name(pipeline_id)}_{get_safe_datasetId(datasetId)}.csv"
            self.writer.append_to_csv(df, fl_nm)
            self.datasets_processed.append(fl_nm)
            print(f"""\n\nNew Datasets Processed for pipeline: {get_prophecy_name(pipeline_id)} \nTemp File: {fl_nm}\n\n""")
            # import pdb; pdb.set_trace()



    def handle_did_open(self, ws, json_msg):
        logging.info("Handling didOpen")
        view_type = (
            json_msg.get("params", {})
            .get("lineage", {})
            .get("metaInfo", {})
            .get("viewType")
        )
        if view_type == "summaryView":
            datasets = self._get_dataset_from_summary_view(json_msg)
            # for every datasets run and get lineage
            debug(json_msg, 'summary_view')
            datasets = self._get_lineage_for_given_pipeline(json_msg, datasets)
            # self.dataset_connection_mapping = dataset_connection_mapping
            self.datasets_to_process = datasets
            for dataset in datasets:
                # change active entity
                logging.info(f"running lineage fetch for dataset {dataset}")

                ws.send(messages.change_active_entity(dataset))
                time.sleep(SLEEP_TIME)
                # get lineage
                ws.send(messages.detailed_view())
                time.sleep(LONG_SLEEP_TIME)

                logging.info(f"Going back to summary view")
                ws.send(messages.summary_view())
                time.sleep(SLEEP_TIME)


    def handle_did_update(self, ws, json_msg):
        # import pdb; pdb.set_trace()
        logging.info("Handling didUpdate")
        for change in json_msg.get("params", {}).get("changes", []):
            # Check if 'viewType' is present and equals 'detailedDatasetView'
            if (
                change.get("value", {}).get("metaInfo", {}).get("viewType")
                == "detailedDatasetView"
            ):
                try:
                    self._get_lineage_from_detailed_view(change)
                except Exception as e:
                    logging.error(f"Error: {str(e)}\nTraceback:\n{traceback.format_exc()}")
                    ws.close()
