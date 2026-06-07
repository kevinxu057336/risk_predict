from __future__ import annotations

import json
import time
from pathlib import Path

from app.models import RiskFeatures, RiskResult, RuleDetail
from app.services.rules.base import BaseRule
from app.services.rules.large_amount import LargeAmountRule
from app.services.rules.high_frequency import HighFrequencyRule
from app.services.rules.late_night import LateNightRule
from app.services.rules.new_device import NewDeviceRule
from app.services.rules.same_ip_diff_phone import SameIpDiffPhoneRule
from app.services.rules.same_device_diff_account import SameDeviceDiffAccountRule
from app.services.rules.new_user_large_order import NewUserLargeOrderRule
from app.services.rules.batch_registration import BatchRegistrationRule
from app.services.rules.high_return_rate import HighReturnRateRule

LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_FILE = LOG_DIR / "decisions.jsonl"


class RiskEngine:
    """规则引擎：注册规则 → 逐条执行 → 汇总打分"""

    def __init__(self, log_decisions: bool = True):
        self.rules: list[BaseRule] = []
        self.log_decisions = log_decisions

    def register(self, rule: BaseRule) -> None:
        self.rules.append(rule)

    def evaluate(self, features: RiskFeatures) -> RiskResult:
        total = 0
        details: list[RuleDetail] = []
        reasons: list[str] = []

        for rule in self.rules:
            result = rule.evaluate(features)
            total += result.score
            details.append(RuleDetail(
                rule_name=result.rule_name,
                triggered=result.triggered,
                score=result.score,
                reason=result.reason,
            ))
            if result.reason:
                reasons.append(result.reason)

        total = min(total, 100)

        if total >= 60:
            level = "high"
        elif total >= 30:
            level = "medium"
        else:
            level = "low"

        risk_result = RiskResult(score=total, risk_level=level, details=details, reasons=reasons)

        if self.log_decisions:
            self._write_log(features, risk_result)

        return risk_result

    def _write_log(self, features: RiskFeatures, result: RiskResult) -> None:
        LOG_DIR.mkdir(exist_ok=True)
        entry = {
            "timestamp": int(time.time() * 1000),
            "features": features.model_dump(),
            "result": result.model_dump(),
        }
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    @classmethod
    def with_default_rules(cls) -> RiskEngine:
        """创建预装全部规则的引擎"""
        engine = cls()
        engine.register(LargeAmountRule())
        engine.register(HighFrequencyRule())
        engine.register(LateNightRule())
        engine.register(NewDeviceRule())
        engine.register(SameIpDiffPhoneRule())
        engine.register(SameDeviceDiffAccountRule())
        engine.register(NewUserLargeOrderRule())
        engine.register(BatchRegistrationRule())
        engine.register(HighReturnRateRule())
        return engine
