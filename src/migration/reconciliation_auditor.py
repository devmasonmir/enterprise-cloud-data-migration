"""Reconcile row counts and financial aggregate totals for migration batches."""
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Union

Amount = Union[int, float, Decimal]


class ReconciliationAuditor:
    @staticmethod
    def _validate_row_count(value: int) -> None:
        """Reject invalid counts before they can produce a misleading audit."""
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError("Row counts must be non-negative integers")

    @staticmethod
    def _coerce_financial_total(value: Amount) -> Decimal:
        """Convert supported numeric totals while rejecting ambiguous inputs."""
        if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
            raise ValueError("Financial totals must be int, float, or Decimal values")

        try:
            total = Decimal(str(value))
        except (InvalidOperation, ValueError) as error:
            raise ValueError(
                "Financial totals must be int, float, or Decimal values"
            ) from error

        if not total.is_finite():
            raise ValueError("Financial totals must be finite")
        return total

    @staticmethod
    def audit_parity(
        source_count: int,
        target_count: int,
        source_sum: Amount,
        target_sum: Amount,
    ) -> Dict[str, Any]:
        """Require valid equal counts and a total difference below 0.01.

        Row counts must be non-negative integers. Decimal inputs preserve
        precision from database NUMERIC/DECIMAL values. Floats are converted
        through their string representation, avoiding extra binary conversion
        noise. Totals must be finite; NaN and infinity raise ValueError.
        Comparisons use the unrounded difference.
        """
        ReconciliationAuditor._validate_row_count(source_count)
        ReconciliationAuditor._validate_row_count(target_count)

        source_total = ReconciliationAuditor._coerce_financial_total(source_sum)
        target_total = ReconciliationAuditor._coerce_financial_total(target_sum)

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

