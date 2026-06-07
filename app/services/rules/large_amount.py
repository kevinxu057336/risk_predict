from app.services.rules.base import BaseRule, RuleResult
from app.models import RiskFeatures


class LargeAmountRule(BaseRule):
    name = "large_amount"
    description = "大额订单检测"

    def evaluate(self, f: RiskFeatures) -> RuleResult:
        if f.order_amount > 5000:
            if f.product_category in ("白酒", "洋酒"):
                return RuleResult(self.name, True, 35, f"大额{ f.product_category }订单（>{f.order_amount}元），白酒/洋酒额外加权")
            return RuleResult(self.name, True, 30, f"大额订单（{f.order_amount}元）")
        if f.order_amount > 2000:
            return RuleResult(self.name, True, 15, f"中等金额订单（{f.order_amount}元）")
        return RuleResult(self.name, False, 0, None)
