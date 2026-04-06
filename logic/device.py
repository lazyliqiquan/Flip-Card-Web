from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
from logic.init_db import get_db_connection, close_db_connection

router = APIRouter(
    prefix="/user",  # 路由前缀
    tags=["user"],  # 标签，用于 API 文档分组
)


class UserRequest(BaseModel):
    """登录请求模型"""
    username: str
    password: str


@router.post("/login")
def login(login_data: UserRequest):
    """用户登录"""
    conn = None
    try:
        # 获取数据库连接
        conn = get_db_connection()
        cursor = conn.cursor()

        # 直接在 SQL 查询中验证用户名和密码
        cursor.execute(
            "SELECT root, id FROM users WHERE username = ? AND password = ?",
            (login_data.username, login_data.password))
        user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )

        # 获取用户信息
        is_root = user["root"]
        user_id = user["id"]

        # 生成格式化的登录时间字符串
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 更新登录时间
        cursor.execute("UPDATE users SET login_time = ? WHERE id = ?", (current_time, user_id))
        conn.commit()

        # 返回登录成功信息
        return {
            "message": "登录成功",
            "is_root": bool(is_root)
        }

    except HTTPException:
        # 重新抛出 HTTP 异常
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        )
    finally:
        # 关闭数据库连接
        close_db_connection(conn)


@router.post("/create")
def create_user(user_data: UserRequest):
    """创建用户"""
    conn = None
    try:
        # 获取数据库连接
        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查用户名是否已存在
        cursor.execute("SELECT id FROM users WHERE username = ?", (user_data.username,))
        existing_user = cursor.fetchone()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )

        # 插入新用户
        cursor.execute(
            "INSERT INTO users (username, password, root) VALUES (?, ?, ?)",
            (user_data.username, user_data.password, 0)
        )
        conn.commit()

        # 返回创建成功信息
        return {
            "message": "用户创建成功",
        }

    except HTTPException:
        # 重新抛出 HTTP 异常
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建用户失败: {str(e)}"
        )
    finally:
        # 关闭数据库连接
        close_db_connection(conn)