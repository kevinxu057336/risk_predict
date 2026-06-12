import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.routers import risk, stats
from app.services.metrics import metrics_response
from app.services.stats import stats_collector
from app.services.engine import LOG_DIR, LOG_FILE
from app.middleware.auth import ApiKeyMiddleware
from app.middleware.rate_limit import limiter
from app.services.tracing import setup_tracing

logger = logging.getLogger("risk_api")
STATS_SNAPSHOT_FILE = LOG_DIR / "stats_snapshot.json"


def _save_stats_snapshot():
    try:
        LOG_DIR.mkdir(exist_ok=True)
        import json
        data = stats_collector.summary()
        with open(STATS_SNAPSHOT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        logger.info("统计快照已保存至 %s", STATS_SNAPSHOT_FILE)
    except Exception as e:
        logger.warning("保存统计快照失败: %s", e)


def _load_stats_snapshot():
    try:
        if STATS_SNAPSHOT_FILE.exists():
            logger.info("发现统计快照 %s，但当前版本仅记录日志，不自动恢复", STATS_SNAPSHOT_FILE)
    except Exception as e:
        logger.warning("加载统计快照失败: %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("风控 API 启动中...")
    _load_stats_snapshot()
    yield
    logger.info("风控 API 关闭中，保存统计快照...")
    _save_stats_snapshot()
    logger.info("风控 API 已关闭")


app = FastAPI(
    title="电商风控 API",
    description="基于可插拔规则引擎的风险评分微服务，适用于酒类及时零售场景。",
    version="0.3.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_middleware(ApiKeyMiddleware)

app.include_router(risk.router)
app.include_router(stats.router)

setup_tracing(app)


@app.get("/health", tags=["健康检查"])
def health():
    return {"status": "ok"}


@app.get("/metrics", tags=["监控"])
def metrics():
    """Prometheus 指标端点：请求量、延迟、分数分布、规则命中率。"""
    return metrics_response()


@app.exception_handler(429)
async def rate_limit_handler(request: Request, exc):
    return JSONResponse(status_code=429, content={"detail": "请求过于频繁，请稍后再试"})
