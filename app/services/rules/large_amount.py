from app.services.rules.base import BaseRule, RuleResult
from app.models import RiskFeatures
from app.services.config import get_rule_config


class LargeAmountRule(BaseRule):
    name = "large_amount"
    description = "大额订单检测"

    def evaluate(self, f: RiskFeatures) -> RuleResult:
        cfg = get_rule_config(self.name)
        high_threshold = cfg.get("high_threshold", 5000)
        medium_threshold = cfg.get("medium_threshold", 2000)
        high_score = cfg.get("high_score", 30)
        medium_score = cfg.get("medium_score", 15)
        liquor_extra_score = cfg.get("liquor_extra_score", 5)

        if f.order_amount > high_threshold:
            if f.product_category in ("白酒", "洋酒"):
                return RuleResult(self.name, True, high_score + liquor_extra_score,
                                  f"大额{f.product_category}订单（>{f.order_amount}元），白酒/洋酒额外加权")
            return RuleResult(self.name, True, high_score, f"大额订单（{f.order_amount}元）")
        if f.order_amount > medium_threshold:
            return RuleResult(self.name, True, medium_score, f"中等金额订单（{f.order_amount}元）")
        return RuleResult(self.name, False, 0, None)
