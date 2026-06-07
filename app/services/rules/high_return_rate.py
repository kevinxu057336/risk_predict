from app.services.rules.base import BaseRule, RuleResult
from app.models import RiskFeatures


class HighReturnRateRule(BaseRule):
    name = "high_return_rate"
    description = "高退货/拒收率检测"

    def evaluate(self, f: RiskFeatures) -> RuleResult:
        score = 0
        reasons: list[str] = []

        if f.return_rate > 0.3:
            score += 20
            reasons.append(f"退货率{f.return_rate:.0%}，远超正常水平")
        elif f.return_rate > 0.15:
            score += 10
            reasons.append(f"退货率{f.return_rate:.0%}，偏高")

        if f.cod_reject_rate > 0.3:
            score += 20
            reasons.append(f"COD拒收率{f.cod_reject_rate:.0%}，高度可疑")
        elif f.cod_reject_rate > 0.15:
            score += 10
            reasons.append(f"COD拒收率{f.cod_reject_rate:.0%}，偏高")

        if reasons:
            return RuleResult(self.name, True, min(score, 40), "；".join(reasons))
        return RuleResult(self.name, False, 0, None)
