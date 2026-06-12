from fastapi import APIRouter
from app.services.config import RuleConfig
from app.services.stats import stats_collector

router = APIRouter(prefix="/stats", tags=["指标统计"])


@router.get("", summary="风险指标聚合统计")
def get_stats():
    """返回内存中聚合的风险指标：规则命中率、分数/金额分布、时间窗口趋势。"""
    return stats_collector.summary()


@router.post("/reload-config", summary="热更新配置")
def reload_config():
    """重新加载 YAML 配置文件，无需重启服务。"""
    RuleConfig.get().reload()
    return {"status": "ok", "message": "配置已重新加载"}
