from app.services.rules.base import BaseRule, RuleResult
from app.models import RiskFeatures


class SameDeviceDiffAccountRule(BaseRule):
    name = "same_device_diff_account"
    description = "同设备多账号检测"

    def evaluate(self, f: RiskFeatures) -> RuleResult:
        if f.same_device_account_count > 3:
            return RuleResult(self.name, True, 25, f"同设备近24h关联{f.same_device_account_count}个不同账号")
        if f.same_device_account_count > 1:
            return RuleResult(self.name, True, 10, f"同设备近24h关联{f.same_device_account_count}个不同账号")
        return RuleResult(self.name, False, 0, None)
