from fastapi import FastAPI
from logic.user import router as user_router
from logic.device import router as device_router

app = FastAPI(
    title="Flip Card API",
    version="1.0.0"
)

# 注册路由
app.include_router(user_router)
app.include_router(device_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
