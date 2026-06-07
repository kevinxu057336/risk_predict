from app.services.rules.base import BaseRule, RuleResult
from app.models import RiskFeatures


class LateNightRule(BaseRule):
    name = "late_night"
    description = "深夜下单检测"

    def evaluate(self, f: RiskFeatures) -> RuleResult:
        if 2 <= f.hour_of_day <= 5:
            extra = ""
            if f.product_category == "白酒":
                extra = "；深夜+白酒品类，触发额外关注"
            return RuleResult(self.name, True, 20, f"深夜时段下单（{f.hour_of_day}:00）{extra}")
        return RuleResult(self.name, False, 0, None)
