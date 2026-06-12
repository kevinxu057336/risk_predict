from app.services.rules.base import BaseRule, RuleResult
from app.models import RiskFeatures
from app.services.config import get_rule_config


class NewUserLargeOrderRule(BaseRule):
    name = "new_user_large_order"
    description = "新用户大额首单检测（疑似盗刷/薅羊毛）"

    def evaluate(self, f: RiskFeatures) -> RuleResult:
        if not f.is_new_user:
            return RuleResult(self.name, False, 0, None)

        cfg = get_rule_config(self.name)
        amount_high = cfg.get("amount_high", 2000)
        amount_medium = cfg.get("amount_medium", 1000)
        amount_low = cfg.get("amount_low", 500)
        score_high = cfg.get("score_high", 30)
        score_medium = cfg.get("score_medium", 20)
        score_low = cfg.get("score_low", 10)
        new_day_threshold = cfg.get("new_day_threshold", 1)
        new_day_score = cfg.get("new_day_score", 10)
        max_score = cfg.get("max_score", 40)

        score = 0
        reasons: list[str] = []

        if f.order_amount > amount_high:
            score += score_high
            reasons.append(f"新用户大额订单（{f.order_amount}元），高度可疑")
        elif f.order_amount > amount_medium:
            score += score_medium
            reasons.append(f"新用户较大额订单（{f.order_amount}元）")
        elif f.order_amount > amount_low:
            score += score_low
            reasons.append(f"新用户中等金额订单（{f.order_amount}元）")

        if f.days_since_registration is not None and f.days_since_registration < new_day_threshold:
            score += new_day_score
            reasons.append("注册不到1天即下单")

        if reasons:
            return RuleResult(self.name, True, min(score, max_score), "；".join(reasons))
        return RuleResult(self.name, False, 0, None)
