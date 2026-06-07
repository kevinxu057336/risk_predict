from fastapi import FastAPI
from app.routers import risk, stats
from app.services.metrics import metrics_response

app = FastAPI(
    title="风控 Demo API",
    description="基于可插拔规则引擎的风险评分微服务，适用于酒类及时零售场景。",
    version="0.2.1",
)

app.include_router(risk.router)
app.include_router(stats.router)


@app.get("/health", tags=["健康检查"])
def health():
    return {"status": "ok"}


@app.get("/metrics", tags=["监控"])
def metrics():
    """Prometheus 指标端点：请求量、延迟、分数分布、规则命中率。"""
    return metrics_response()
