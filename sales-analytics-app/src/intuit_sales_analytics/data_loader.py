import csv
import logging
from typing import List

from .models import SaleRecord


class SalesDataLoader:
    """
    Handles reading and parsing sales data from CSV files.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path

    def load_data(self) -> List[SaleRecord]:
        records = []
        try:
            with open(self.file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row_num, row in enumerate(reader, start=2):  # Header is line 1
                    try:
                        record = SaleRecord.from_csv_row(row)
                        records.append(record)
                    except ValueError as e:
                        logging.warning(
                            f"Skipping malformed row {row_num}: {e}")
        except FileNotFoundError:
            logging.error(f"Error: File not found at {self.file_path}")
            raise
        except Exception as e:
            logging.error(f"Error reading file {self.file_path}: {e}")
            raise

        logging.info(
            f"Successfully loaded {len(records)} records from {self.file_path}")
        return records
