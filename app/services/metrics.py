from prometheus_client import Counter, Histogram, generate_latest
from fastapi import Response

risk_score_hist = Histogram(
    "risk_score", "风险分数分布", buckets=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
)
risk_rule_triggers = Counter(
    "risk_rule_triggers_total", "规则命中次数", ["rule_name"]
)
risk_level_counter = Counter(
    "risk_level_total", "风险等级分布", ["level"]
)
risk_order_amount_hist = Histogram(
    "risk_order_amount", "订单金额分布",
    buckets=[200, 500, 1000, 2000, 5000, 10000]
)
risk_prediction_duration = Histogram(
    "risk_prediction_duration_seconds", "风控决策耗时"
)
risk_prediction_total = Counter(
    "risk_prediction_total", "风控请求总量"
)


def record_metrics(features, result, duration: float):
    risk_score_hist.observe(result.score)
    risk_level_counter.labels(level=result.risk_level).inc()
    risk_order_amount_hist.observe(features.order_amount)
    risk_prediction_duration.observe(duration)
    risk_prediction_total.inc()
    for d in result.details:
        if d.triggered:
            risk_rule_triggers.labels(rule_name=d.rule_name).inc()


def metrics_response() -> Response:
    return Response(content=generate_latest(), media_type="text/plain")
