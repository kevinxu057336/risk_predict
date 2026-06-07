from app.services.rules.base import BaseRule, RuleResult
from app.models import RiskFeatures


class HighFrequencyRule(BaseRule):
    name = "high_frequency"
    description = "高频下单检测"

    def evaluate(self, f: RiskFeatures) -> RuleResult:
        score = 0
        reasons: list[str] = []

        if f.order_count_1h > 5:
            score += 25
            reasons.append(f"1小时内下单{f.order_count_1h}次，频率异常")
        elif f.order_count_1h > 3:
            score += 10
            reasons.append(f"1小时内下单{f.order_count_1h}次，频率偏高")

        if f.order_count_24h > 20:
            score += 20
            reasons.append(f"24小时内下单{f.order_count_24h}次，频率异常")

        if reasons:
            return RuleResult(self.name, True, score, "；".join(reasons))
        return RuleResult(self.name, False, 0, None)
