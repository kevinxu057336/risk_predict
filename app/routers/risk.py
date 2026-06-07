from fastapi import APIRouter
from app.models import RiskFeatures, RiskResult
from app.services.engine import RiskEngine

router = APIRouter(prefix="/risk", tags=["风控"])

engine = RiskEngine.with_default_rules()


@router.post("/predict", response_model=RiskResult, summary="风险评估")
def predict(features: RiskFeatures) -> RiskResult:
    """接收订单特征和用户画像，返回风险评分、等级、各规则命中明细。"""
    return engine.evaluate(features)
