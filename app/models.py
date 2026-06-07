from pydantic import BaseModel, Field


class RiskFeatures(BaseModel):
    """风控请求输入"""

    # 订单信息
    order_amount: float = Field(..., gt=0, description="订单金额（元）")
    order_count_1h: int = Field(0, ge=0, description="近1小时下单次数")
    order_count_24h: int = Field(0, ge=0, description="近24小时下单次数")
    hour_of_day: int = Field(..., ge=0, le=23, description="当前小时（0-23）")
    product_category: str | None = Field(None, description="商品品类: 白酒/啤酒/葡萄酒/洋酒/其他")

    # 设备/网络指纹
    ip_address: str | None = Field(None, description="客户端IP")
    device_id: str | None = Field(None, description="设备指纹ID")
    is_new_device: bool = Field(False, description="是否新设备登录")

    # 用户画像
    user_id: str | None = Field(None, description="用户ID")
    phone: str | None = Field(None, description="手机号")
    is_new_user: bool = Field(False, description="是否新注册用户")
    days_since_registration: int | None = Field(None, description="注册至今多少天")
    total_orders: int = Field(0, ge=0, description="历史总订单数")
    return_rate: float = Field(0.0, ge=0, le=1, description="历史退货率")
    cod_reject_rate: float = Field(0.0, ge=0, le=1, description="货到付款拒收率")

    # 关联风险（由上游缓存/DB 预计算后传入）
    same_ip_phone_count: int = Field(0, ge=0, description="同IP近24h不同手机号数量")
    same_device_account_count: int = Field(0, ge=0, description="同设备近24h不同账号数量")
    recent_batch_reg_count: int = Field(0, ge=0, description="近1h同网段新注册数量")


class RuleDetail(BaseModel):
    """单条规则的命中结果"""
    rule_name: str = Field(..., description="规则名称")
    triggered: bool = Field(..., description="是否命中")
    score: int = Field(0, description="贡献分值")
    reason: str | None = Field(None, description="命中原因")


class RiskResult(BaseModel):
    """风控响应"""
    score: int = Field(..., ge=0, le=100, description="风险总分 0-100")
    risk_level: str = Field(..., description="风险等级: low / medium / high")
    details: list[RuleDetail] = Field(default_factory=list, description="各规则得分明细")
    reasons: list[str] = Field(default_factory=list, description="命中规则简述（便于前端展示）")
