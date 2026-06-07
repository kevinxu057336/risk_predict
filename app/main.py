from fastapi import FastAPI
from app.routers import risk

app = FastAPI(
    title="风控 Demo API",
    description="基于可插拔规则引擎的风险评分微服务，适用于酒类及时零售场景。",
    version="0.2.0",
)

app.include_router(risk.router)


@app.get("/health", tags=["健康检查"])
def health():
    return {"status": "ok"}
