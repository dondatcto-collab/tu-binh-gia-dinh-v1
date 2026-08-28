from loi.ket_qua.schema_v25 import PRODUCT_SCHEMA_VERSION, canonicalize_v25


def test_canonicalize_promotes_old_component_without_losing_traceability():
    out = canonicalize_v25({"schema_version": "2.3-alpha.1", "kind": "personal_period", "numeric_score": None})
    assert out["schema_version"] == PRODUCT_SCHEMA_VERSION == "2.5-alpha.1"
    assert out["product_schema_version"] == "2.5-alpha.1"
    assert out["component_schema_version"] == "2.3-alpha.1"
    assert out["numeric_score"] is None
    assert out["numeric_score_status"] == "LOCKED_OFF"


def test_canonicalize_keeps_v25_component_clean():
    out = canonicalize_v25({"schema_version": "2.5-alpha.1", "kind": "event_search", "numeric_score_status": "LOCKED_OFF"})
    assert out["schema_version"] == "2.5-alpha.1"
    assert out["product_schema_version"] == "2.5-alpha.1"
    assert "component_schema_version" not in out


def test_hour_component_can_remain_24_under_public_25():
    out = canonicalize_v25({"schema_version": "2.4-alpha.1", "kind": "personal_hour_reference"})
    assert out["schema_version"] == "2.5-alpha.1"
    assert out["component_schema_version"] == "2.4-alpha.1"
    assert out["numeric_score"] is None
    assert out["numeric_score_status"] == "LOCKED_OFF"
