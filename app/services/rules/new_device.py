from app.services.rules.base import BaseRule, RuleResult
from app.models import RiskFeatures
from app.services.config import get_rule_config


class NewDeviceRule(BaseRule):
    name = "new_device"
    description = "新设备登录检测"

    def evaluate(self, f: RiskFeatures) -> RuleResult:
        cfg = get_rule_config(self.name)
        score = cfg.get("score", 10)
        large_amount_threshold = cfg.get("large_amount_threshold", 1000)

        if f.is_new_device:
            extra = ""
            if f.order_amount > large_amount_threshold:
                extra = "，且首单金额较大，疑似盗刷测试"
            return RuleResult(self.name, True, score, f"新设备登录{extra}")
        return RuleResult(self.name, False, 0, None)
