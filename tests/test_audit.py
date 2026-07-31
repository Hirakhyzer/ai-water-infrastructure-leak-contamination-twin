from watertwin.audit import append_record, verify_log


def test_audit_log_verifies_hash_chain(tmp_path):
    path = tmp_path / "audit" / "water.jsonl"
    append_record(path, {"run": 1, "purpose": "synthetic water test"})
    append_record(path, {"run": 2, "purpose": "synthetic water test"})
    result = verify_log(path)
    assert result["valid"] is True
    assert result["record_count"] == 2
