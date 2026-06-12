from fastapi import FastAPI
from logic.user import router as user_router
from logic.device import router as device_router
from fastapi.middleware.cors import CORSMiddleware




app = FastAPI(
    title="Flip Card API",
    version="1.0.0"
)

# 注册路由
app.include_router(user_router)
app.include_router(device_router)

# 配置跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有域名，生产环境改具体前端地址
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有请求方法（包含 OPTIONS）
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
