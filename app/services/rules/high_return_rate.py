from app.services.rules.base import BaseRule, RuleResult
from app.models import RiskFeatures
from app.services.config import get_rule_config


class HighReturnRateRule(BaseRule):
    name = "high_return_rate"
    description = "高退货/拒收率检测"

    def evaluate(self, f: RiskFeatures) -> RuleResult:
        cfg = get_rule_config(self.name)
        high_threshold = cfg.get("high_threshold", 0.3)
        medium_threshold = cfg.get("medium_threshold", 0.15)
        high_score = cfg.get("high_score", 20)
        medium_score = cfg.get("medium_score", 10)
        max_score = cfg.get("max_score", 40)

        score = 0
        reasons: list[str] = []

        if f.return_rate > high_threshold:
            score += high_score
            reasons.append(f"退货率{f.return_rate:.0%}，远超正常水平")
        elif f.return_rate > medium_threshold:
            score += medium_score
            reasons.append(f"退货率{f.return_rate:.0%}，偏高")

        if f.cod_reject_rate > high_threshold:
            score += high_score
            reasons.append(f"COD拒收率{f.cod_reject_rate:.0%}，高度可疑")
        elif f.cod_reject_rate > medium_threshold:
            score += medium_score
            reasons.append(f"COD拒收率{f.cod_reject_rate:.0%}，偏高")

        if reasons:
            return RuleResult(self.name, True, min(score, max_score), "；".join(reasons))
        return RuleResult(self.name, False, 0, None)
