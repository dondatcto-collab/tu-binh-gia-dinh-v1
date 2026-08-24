from loi.linh_vuc.cong_viec import WORK_POLICY_RULE, WORK_RULESET_VERSION, danh_gia_cong_viec


def raw_work(*, state="SUPPORT", group="AUTHORITY", natal_status="READY"):
    dg = {
        "state": state,
        "theme": {
            "theme_group": group,
            "theme": "Trách nhiệm, quy tắc và vị trí công việc",
            "ten_god": "CHINH_QUAN",
            "ten_god_vi": "Chính Quan",
            "rule_id": "BT-TT-0001",
            "source_id": "SRC-ZPZQ",
            "verification_status": "VERIFIED",
        },
        "natal_pattern": {"status": natal_status, "pattern": "ZHENG_GUAN"},
        "branch_impacts": [],
        "rule_ids": ["BT-TT-0001", "BT-CC-0001"],
        "source_ids": ["SRC-ZPZQ"],
    }
    return {"chuyen_sau": {"ngay": {"danh_gia": dg}, "thang": {"danh_gia": dg}}}


def test_work_support_requires_relevant_theme_and_ready_natal_pattern():
    out = danh_gia_cong_viec(raw_work(), scope="day")
    assert out["state"] == "SUPPORT"
    assert out["label"] == "Hỗ trợ công việc"
    assert out["domain"] == "work"
    assert out["ruleset_version"] == WORK_RULESET_VERSION
    assert WORK_POLICY_RULE in out["rule_ids"]
    assert "SRC-ZPZQ" in out["source_ids"]
    assert "thăng chức" not in out["plain_explanation"].lower()


def test_work_caution_is_not_rendered_as_job_loss_prediction():
    out = danh_gia_cong_viec(raw_work(state="CAUTION", group="OUTPUT"), scope="month")
    assert out["state"] == "CAUTION"
    assert out["label"] == "Nên thận trọng trong công việc"
    text = (out["plain_explanation"] + " " + " ".join(out["cautions"])).lower()
    assert "mất việc" in text
    assert "chắc chắn mất việc" in text


def test_wealth_theme_cannot_be_reused_as_work_conclusion():
    out = danh_gia_cong_viec(raw_work(group="WEALTH"), scope="day")
    assert out["state"] == "INSUFFICIENT"
    assert out["confidence_state"] == "Chưa đủ căn cứ"
    assert "không dùng tín hiệu tài" in out["plain_explanation"].lower()


def test_descriptive_only_never_becomes_work_advice():
    out = danh_gia_cong_viec(raw_work(state="DESCRIPTIVE_ONLY", natal_status="AMBIGUOUS"), scope="day")
    assert out["state"] == "INSUFFICIENT"
    assert "không ép kết luận" in out["plain_explanation"].lower()


def test_work_domain_has_no_numeric_score_field_or_ranking_math():
    out = danh_gia_cong_viec(raw_work(group="RESOURCE"), scope="day")
    assert "score" not in out
    assert out["confidence_state"] == "Căn cứ vừa"


def test_only_day_and_month_are_supported_in_v2_1():
    out = danh_gia_cong_viec(raw_work(), scope="year")
    assert out["state"] == "INSUFFICIENT"
    assert "chỉ hỗ trợ ngày và tháng" in out["plain_explanation"].lower()
