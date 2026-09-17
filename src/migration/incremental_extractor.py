"""Watermark-Based Incremental Extractor."""
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IncrementalExtractor:
    def __init__(self, table_name: str, watermark_column: str):
        self.table_name = table_name
        self.watermark_column = watermark_column

    def build_extract_query(self, last_watermark: str, current_watermark: str) -> str:
        return (
            "SELECT * FROM " + self.table_name + " "
            "WHERE " + self.watermark_column + " > '" + last_watermark + "' "
            "AND " + self.watermark_column + " <= '" + current_watermark + "'"
        )

    def extract_mock_batch(self, count: int = 500) -> Dict[str, Any]:
        logger.info("Extracted " + str(count) + " incremental records from " + self.table_name)
        return {"table": self.table_name, "records_count": count, "status": "COMPLETED"}

if __name__ == "__main__":
    extractor = IncrementalExtractor("sap_orders", "last_modified_timestamp")
    q = extractor.build_extract_query("2026-09-01 00:00:00", "2026-09-17 00:00:00")
    print("Extract Query:", q)
