"""Reconcile row counts and financial aggregate totals for migration batches."""
from decimal import Decimal
from typing import Any, Dict, Union

Amount = Union[int, float, Decimal]


class ReconciliationAuditor:
    @staticmethod
    def audit_parity(
        source_count: int,
        target_count: int,
        source_sum: Amount,
        target_sum: Amount,
    ) -> Dict[str, Any]:
        """Require equal counts and an absolute total difference below 0.01.

        Decimal inputs preserve precision from database NUMERIC/DECIMAL values.
        Floats are converted through their string representation, avoiding extra
        binary conversion noise. Totals must be finite; NaN and infinity raise
        ValueError. Comparisons use the unrounded difference.
        """
        source_total = Decimal(str(source_sum))
        target_total = Decimal(str(target_sum))
        if not source_total.is_finite() or not target_total.is_finite():
            raise ValueError("Financial totals must be finite")

        count_passed = source_count == target_count
        sum_passed = abs(source_total - target_total) < Decimal("0.01")

        return {
            "row_count_parity": {
                "source": source_count, "target": target_count, "passed": count_passed,
            },
            "financial_sum_parity": {
                "source": source_sum, "target": target_sum, "passed": sum_passed,
            },
            "overall_audit_passed": count_passed and sum_passed,
        }
