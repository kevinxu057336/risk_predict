from abc import ABC, abstractmethod
from dataclasses import dataclass
from app.models import RiskFeatures


@dataclass
class RuleResult:
    rule_name: str
    triggered: bool
    score: int
    reason: str | None


class BaseRule(ABC):
    """风控规则基类，所有规则继承此类"""

    name: str = ""
    description: str = ""

    @abstractmethod
    def evaluate(self, features: RiskFeatures) -> RuleResult:
        """评估风险，返回规则命中结果"""
        ...
