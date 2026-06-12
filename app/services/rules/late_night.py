from app.services.rules.base import BaseRule, RuleResult
from app.models import RiskFeatures
from app.services.config import get_rule_config


class LateNightRule(BaseRule):
    name = "late_night"
    description = "深夜下单检测"

    def evaluate(self, f: RiskFeatures) -> RuleResult:
        cfg = get_rule_config(self.name)
        start_hour = cfg.get("start_hour", 2)
        end_hour = cfg.get("end_hour", 5)
        score = cfg.get("score", 20)

        if start_hour <= f.hour_of_day <= end_hour:
            extra = ""
            if f.product_category == "白酒":
                extra = "；深夜+白酒品类，触发额外关注"
            return RuleResult(self.name, True, score, f"深夜时段下单（{f.hour_of_day}:00）{extra}")
        return RuleResult(self.name, False, 0, None)
