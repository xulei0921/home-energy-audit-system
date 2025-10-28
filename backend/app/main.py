from sys import prefix

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn

from .database import engine, Base
from .routers import users, devices, energy_readings, recommendations
import logging

# 创建数据库表
Base.metadata.create_all(bind=engine)

load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log', encoding='utf-8')
    ]
)

app = FastAPI(
    title="家庭能耗体检与节能建议系统",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:6173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(users.router, prefix="/api/users", tags=["用户"])
app.include_router(devices.router, prefix="/api/devices", tags=["设备"])
app.include_router(energy_readings.router, prefix="/api/energy-readings", tags=["能耗读取"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["节能建议"])


@app.get("/")
async def root():
    return {"message": "家庭能耗体检与节能建议系统 API"}
