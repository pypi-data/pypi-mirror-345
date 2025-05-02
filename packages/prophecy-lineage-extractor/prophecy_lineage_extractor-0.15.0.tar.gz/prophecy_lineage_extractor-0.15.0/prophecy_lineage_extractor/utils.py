import json
import logging
import logging
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import pandas as pd
import sqlparse
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.workbook import Workbook

from prophecy_lineage_extractor import constants
from prophecy_lineage_extractor.constants import (
    OUTPUT_DIR,
    MONITOR_TIME_ENV,
    MONITOR_TIME_DEFAULT, RUN_FOR_ALL_PIPELINES,
)
from prophecy_lineage_extractor.constants import PROPHECY_URL

FILE_COUNTER = 1

def safe_env_variable(var_name):
    if var_name not in os.environ:
        logging.error(
            f"[ERROR]: Environment variable '{var_name}' is not set, Please set this value to continue."
        )
        raise Exception(f"Environment variable '{var_name}' is not set")
    return os.environ[var_name]  # Optional: return the value if needed.

def get_prophecy_name(id):
    return id.split("/")[2]

def get_safe_datasetId(datasetId):
    return str(datasetId).split("/")[2]


def get_ws_url():
    prophecy_url = safe_env_variable(PROPHECY_URL)
    try:
        # Parse the URL
        parsed_url = urlparse(prophecy_url)

        # # Ensure the URL uses HTTPS
        # if parsed_url.scheme != "https":
        #     raise ValueError("Invalid URL. Must start with 'https://'.")

        # Remove 'www.' from the netloc (hostname)
        netloc = parsed_url.netloc.replace("www.", "")

        # Create the WebSocket URL

        # Create the WebSocket URL
        websocket_url = parsed_url._replace(
            scheme="wss", netloc=netloc, path="/api/lineage/ws"
        )

        # Return the reconstructed URL without trailing slashes
        return urlunparse(websocket_url).rstrip("/")
    except Exception as e:
        raise ValueError(f"Error processing URL: {e}")


def get_graphql_url():
    prophecy_url = safe_env_variable(PROPHECY_URL)

    try:
        parsed_url = urlparse(prophecy_url)
        # # Ensure the URL uses HTTPS
        # if parsed_url.scheme not in ["https", "http"]:
        #     raise ValueError("Invalid URL. Must start with 'https://' or 'http://'.")

        # Remove 'www.' from the netloc (hostname)
        netloc = parsed_url.netloc.replace("www.", "")
        # Append '/api/md/graphql' to the path
        path = parsed_url.path.rstrip("/") + "/api/md/graphql"
        # Create the modified URL
        modified_url = parsed_url._replace(netloc=netloc, path=path)
        # Return the reconstructed URL
        return urlunparse(modified_url)

    except Exception as e:
        raise ValueError(f"Error processing URL: {e}")


def send_email(project_id, file_path: Path, pipeline_id_list = []):
    # Get SMTP credentials and email info from environment variables
    smtp_host = safe_env_variable("SMTP_HOST")
    smtp_port = int(safe_env_variable("SMTP_PORT"))  # with default values
    smtp_username = safe_env_variable("SMTP_USERNAME")
    smtp_password = safe_env_variable("SMTP_PASSWORD")
    receiver_email = safe_env_variable("RECEIVER_EMAIL")

    if not all([smtp_host, smtp_port, smtp_username, smtp_password, receiver_email]):
        raise ValueError("Missing required environment variables for SMTP or email.")

    # Create email message
    msg = MIMEMultipart()
    msg["From"] = smtp_username
    msg["To"] = receiver_email
    msg["Subject"] = (
        f"Prophecy Lineage report for Pipeline: {get_prophecy_name(project_id)}"
    )

    # Email body
    body = (
        f"Dear user,\n\tPlease find the attached Prophecy Lineage Excel report for "
        f"Project Id: {project_id}; pipeline_ids = {pipeline_id_list} \n\nThanks and regards,\n\tProphecy Team"
    )
    msg.attach(MIMEText(body, "plain"))

    # Attach Excel file
    attachment_name = file_path.name
    with open(file_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition", f"attachment; filename= {attachment_name}"
        )
        msg.attach(part)

    # Send email via SMTP
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            logging.info(f"Email sent successfully to {receiver_email}")
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")
        raise e


def _is_sql(expr):
    sql_keywords = {
        "SELECT",
        "INSERT",
        "UPDATE",
        "DELETE",
        "CREATE",
        "DROP",
        "ALTER",
        "FROM",
        "WHERE",
        "JOIN",
    }
    python_keywords = {
        ".",
        "def",
        "lambda",
        "import",
        "class",
        "return",
        "self",
        "=",
        "(",
        ")",
    }
    scala_keywords = {
        "val",
        "var",
        "def",
        "object",
        "class",
        "case",
        "match",
        "=>",
        ":",
        "implicit",
    }

    if any(py_kw in expr for py_kw in python_keywords) or any(
        scala_kw in expr for scala_kw in scala_keywords
    ):
        return False
    words = expr.strip().upper().split()
    return any(word in sql_keywords for word in words)


def format_sql(expr):
    try:
        # if _is_sql(expr):
        formatted_query = sqlparse.format(expr, reindent=True, keyword_case="upper")
        logging.info("query formatted.")
        return formatted_query
    # else:
    #     return expr
    except Exception as e:
        logging.error(
            f"Error occurred while formatting sql expression, returning original: \n {expr}\n error: {e}"
        )
        return expr


def get_monitor_time():
    try:
        return int(os.environ.get(MONITOR_TIME_ENV, MONITOR_TIME_DEFAULT))
    except ValueError:
        return int(MONITOR_TIME_DEFAULT)


def debug(json_msg, msg_name=None, pause = False):
    global FILE_COUNTER
    Path("debug_jsons/").mkdir(parents=True, exist_ok=True)
    if msg_name is None:
        file_nm = f"debug_jsons/debug_file_{FILE_COUNTER}.json"
    else:
        file_nm = f"debug_jsons/debug_{msg_name}_file_{FILE_COUNTER}.json"
    with open(file_nm, "w") as fp:
        json.dump(json_msg, fp, indent=2)
    FILE_COUNTER = FILE_COUNTER + 1
    if pause:
        import pdb
        pdb.set_trace()

