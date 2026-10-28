from decimal import Decimal
import sqlite3
import unittest

from src.migration.incremental_extractor import IncrementalExtractor
from src.migration.reconciliation_auditor import ReconciliationAuditor


class MigrationPipelineTests(unittest.TestCase):
    def test_incremental_query_builder_returns_bound_parameters(self):
        ext = IncrementalExtractor("analytics.accounts", "updated_at")
        query, parameters = ext.build_extract_query("2026-01-01", "2026-01-02")

        self.assertEqual(
            query,
            "SELECT * FROM analytics.accounts "
            "WHERE updated_at > :last_watermark "
            "AND updated_at <= :current_watermark",
        )
        self.assertEqual(
            parameters,
            {
                "last_watermark": "2026-01-01",
                "current_watermark": "2026-01-02",
            },
        )

    def test_watermark_values_are_never_interpolated_into_query(self):
        ext = IncrementalExtractor("accounts", "updated_at")
        suspicious_value = "2026-01-01' OR 1=1 --"
        query, parameters = ext.build_extract_query(
            suspicious_value, "2026-01-02"
        )

        self.assertNotIn(suspicious_value, query)
        self.assertEqual(parameters["last_watermark"], suspicious_value)

    def test_parameterized_query_executes_with_expected_window(self):
        ext = IncrementalExtractor("accounts", "updated_at")
        query, parameters = ext.build_extract_query("2026-01-01", "2026-01-02")

        with sqlite3.connect(":memory:") as connection:
            connection.execute(
                "CREATE TABLE accounts (account_id INTEGER, updated_at TEXT)"
            )
            connection.executemany(
                "INSERT INTO accounts VALUES (?, ?)",
                (
                    (1, "2026-01-01"),
                    (2, "2026-01-01 12:00:00"),
                    (3, "2026-01-02"),
                    (4, "2026-01-03"),
                ),
            )
            rows = connection.execute(query, parameters).fetchall()

        self.assertEqual(rows, [(2, "2026-01-01 12:00:00"), (3, "2026-01-02")])

    def test_unsafe_sql_identifiers_are_rejected(self):
        unsafe_identifiers = (
            "accounts; DROP TABLE accounts",
            "accounts where 1=1",
            "analytics..accounts",
            "account-name",
            '"accounts"',
            "",
        )
        for identifier in unsafe_identifiers:
            with self.subTest(identifier=identifier):
                with self.assertRaisesRegex(ValueError, "SQL identifier"):
                    IncrementalExtractor(identifier, "updated_at")
                with self.assertRaisesRegex(ValueError, "SQL identifier"):
                    IncrementalExtractor("accounts", identifier)

    def test_none_watermark_bounds_are_rejected(self):
        ext = IncrementalExtractor("accounts", "updated_at")
        for last_watermark, current_watermark in (
            (None, "2026-01-02"),
            ("2026-01-01", None),
        ):
            with self.subTest(
                last_watermark=last_watermark,
                current_watermark=current_watermark,
            ):
                with self.assertRaisesRegex(ValueError, "cannot be None"):
                    ext.build_extract_query(last_watermark, current_watermark)

    def test_reconciliation_audit(self):
        audit = ReconciliationAuditor.audit_parity(
            1000, 1000, 50000.0, 50000.0
        )
        self.assertTrue(audit["overall_audit_passed"])

    def test_reconciliation_fail(self):
        audit = ReconciliationAuditor.audit_parity(
            1000, 990, 50000.0, 49500.0
        )
        self.assertFalse(audit["overall_audit_passed"])

    def test_financial_tolerance_boundaries_in_both_directions(self):
        cases = [
            ("0.004", True),
            ("0.006", True),
            ("0.009999", True),
            ("0.01", False),
            ("0.010001", False),
        ]
        for difference, passed in cases:
            for sign in (1, -1):
                with self.subTest(difference=difference, sign=sign):
                    source = Decimal("100.00")
                    target = source + sign * Decimal(difference)
                    audit = ReconciliationAuditor.audit_parity(
                        10, 10, source, target
                    )
                    self.assertEqual(
                        audit["financial_sum_parity"]["passed"], passed
                    )
                    self.assertEqual(audit["overall_audit_passed"], passed)

    def test_float_subcent_difference_passes(self):
        audit = ReconciliationAuditor.audit_parity(10, 10, 100.0, 100.006)
        self.assertTrue(audit["overall_audit_passed"])

    def test_large_decimal_totals_preserve_cent_difference(self):
        audit = ReconciliationAuditor.audit_parity(
            10,
            10,
            Decimal("1000000000000000.00"),
            Decimal("1000000000000000.01"),
        )
        self.assertFalse(audit["overall_audit_passed"])

    def test_non_finite_totals_are_rejected(self):
        values = (
            float("nan"),
            float("inf"),
            float("-inf"),
            Decimal("NaN"),
            Decimal("sNaN"),
            Decimal("Infinity"),
            Decimal("-Infinity"),
        )
        for value in values:
            for source, target in ((value, 100), (100, value)):
                with self.subTest(source=str(source), target=str(target)):
                    with self.assertRaisesRegex(ValueError, "finite"):
                        ReconciliationAuditor.audit_parity(
                            10, 10, source, target
                        )

    def test_invalid_row_counts_are_rejected(self):
        invalid_counts = (-1, 1.0, True, "10", None)
        for value in invalid_counts:
            for source_count, target_count in ((value, 10), (10, value)):
                with self.subTest(
                    source_count=source_count, target_count=target_count
                ):
                    with self.assertRaisesRegex(
                        ValueError, "non-negative integers"
                    ):
                        ReconciliationAuditor.audit_parity(
                            source_count, target_count, 100, 100
                        )

    def test_row_count_mismatch_fails_with_matching_totals(self):
        audit = ReconciliationAuditor.audit_parity(10, 9, 100, 100)
        self.assertFalse(audit["row_count_parity"]["passed"])
        self.assertTrue(audit["financial_sum_parity"]["passed"])
        self.assertFalse(audit["overall_audit_passed"])

    def test_empty_batches_pass(self):
        audit = ReconciliationAuditor.audit_parity(0, 0, 0, 0)
        self.assertTrue(audit["overall_audit_passed"])

    def test_report_preserves_supplied_values(self):
        source, target = Decimal("12.345"), 12.346
        audit = ReconciliationAuditor.audit_parity(10, 10, source, target)
        self.assertEqual(audit["financial_sum_parity"]["source"], source)
        self.assertEqual(audit["financial_sum_parity"]["target"], target)


if __name__ == "__main__":
    unittest.main()
