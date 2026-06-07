from app.services.rules.base import BaseRule, RuleResult
from app.models import RiskFeatures


class NewUserLargeOrderRule(BaseRule):
    name = "new_user_large_order"
    description = "新用户大额首单检测（疑似盗刷/薅羊毛）"

    def evaluate(self, f: RiskFeatures) -> RuleResult:
        if not f.is_new_user:
            return RuleResult(self.name, False, 0, None)

        score = 0
        reasons: list[str] = []

        if f.order_amount > 2000:
            score += 30
            reasons.append(f"新用户大额订单（{f.order_amount}元），高度可疑")
        elif f.order_amount > 1000:
            score += 20
            reasons.append(f"新用户较大额订单（{f.order_amount}元）")
        elif f.order_amount > 500:
            score += 10
            reasons.append(f"新用户中等金额订单（{f.order_amount}元）")

        if f.days_since_registration is not None and f.days_since_registration < 1:
            score += 10
            reasons.append("注册不到1天即下单")

        if reasons:
            return RuleResult(self.name, True, min(score, 40), "；".join(reasons))
        return RuleResult(self.name, False, 0, None)
