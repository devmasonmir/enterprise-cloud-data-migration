import pytest
from src.migration.incremental_extractor import IncrementalExtractor
from src.migration.reconciliation_auditor import ReconciliationAuditor

def test_incremental_query_builder():
    ext = IncrementalExtractor("accounts", "updated_at")
    q = ext.build_extract_query("2026-01-01", "2026-01-02")
    assert "WHERE updated_at > '2026-01-01'" in q
    assert "AND updated_at <= '2026-01-02'" in q

def test_reconciliation_audit():
    audit = ReconciliationAuditor.audit_parity(1000, 1000, 50000.0, 50000.0)
    assert audit["overall_audit_passed"] is True

def test_reconciliation_fail():
    audit = ReconciliationAuditor.audit_parity(1000, 990, 50000.0, 49500.0)
    assert audit["overall_audit_passed"] is False
