from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_predict_low_risk():
    """正常订单 → low risk"""
    resp = client.post("/risk/predict", json={
        "order_amount": 200,
        "order_count_1h": 1,
        "order_count_24h": 3,
        "hour_of_day": 14,
        "product_category": "啤酒",
        "is_new_device": False,
        "is_new_user": False,
        "same_ip_phone_count": 1,
        "same_device_account_count": 1,
        "recent_batch_reg_count": 0,
        "return_rate": 0.0,
        "cod_reject_rate": 0.0,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["risk_level"] == "low"
    assert data["score"] == 0
    assert len(data["reasons"]) == 0


def test_predict_high_risk():
    """多项规则同时命中 → high risk"""
    resp = client.post("/risk/predict", json={
        "order_amount": 6000,
        "order_count_1h": 7,
        "order_count_24h": 25,
        "hour_of_day": 3,
        "product_category": "白酒",
        "ip_address": "10.0.0.1",
        "device_id": "dev-001",
        "is_new_device": True,
        "is_new_user": True,
        "days_since_registration": 0,
        "same_ip_phone_count": 6,
        "same_device_account_count": 4,
        "recent_batch_reg_count": 25,
        "return_rate": 0.4,
        "cod_reject_rate": 0.35,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["risk_level"] == "high"
    assert data["score"] == 100
    # 9 条规则至少命中 7 条以上
    triggered = [d for d in data["details"] if d["triggered"]]
    assert len(triggered) >= 7


def test_predict_medium_risk():
    """部分规则命中 → medium risk"""
    resp = client.post("/risk/predict", json={
        "order_amount": 3000,
        "order_count_1h": 4,
        "order_count_24h": 10,
        "hour_of_day": 22,
        "product_category": "葡萄酒",
        "is_new_device": True,
        "is_new_user": False,
        "same_ip_phone_count": 2,
        "same_device_account_count": 1,
        "recent_batch_reg_count": 0,
        "return_rate": 0.1,
        "cod_reject_rate": 0.0,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["risk_level"] == "medium"


def test_predict_validation_error():
    """缺少必填字段 → 422"""
    resp = client.post("/risk/predict", json={"order_amount": -1})
    assert resp.status_code == 422


def test_rule_details_in_response():
    """响应中包含每条规则的明细"""
    resp = client.post("/risk/predict", json={
        "order_amount": 200,
        "order_count_1h": 1,
        "order_count_24h": 3,
        "hour_of_day": 14,
        "is_new_device": False,
        "is_new_user": False,
        "same_ip_phone_count": 0,
        "same_device_account_count": 0,
        "recent_batch_reg_count": 0,
        "return_rate": 0.0,
        "cod_reject_rate": 0.0,
    })
    data = resp.json()
    assert "details" in data
    # 全部 9 条规则都有明细记录（不管是否命中）
    assert len(data["details"]) == 9
    for d in data["details"]:
        assert "rule_name" in d
        assert "triggered" in d
        assert "score" in d
