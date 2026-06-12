from app.services.rules.base import BaseRule, RuleResult
from app.models import RiskFeatures
from app.services.config import get_rule_config


class SameDeviceDiffAccountRule(BaseRule):
    name = "same_device_diff_account"
    description = "同设备多账号检测"

    def evaluate(self, f: RiskFeatures) -> RuleResult:
        cfg = get_rule_config(self.name)
        high_threshold = cfg.get("high_threshold", 3)
        medium_threshold = cfg.get("medium_threshold", 1)
        high_score = cfg.get("high_score", 25)
        medium_score = cfg.get("medium_score", 10)

        if f.same_device_account_count > high_threshold:
            return RuleResult(self.name, True, high_score,
                              f"同设备近24h关联{f.same_device_account_count}个不同账号")
        if f.same_device_account_count > medium_threshold:
            return RuleResult(self.name, True, medium_score,
                              f"同设备近24h关联{f.same_device_account_count}个不同账号")
        return RuleResult(self.name, False, 0, None)
