from app.services.rules.base import BaseRule, RuleResult
from app.models import RiskFeatures


class SameIpDiffPhoneRule(BaseRule):
    name = "same_ip_diff_phone"
    description = "同IP多手机号检测（疑似薅羊毛/刷券）"

    def evaluate(self, f: RiskFeatures) -> RuleResult:
        if f.same_ip_phone_count > 5:
            return RuleResult(self.name, True, 30, f"同IP近24h关联{f.same_ip_phone_count}个不同手机号，疑似批量刷券")
        if f.same_ip_phone_count > 3:
            return RuleResult(self.name, True, 15, f"同IP近24h关联{f.same_ip_phone_count}个不同手机号")
        return RuleResult(self.name, False, 0, None)
