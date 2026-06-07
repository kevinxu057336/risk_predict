from fastapi import APIRouter
from app.services.stats import stats_collector

router = APIRouter(prefix="/stats", tags=["指标统计"])


@router.get("", summary="风险指标聚合统计")
def get_stats():
    """返回内存中聚合的风险指标：规则命中率、分数/金额分布、时间窗口趋势。"""
    return stats_collector.summary()
