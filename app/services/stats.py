import time
import threading
from collections import defaultdict
from app.models import RiskFeatures, RiskResult

# 分数分桶（10分一档）
SCORE_BUCKETS = [(0, 9), (10, 19), (20, 29), (30, 39), (40, 49),
                 (50, 59), (60, 69), (70, 79), (80, 89), (90, 100)]
# 金额分桶（酒水零售实际区间）
AMOUNT_BUCKETS = [(0, 200), (200, 500), (500, 1000),
                  (1000, 2000), (2000, 5000), (5000, float("inf"))]


def _bucket_label(buckets: list[tuple], value: float) -> str:
    for lo, hi in buckets:
        if lo <= value <= hi:
            return f"{lo}-{hi}" if hi != float("inf") else f"{lo}+"
    return "unknown"


class RiskStatsCollector:
    """内存中的风险指标聚合器，线程安全"""

    def __init__(self):
        self._lock = threading.Lock()
        self._reset()

    def _reset(self):
        self.total = 0
        self.rule_triggers: dict[str, int] = defaultdict(int)
        self.level_counts: dict[str, int] = defaultdict(int)
        self.score_buckets: dict[str, int] = defaultdict(int)
        self.amount_buckets: dict[str, int] = defaultdict(int)
        self.category_counts: dict[str, int] = defaultdict(int)
        self.hour_dist: dict[int, int] = defaultdict(int)
        self._records: list[tuple[float, int, str, int]] = []  # (ts, score, level, amount)

    def record(self, features: RiskFeatures, result: RiskResult):
        """记录一次预测"""
        now = time.time()
        with self._lock:
            self.total += 1
            self.level_counts[result.risk_level] += 1
            self.score_buckets[_bucket_label(SCORE_BUCKETS, result.score)] += 1
            self.amount_buckets[_bucket_label(AMOUNT_BUCKETS, features.order_amount)] += 1
            self.hour_dist[features.hour_of_day] += 1

            if features.product_category:
                self.category_counts[features.product_category] += 1

            for d in result.details:
                if d.triggered:
                    self.rule_triggers[d.rule_name] += 1

            self._records.append((now, result.score, result.risk_level, int(features.order_amount)))
            # 只保留最近24小时的记录，控制内存
            cutoff = now - 86400
            self._records = [r for r in self._records if r[0] > cutoff]

    def summary(self) -> dict:
        """返回聚合统计"""
        with self._lock:
            now = time.time()
            h1_cutoff = now - 3600
            h24_cutoff = now - 86400

            def _window(cutoff_ts: float) -> dict:
                recs = [r for r in self._records if r[0] > cutoff_ts]
                if not recs:
                    return {"count": 0, "avg_score": 0, "high_rate": 0, "total_amount": 0}
                scores = [r[1] for r in recs]
                return {
                    "count": len(recs),
                    "avg_score": round(sum(scores) / len(scores), 1),
                    "high_rate": round(sum(1 for r in recs if r[2] == "high") / len(recs), 3),
                    "total_amount": sum(r[3] for r in recs),
                }

            return {
                "total_predictions": self.total,
                "window": {
                    "last_1h": _window(h1_cutoff),
                    "last_24h": _window(h24_cutoff),
                },
                "rule_trigger_rates": {
                    name: {
                        "count": cnt,
                        "rate": round(cnt / self.total, 4) if self.total else 0,
                    }
                    for name, cnt in sorted(self.rule_triggers.items(),
                                            key=lambda x: x[1], reverse=True)
                },
                "risk_level_distribution": {
                    level: {
                        "count": self.level_counts.get(level, 0),
                        "pct": round(self.level_counts.get(level, 0) / self.total, 3) if self.total else 0,
                    }
                    for level in ["low", "medium", "high"]
                },
                "score_distribution": {
                    b: self.score_buckets.get(b, 0)
                    for b in ["0-9", "10-19", "20-29", "30-39", "40-49",
                              "50-59", "60-69", "70-79", "80-89", "90-100"]
                },
                "amount_distribution": {
                    b: self.amount_buckets.get(b, 0)
                    for b in ["0-200", "200-500", "500-1000",
                              "1000-2000", "2000-5000", "5000+"]
                },
                "product_category_distribution": dict(self.category_counts),
                "hour_distribution": {str(h): self.hour_dist.get(h, 0) for h in range(24)},
            }


# 全局单例
stats_collector = RiskStatsCollector()
