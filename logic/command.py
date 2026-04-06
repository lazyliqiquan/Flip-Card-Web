from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
from logic.init_db import get_db_connection, close_db_connection

router = APIRouter(
    prefix="/command",  # 路由前缀
    tags=["command"],  # 标签，用于 API 文档分组
)

