from app.services.rules.base import BaseRule, RuleResult
from app.models import RiskFeatures
from app.services.config import get_rule_config


class BatchRegistrationRule(BaseRule):
    name = "batch_registration"
    description = "批量注册检测"

    def evaluate(self, f: RiskFeatures) -> RuleResult:
        cfg = get_rule_config(self.name)
        high_threshold = cfg.get("high_threshold", 20)
        medium_threshold = cfg.get("medium_threshold", 10)
        low_threshold = cfg.get("low_threshold", 5)
        high_score = cfg.get("high_score", 30)
        medium_score = cfg.get("medium_score", 20)
        low_score = cfg.get("low_score", 10)

        if f.recent_batch_reg_count > high_threshold:
            return RuleResult(self.name, True, high_score,
                              f"近1h同网段新注册{f.recent_batch_reg_count}个账号，疑似批量注册攻击")
        if f.recent_batch_reg_count > medium_threshold:
            return RuleResult(self.name, True, medium_score,
                              f"近1h同网段新注册{f.recent_batch_reg_count}个账号")
        if f.recent_batch_reg_count > low_threshold:
            return RuleResult(self.name, True, low_score,
                              f"近1h同网段新注册{f.recent_batch_reg_count}个账号，需关注")
        return RuleResult(self.name, False, 0, None)
