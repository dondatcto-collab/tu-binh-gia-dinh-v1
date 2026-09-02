from pathlib import Path
import yaml


def test_recent_rule_goldens_remain_pending_not_source_approved():
    root=Path("du_lieu/ca_vang/GOLD-HK")
    checked=[]
    for path in sorted(root.glob("HK-*.yaml")):
        raw=yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        case_id=str(raw.get("case_id") or "")
        if case_id.startswith("HK-"):
            try: number=int(case_id.split("-")[1])
            except (ValueError,IndexError): continue
            if number>=17:
                checked.append(case_id)
                assert raw.get("review_status")=="PENDING", path.name
    assert "HK-0027" in checked
    assert "HK-0028" in checked
