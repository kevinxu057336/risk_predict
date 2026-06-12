import os
os.environ.setdefault("RISK_API_KEY", "")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_predict_low_risk():
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
    triggered = [d for d in data["details"] if d["triggered"]]
    assert len(triggered) >= 7


def test_predict_medium_risk():
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
    resp = client.post("/risk/predict", json={"order_amount": -1})
    assert resp.status_code == 422


def test_rule_details_in_response():
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
    assert len(data["details"]) == 9
    for d in data["details"]:
        assert "rule_name" in d
        assert "triggered" in d
        assert "score" in d


def test_stats_endpoint():
    resp = client.get("/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_predictions" in data
    assert "window" in data
    assert "rule_trigger_rates" in data
    assert "risk_level_distribution" in data
    assert "score_distribution" in data
    assert "amount_distribution" in data
    assert "hour_distribution" in data
    assert data["total_predictions"] > 0


def test_metrics_endpoint():
    resp = client.get("/metrics")
    assert resp.status_code == 200
    body = resp.text
    assert "risk_score" in body
    assert "risk_rule_triggers_total" in body
    assert "risk_level_total" in body
    assert "risk_order_amount" in body
    assert "risk_prediction_total" in body


def test_rule_fault_tolerance():
    from app.services.engine import RiskEngine
    from app.services.rules.base import BaseRule, RuleResult
    from app.models import RiskFeatures

    class BrokenRule(BaseRule):
        name = "broken_rule"
        description = "故意抛异常的规则"

        def evaluate(self, f: RiskFeatures) -> RuleResult:
            raise ValueError("故意出错")

    engine = RiskEngine(log_decisions=False)
    engine.register(BrokenRule())

    import asyncio
    features = RiskFeatures(order_amount=100, hour_of_day=10)
    result = asyncio.run(engine.evaluate(features))

    assert result.score == 0
    assert result.risk_level == "low"
    broken_detail = [d for d in result.details if d.rule_name == "broken_rule"][0]
    assert broken_detail.triggered is False
    assert "规则执行异常" in broken_detail.reason


def test_cache_endpoint():
    resp = client.get("/risk/cache/info")
    assert resp.status_code == 200


def test_reload_config():
    resp = client.post("/stats/reload-config")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_api_key_auth():
    import os
    original = os.environ.get("RISK_API_KEY", "")
    os.environ["RISK_API_KEY"] = "test-secret-key"

    from app.middleware.auth import API_KEY
    import app.middleware.auth as auth_mod
    auth_mod.API_KEY = "test-secret-key"

    resp = client.post("/risk/predict", json={
        "order_amount": 200,
        "hour_of_day": 14,
    })
    assert resp.status_code == 401

    resp = client.post("/risk/predict", json={
        "order_amount": 200,
        "hour_of_day": 14,
    }, headers={"X-API-Key": "test-secret-key"})
    assert resp.status_code == 200

    os.environ["RISK_API_KEY"] = original
    auth_mod.API_KEY = original
