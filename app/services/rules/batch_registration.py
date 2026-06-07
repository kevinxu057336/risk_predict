from app.services.rules.base import BaseRule, RuleResult
from app.models import RiskFeatures


class BatchRegistrationRule(BaseRule):
    name = "batch_registration"
    description = "批量注册检测"

    def evaluate(self, f: RiskFeatures) -> RuleResult:
        if f.recent_batch_reg_count > 20:
            return RuleResult(self.name, True, 30, f"近1h同网段新注册{f.recent_batch_reg_count}个账号，疑似批量注册攻击")
        if f.recent_batch_reg_count > 10:
            return RuleResult(self.name, True, 20, f"近1h同网段新注册{f.recent_batch_reg_count}个账号")
        if f.recent_batch_reg_count > 5:
            return RuleResult(self.name, True, 10, f"近1h同网段新注册{f.recent_batch_reg_count}个账号，需关注")
        return RuleResult(self.name, False, 0, None)
