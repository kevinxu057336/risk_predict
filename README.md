# 风控 Demo API

基于**可插拔规则引擎**的风险评分微服务，面向酒类及时零售场景。9 条风控规则，覆盖账户风险、交易行为、履约风险。

## 快速开始

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

浏览器打开 http://localhost:8000/docs → Swagger 直接试接口。

## 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| POST | `/risk/predict` | 风险评估（9条规则并行执行） |
| GET | `/docs` | Swagger 文档 |

## curl 示例

```bash
# 健康检查
curl http://localhost:8000/health

# 低风险：普通用户买啤酒
curl -X POST http://localhost:8000/risk/predict \
  -H "Content-Type: application/json" \
  -d '{
    "order_amount":200,"order_count_1h":1,"order_count_24h":3,
    "hour_of_day":14,"product_category":"啤酒",
    "is_new_device":false,"is_new_user":false,
    "same_ip_phone_count":1,"same_device_account_count":1,
    "recent_batch_reg_count":0,"return_rate":0,"cod_reject_rate":0
  }'

# 高风险：新用户深夜买白酒 + 大额 + 新设备 + 同IP多号
curl -X POST http://localhost:8000/risk/predict \
  -H "Content-Type: application/json" \
  -d '{
    "order_amount":6000,"order_count_1h":7,"order_count_24h":25,
    "hour_of_day":3,"product_category":"白酒",
    "ip_address":"10.0.0.1","device_id":"dev-001",
    "is_new_device":true,"is_new_user":true,
    "days_since_registration":0,
    "same_ip_phone_count":6,"same_device_account_count":4,
    "recent_batch_reg_count":25,"return_rate":0.4,"cod_reject_rate":0.35
  }'
```

## 响应示例

```json
{
  "score": 100,
  "risk_level": "high",
  "details": [
    {"rule_name": "large_amount",            "triggered": true, "score": 35, "reason": "大额白酒订单（6000.0元），白酒/洋酒额外加权"},
    {"rule_name": "high_frequency",          "triggered": true, "score": 45, "reason": "1小时内下单7次，频率异常；24小时内下单25次，频率异常"},
    {"rule_name": "late_night",              "triggered": true, "score": 20, "reason": "深夜时段下单（3:00）；深夜+白酒品类，触发额外关注"},
    {"rule_name": "new_device",              "triggered": true, "score": 10, "reason": "新设备登录，且首单金额较大，疑似盗刷测试"},
    {"rule_name": "same_ip_diff_phone",      "triggered": true, "score": 30, "reason": "同IP近24h关联6个不同手机号，疑似批量刷券"},
    {"rule_name": "same_device_diff_account","triggered": true, "score": 25, "reason": "同设备近24h关联4个不同账号"},
    {"rule_name": "new_user_large_order",    "triggered": true, "score": 40, "reason": "新用户大额订单（6000.0元），高度可疑；注册不到1天即下单"},
    {"rule_name": "batch_registration",      "triggered": true, "score": 30, "reason": "近1h同网段新注册25个账号，疑似批量注册攻击"},
    {"rule_name": "high_return_rate",        "triggered": true, "score": 40, "reason": "退货率40%，远超正常水平；COD拒收率35%，高度可疑"}
  ],
  "reasons": ["大额白酒订单...", "高频...", ...]
}
```

## 运行测试

```bash
pytest -v                          # 全部测试
pytest tests/test_risk.py -v       # 单文件
```

## Docker

```bash
docker build -t risk-api .
docker run -p 8000:8000 risk-api
```

## 项目结构

```
app/
├── main.py                       # FastAPI 入口
├── models.py                     # Pydantic 模型
├── routers/risk.py               # 路由层
└── services/
    ├── engine.py                 # 规则引擎（注册 + 编排 + 日志）
    └── rules/                    # 9 条独立规则文件
        ├── base.py
        ├── large_amount.py
        ├── high_frequency.py
        ├── late_night.py
        ├── new_device.py
        ├── same_ip_diff_phone.py
        ├── same_device_diff_account.py
        ├── new_user_large_order.py
        ├── batch_registration.py
        └── high_return_rate.py
tests/
└── test_risk.py
logs/
└── decisions.jsonl              # 决策日志（自动生成）
```
