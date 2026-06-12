from fastapi import APIRouter, Request
from app.models import RiskFeatures, RiskResult
from app.services.engine import RiskEngine
from app.services.stats import stats_collector
from app.services.cache import RiskCache
from app.middleware.rate_limit import limiter

router = APIRouter(prefix="/risk", tags=["风控"])

_cache = RiskCache.from_config()
engine = RiskEngine.with_default_rules(stats_collector=stats_collector, cache=_cache)


@router.post("/predict", response_model=RiskResult, summary="风险评估")
@limiter.limit("100/minute")
async def predict(request: Request, features: RiskFeatures) -> RiskResult:
    """接收订单特征和用户画像，返回风险评分、等级、各规则命中明细。"""
    return await engine.evaluate(features)


@router.get("/cache/info", summary="缓存信息")
def cache_info():
    """返回缓存状态信息。"""
    if engine.cache:
        return engine.cache.info()
    return {"enabled": False}
