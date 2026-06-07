# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

风控 Demo API —— 基于可插拔规则引擎的微型风控服务，FastAPI + Pydantic，面向酒类及时零售场景。
内置风险指标收集（内存聚合 + Prometheus）和决策日志。

## 常用命令

```bash
# 开发启动（热重载）
uvicorn app.main:app --reload --port 8000

# 运行全部测试
pytest -v

# 运行单个测试
pytest tests/test_risk.py::test_predict_high_risk -v

# Docker 构建与运行
docker build -t risk-api .
docker run -p 8000:8000 risk-api
```

## 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| POST | `/risk/predict` | 风险评估（9条规则并行） |
| GET | `/stats` | 风险指标聚合统计（JSON） |
| GET | `/metrics` | Prometheus 指标（Counter + Histogram） |
| GET | `/docs` | Swagger 文档 |

## 架构

```
app/
├── main.py                          # FastAPI 入口，注册路由和 /metrics
├── models.py                        # Pydantic 模型（RiskFeatures / RiskResult / RuleDetail）
├── routers/
│   ├── risk.py                      # /risk/predict 路由
│   └── stats.py                     # /stats 路由
└── services/
    ├── engine.py                    # RiskEngine：规则编排 + 日志 + 统计 + Prometheus
    ├── stats.py                     # RiskStatsCollector：内存聚合器（分布/趋势/命中率）
    ├── metrics.py                   # Prometheus 自定义指标
    └── rules/
        ├── base.py                  # BaseRule + RuleResult
        ├── large_amount.py          # 大额订单（白酒/洋酒加权）
        ├── high_frequency.py        # 高频下单
        ├── late_night.py            # 深夜下单（品类关联）
        ├── new_device.py            # 新设备登录
        ├── same_ip_diff_phone.py    # 同IP多手机号
        ├── same_device_diff_account.py  # 同设备多账号
        ├── new_user_large_order.py  # 新用户大额首单
        ├── batch_registration.py    # 批量注册
        └── high_return_rate.py      # 高退货/拒收率
```

**数据流**：请求 → `routers/risk.py` → `engine.evaluate()` → 9条规则并行 → 汇总分数 →
同时写入三路：① 决策日志（`logs/decisions.jsonl`）② 内存统计（`stats_collector`）③ Prometheus metrics

## 风险指标收集

### /stats 端点 — 内存聚合器（`app/services/stats.py`）

`RiskStatsCollector` 单例在每次预测后记录，提供：
- **时间窗口统计**：最近 1h / 24h 的请求量、均分、高风险占比、交易总额
- **规则命中率**：每条规则的触发次数和命中率（用于判断规则有效性）
- **风险等级分布**：low/medium/high 的计数和占比
- **分数分布**：0-9, 10-19, ..., 90-100 各桶计数（用于调阈值）
- **金额分布**：0-200, 200-500, 500-1000, 1000-2000, 2000-5000, 5000+ 各桶计数
- **品类分布**：白酒/啤酒/葡萄酒等出现频次
- **小时分布**：0-23 时各时段请求量（识别风险高峰时段）
- 内存保留最近 24h 记录，线程安全

### /metrics 端点 — Prometheus 指标（`app/services/metrics.py`）

| 指标名 | 类型 | 说明 |
|--------|------|------|
| `risk_score` | Histogram | 风险分数分布（10分一档） |
| `risk_rule_triggers_total` | Counter | 每条规则命中次数（按 rule_name 分 label） |
| `risk_level_total` | Counter | 风险等级计数（按 level 分 label） |
| `risk_order_amount` | Histogram | 订单金额分布 |
| `risk_prediction_duration_seconds` | Histogram | 风控决策耗时 |
| `risk_prediction_total` | Counter | 风控请求总量 |

### 决策日志（`logs/decisions.jsonl`）

每行一条 JSON：时间戳 + 完整入参 + 结果 + 规则明细。用于离线回溯和规则效果分析。

## 如何新增一条规则

1. 在 `app/services/rules/` 下新建文件，继承 `BaseRule`
2. 设置 `name`、`description`，实现 `evaluate(features) -> RuleResult`
3. 在 `engine.py` 的 `with_default_rules()` 中 `register(NewRule())`
4. 写对应测试用例
