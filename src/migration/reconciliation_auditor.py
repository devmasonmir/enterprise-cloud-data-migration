"""Reconciliation and Data Parity Auditor."""
import hashlib
from typing import List, Dict, Any

class ReconciliationAuditor:
    @staticmethod
    def audit_parity(source_count: int, target_count: int, source_sum: float, target_sum: float) -> Dict[str, Any]:
        count_diff = abs(source_count - target_count)
        sum_diff = round(abs(source_sum - target_sum), 2)
        passed = (count_diff == 0) and (sum_diff < 0.01)

        return {
            "row_count_parity": {"source": source_count, "target": target_count, "passed": count_diff == 0},
            "financial_sum_parity": {"source": source_sum, "target": target_sum, "passed": sum_diff < 0.01},
            "overall_audit_passed": passed
        }
