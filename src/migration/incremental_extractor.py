"""Watermark-based incremental extractor."""

import logging
import re
from typing import Any, Dict, Tuple


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_QUALIFIED_IDENTIFIER = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*$"
)


class IncrementalExtractor:
    """Build safe, parameterized incremental extraction statements."""

    def __init__(self, table_name: str, watermark_column: str):
        self.table_name = self._validate_identifier(table_name, "table_name")
        self.watermark_column = self._validate_identifier(
            watermark_column, "watermark_column"
        )

    @staticmethod
    def _validate_identifier(identifier: str, field_name: str) -> str:
        """Accept conservative SQL identifiers, including schema qualification."""
        if not isinstance(identifier, str) or not _QUALIFIED_IDENTIFIER.fullmatch(
            identifier
        ):
            raise ValueError(
                f"{field_name} must be a simple or dot-qualified SQL identifier"
            )
        return identifier

    def build_extract_query(
        self, last_watermark: Any, current_watermark: Any
    ) -> Tuple[str, Dict[str, Any]]:
        """Return a query and named parameters for an exclusive-inclusive window.

        The caller must pass the returned parameter mapping to its database driver;
        watermark values are deliberately never interpolated into SQL text.
        """
        if last_watermark is None or current_watermark is None:
            raise ValueError("Watermark bounds cannot be None")

        query = (
            f"SELECT * FROM {self.table_name} "
            f"WHERE {self.watermark_column} > :last_watermark "
            f"AND {self.watermark_column} <= :current_watermark"
        )
        parameters = {
            "last_watermark": last_watermark,
            "current_watermark": current_watermark,
        }
        return query, parameters

    def extract_mock_batch(self, count: int = 500) -> Dict[str, Any]:
        logger.info(
            "Extracted %s incremental records from %s", count, self.table_name
        )
        return {
            "table": self.table_name,
            "records_count": count,
            "status": "COMPLETED",
        }


if __name__ == "__main__":
    extractor = IncrementalExtractor("sap_orders", "last_modified_timestamp")
    sql, params = extractor.build_extract_query(
        "2026-09-01 00:00:00", "2026-09-17 00:00:00"
    )
    print("Extract Query:", sql)
    print("Parameters:", params)
