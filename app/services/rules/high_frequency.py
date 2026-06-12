from app.services.rules.base import BaseRule, RuleResult
from app.models import RiskFeatures
from app.services.config import get_rule_config


class HighFrequencyRule(BaseRule):
    name = "high_frequency"
    description = "高频下单检测"

    def evaluate(self, f: RiskFeatures) -> RuleResult:
        cfg = get_rule_config(self.name)
        count_1h_high = cfg.get("count_1h_high", 5)
        count_1h_medium = cfg.get("count_1h_medium", 3)
        count_24h_high = cfg.get("count_24h_high", 20)
        score_1h_high = cfg.get("score_1h_high", 25)
        score_1h_medium = cfg.get("score_1h_medium", 10)
        score_24h_high = cfg.get("score_24h_high", 20)

        score = 0
        reasons: list[str] = []

        if f.order_count_1h > count_1h_high:
            score += score_1h_high
            reasons.append(f"1小时内下单{f.order_count_1h}次，频率异常")
        elif f.order_count_1h > count_1h_medium:
            score += score_1h_medium
            reasons.append(f"1小时内下单{f.order_count_1h}次，频率偏高")

        if f.order_count_24h > count_24h_high:
            score += score_24h_high
            reasons.append(f"24小时内下单{f.order_count_24h}次，频率异常")

        if reasons:
            return RuleResult(self.name, True, score, "；".join(reasons))
        return RuleResult(self.name, False, 0, None)
