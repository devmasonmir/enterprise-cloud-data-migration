from decimal import Decimal
import unittest

from src.migration.incremental_extractor import IncrementalExtractor
from src.migration.reconciliation_auditor import ReconciliationAuditor


class MigrationPipelineTests(unittest.TestCase):
    def test_incremental_query_builder(self):
        ext = IncrementalExtractor("accounts", "updated_at")
        query = ext.build_extract_query("2026-01-01", "2026-01-02")
        self.assertIn("WHERE updated_at > '2026-01-01'", query)
        self.assertIn("AND updated_at <= '2026-01-02'", query)

    def test_reconciliation_audit(self):
        audit = ReconciliationAuditor.audit_parity(1000, 1000, 50000.0, 50000.0)
        self.assertTrue(audit["overall_audit_passed"])

    def test_reconciliation_fail(self):
        audit = ReconciliationAuditor.audit_parity(1000, 990, 50000.0, 49500.0)
        self.assertFalse(audit["overall_audit_passed"])

    def test_financial_tolerance_boundaries_in_both_directions(self):
        cases = [
            ("0.004", True), ("0.006", True), ("0.009999", True),
            ("0.01", False), ("0.010001", False),
        ]
        for difference, passed in cases:
            for sign in (1, -1):
                with self.subTest(difference=difference, sign=sign):
                    source = Decimal("100.00")
                    target = source + sign * Decimal(difference)
                    audit = ReconciliationAuditor.audit_parity(10, 10, source, target)
                    self.assertEqual(audit["financial_sum_parity"]["passed"], passed)
                    self.assertEqual(audit["overall_audit_passed"], passed)

    def test_float_subcent_difference_passes(self):
        audit = ReconciliationAuditor.audit_parity(10, 10, 100.0, 100.006)
        self.assertTrue(audit["overall_audit_passed"])

    def test_large_decimal_totals_preserve_cent_difference(self):
        audit = ReconciliationAuditor.audit_parity(
            10, 10, Decimal("1000000000000000.00"), Decimal("1000000000000000.01")
        )
        self.assertFalse(audit["overall_audit_passed"])

    def test_non_finite_totals_are_rejected(self):
        values = (
            float("nan"), float("inf"), float("-inf"),
            Decimal("NaN"), Decimal("sNaN"),
            Decimal("Infinity"), Decimal("-Infinity"),
        )
        for value in values:
            for source, target in ((value, 100), (100, value)):
                with self.subTest(source=str(source), target=str(target)):
                    with self.assertRaisesRegex(ValueError, "finite"):
                        ReconciliationAuditor.audit_parity(10, 10, source, target)

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
