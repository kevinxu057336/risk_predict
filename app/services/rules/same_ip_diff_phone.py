from app.services.rules.base import BaseRule, RuleResult
from app.models import RiskFeatures
from app.services.config import get_rule_config


class SameIpDiffPhoneRule(BaseRule):
    name = "same_ip_diff_phone"
    description = "同IP多手机号检测（疑似薅羊毛/刷券）"

    def evaluate(self, f: RiskFeatures) -> RuleResult:
        cfg = get_rule_config(self.name)
        high_threshold = cfg.get("high_threshold", 5)
        medium_threshold = cfg.get("medium_threshold", 3)
        high_score = cfg.get("high_score", 30)
        medium_score = cfg.get("medium_score", 15)

        if f.same_ip_phone_count > high_threshold:
            return RuleResult(self.name, True, high_score,
                              f"同IP近24h关联{f.same_ip_phone_count}个不同手机号，疑似批量刷券")
        if f.same_ip_phone_count > medium_threshold:
            return RuleResult(self.name, True, medium_score,
                              f"同IP近24h关联{f.same_ip_phone_count}个不同手机号")
        return RuleResult(self.name, False, 0, None)
