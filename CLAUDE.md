# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

风控 Demo API —— 基于可插拔规则引擎的微型风控服务，FastAPI + Pydantic，面向酒类及时零售场景。

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

## 架构

```
app/
├── main.py                          # FastAPI 应用入口，注册路由
├── models.py                        # Pydantic 请求/响应模型（RiskFeatures / RiskResult / RuleDetail）
├── routers/risk.py                  # /risk/predict 路由，组装引擎
└── services/
    ├── engine.py                    # RiskEngine：规则注册 + 编排执行 + 决策日志
    └── rules/
        ├── base.py                  # BaseRule 抽象基类 + RuleResult 数据类
        ├── large_amount.py          # 大额订单（白酒/洋酒额外加权）
        ├── high_frequency.py        # 高频下单（1h + 24h 双窗口）
        ├── late_night.py            # 深夜下单（2:00-5:00，品类关联）
        ├── new_device.py            # 新设备登录
        ├── same_ip_diff_phone.py    # 同IP多手机号（薅羊毛）
        ├── same_device_diff_account.py  # 同设备多账号
        ├── new_user_large_order.py  # 新用户大额首单（盗刷/薅券）
        ├── batch_registration.py    # 批量注册检测
        └── high_return_rate.py      # 高退货/拒收率
```

- **路由层** (`routers/`) 只做参数转发，不写业务逻辑
- **引擎层** (`engine.py`) 负责规则注册、编排执行、决策日志落盘
- **规则层** (`rules/`) 每条规则独立一个文件，继承 `BaseRule`，实现 `evaluate()` 方法
- **模型层** (`models.py`) 定义 Pydantic 模型，Field 的 description 即 Swagger 文档来源
- **决策日志** 写入 `logs/decisions.jsonl`，每行一条 JSON，含时间戳、入参、结果、规则明细

## 如何新增一条规则

1. 在 `app/services/rules/` 下新建文件，继承 `BaseRule`
2. 设置 `name`、`description`，实现 `evaluate(features) -> RuleResult`
3. 在 `engine.py` 的 `with_default_rules()` 中 `register(NewRule())`
4. 写对应的测试用例

## 风控规则速览（9条）

| 规则 | 触发条件 | 最高分值 | 行业相关性 |
|------|----------|----------|-----------|
| 大额订单 | >5000（+35白酒洋酒）/ >2000（+15） | 35 | 酒水客单价高，茅台/五粮液是欺诈高发品类 |
| 高频下单 | 1h>5（+25）/ 24h>20（+20） | 45 | 即时零售30分钟交付，刷单窗口短 |
| 深夜下单 | 2:00-5:00（+20），白酒额外备注 | 20 | 酒水夜间订单占比高，高度酒风险更大 |
| 新设备 | is_new_device（+10），大额加备注 | 10 | 盗刷常用新设备 |
| 同IP多手机号 | >5（+30）/ >3（+15） | 30 | 薅新客券，酒水券面额大（30-50元） |
| 同设备多账号 | >3（+25）/ >1（+10） | 25 | 薅羊毛/套利 |
| 新用户大额首单 | >2000（+30）/ >1000（+20）/ >500（+10），注册<1天（+10） | 40 | 盗刷测试经典路径 |
| 批量注册 | >20（+30）/ >10（+20）/ >5（+10） | 30 | 批量领券后变现 |
| 高退货/拒收 | 退货率>30%（+20）/>15%（+10），COD拒收>30%（+20）/>15%（+10） | 40 | 即时零售COD占比高，骑手代收风险 |

风险等级：`score >= 60` → high，`>= 30` → medium，其余 low。
