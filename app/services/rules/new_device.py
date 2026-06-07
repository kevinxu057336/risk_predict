from app.services.rules.base import BaseRule, RuleResult
from app.models import RiskFeatures


class NewDeviceRule(BaseRule):
    name = "new_device"
    description = "新设备登录检测"

    def evaluate(self, f: RiskFeatures) -> RuleResult:
        if f.is_new_device:
            extra = ""
            if f.order_amount > 1000:
                extra = "，且首单金额较大，疑似盗刷测试"
            return RuleResult(self.name, True, 10, f"新设备登录{extra}")
        return RuleResult(self.name, False, 0, None)
