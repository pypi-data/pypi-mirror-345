import os
import json
import pandas as pd
from pathlib import Path
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class BaseWriter(ABC):
    def __init__(self, project_id: str, output_dir: str, run_for_all: bool):
        self.project_id = project_id
        self.output_dir = Path(output_dir)
        self.temp_csv_path = Path(os.path.join(self.output_dir, 'temp_files'))
        self.run_for_all = run_for_all

    def get_output_path(self, pipeline_nm_full_str = None):
        """Get final output path with correct format extension"""
        if pipeline_nm_full_str is None:
            return Path(os.path.join(self.output_dir, f"lineage_{self.project_id}.{self.fmt}"))
        else:
            return Path(os.path.join(self.output_dir, f"lineage_{self.project_id}_{pipeline_nm_full_str}.{self.fmt}"))

    @property
    @abstractmethod
    def fmt(self) -> str:
        """File format extension (e.g., 'xlsx', 'csv')"""
        pass

    @property
    @abstractmethod
    def format(self) -> str:
        """Writer format ('excel', 'openLineage')"""
        pass

    def read_csvs(self, pipeline_id: Optional[str] = None,
                  datasets: Optional[List[str]] = None) -> pd.DataFrame:
        """Read CSV files into DataFrame from temp directory"""
        dfs = []
        logging.info(f"DEBUG_WRITE: Reading CSVs from path = {self.temp_csv_path}")
        for csv_file in self.temp_csv_path.glob('*.csv'):
            if self._should_process_file(csv_file, pipeline_id, datasets):
                dfs.append(pd.read_csv(csv_file))
            # import pdb
            # pdb.set_trace()
        return pd.concat(dfs).drop_duplicates() if len(dfs) > 0 else pd.DataFrame()

    def _should_process_file(self, csv_path: Path,
                             pipeline_id: Optional[str],
                             datasets: Optional[List[str]]) -> bool:
        base_condition = str(self.project_id) in csv_path.name

        if not pipeline_id:
            return base_condition
        return (
            f"lineage_{self.project_id}_{self._get_name(pipeline_id)}" in csv_path.name
        ) and base_condition

    def _get_name(self, id: str) -> str:
        """Extract safe name from ID"""
        return id.split("/")[-1]

    def write_temp_file(self, df: pd.DataFrame, dataset_id: str, pipeline_id: str = None):
        """Write temporary CSV file for a dataset"""
        if df.empty:
            logging.info("CSV_WRITER: Received empty DataFrame, nothing to write.")
            return

        # Create filename based on parameters
        if pipeline_id:
            filename = f"lineage_{self.project_id}_{self._get_name(pipeline_id)}_{self._get_name(dataset_id)}.csv"
        else:
            filename = f"lineage_{self.project_id}_{self._get_name(dataset_id)}.csv"

        # Ensure temp directory exists
        self.temp_csv_path.mkdir(parents=True, exist_ok=True)
        file_path = self.temp_csv_path / filename

        # Append to CSV or create new
        mode = 'a' if file_path.exists() else 'w'
        header = not file_path.exists()

        try:
            df.to_csv(file_path, mode=mode, header=header, index=False)
            logging.info(f"Wrote temporary data to {file_path}")
        except Exception as e:
            logging.error(f"Failed to write temp file {file_path}: {str(e)}")
            raise

    def append_to_csv(self, df: pd.DataFrame, file_name: str):
        """
        Append a DataFrame to an existing CSV file or create a new one if it doesn't exist.

        :param df: The DataFrame to append.
        :param file_name: The name of the CSV file.
        """
        # Ensure the temporary CSV directory exists
        self.temp_csv_path.mkdir(parents=True, exist_ok=True)

        file_path = self.temp_csv_path / file_name

        if df.empty:
            logging.info("CSV_WRITER: Received an empty DataFrame, nothing to write.")
            return

        try:
            # Append data to a CSV file, creating it if it doesn't exist
            df.to_csv(file_path, mode='a', header=not file_path.exists(), index=False)
            logging.info(f"CSV_WRITER: Appended data to {file_path}")
        except Exception as e:
            logging.error(f"Failed to append data to {file_path}: {str(e)}")
            raise

    def delete_temp_files(self):
        path = self.temp_csv_path
        self.delete_file(path, recursive=True)

    def delete_file(self, path, recursive=False):
        """
        Delete a file or directory.

        :param path: The path of the file or directory to delete.
        :param recursive: If True and the path is a directory, delete all contents recursively.
        """
        if not path.exists():
            logging.info(f"{path} does not exist. Nothing to delete.")
            return

        try:
            if path.is_file():
                path.unlink()
                logging.info(f"Deleted file {path}")
            elif path.is_dir():
                for child in path.iterdir():
                    if child.is_file():
                        child.unlink()
                    elif child.is_dir():
                        self.delete_file(child, recursive=True)
                path.rmdir()
                logging.info(f"Deleted directory {path}")
            else:
                logging.warning(f"{path} is not a valid file or directory.")
        except Exception as e:
            logging.error(f"Failed to delete {path}: {str(e)}")

    def write_to_format(self, pipeline_dataset_map: Dict) -> Path:
        raise NotImplementedError("write_to_format not defined")

    def write(self, pipeline_dataset_map: Dict) -> Path:
        logging.info(f"STARTED WRITING TO DATA FORMAT {self.format} has begun. Project Level File Name = {self.get_output_path()}")
        logging.info(f"PIPELINE_DATASET_MAP = {json.dumps(pipeline_dataset_map, indent=2)}")
        logging.info(f"CURRENT WORKING DIRECTORY = {os.getcwd()}; CURRENT_TEMP_FILE_DIR = {self.temp_csv_path}")
        logging.info(f"FILES IN CURRENT WORKING DIRECTORY = {os.listdir(os.getcwd())}")
        logging.info(f"FILES IN TEMP FILE DIRECTORY = {os.listdir(self.temp_csv_path)}")
        self.write_to_format(pipeline_dataset_map)
        self.delete_temp_files()
        logging.info(f"ENDED WRITING TO DATA FORMAT {self.format} has ended. Project Level File Name = {self.get_output_path()}")

