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
            'code': 0,
            "isRoot": bool(is_root)
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
            "INSERT INTO users (username, password, login_time, root) VALUES (?, ?, ?, ?)",
            (user_data.username, user_data.password, '', 0)
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


@router.get("/info/{username}")
def get_user_info(username: str):
    """获取指定用户的全部信息"""
    conn = None
    try:
        # 获取数据库连接
        conn = get_db_connection()
        cursor = conn.cursor()
        print(1)
        # 查询用户信息
        cursor.execute(
            "SELECT id, username, password, login_time FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        print(2)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        # 构建返回结果
        user_info = {
            "username": user["username"],
            "password": user["password"],
            "login_time": user["login_time"]
        }

        # 返回用户信息
        return {
            "message": "获取用户信息成功",
            "user_info": user_info
        }

    except HTTPException:
        # 重新抛出 HTTP 异常
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户信息失败: {str(e)}"
        )
    finally:
        # 关闭数据库连接
        close_db_connection(conn)


@router.get("/delete/{username}")
def delete_user(username: str):
    """删除指定用户"""
    conn = None
    try:
        # 获取数据库连接
        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查用户是否存在
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        # 删除用户
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()

        # 返回删除成功信息
        return {"message": "用户删除成功"}

    except HTTPException:
        # 重新抛出 HTTP 异常
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除用户失败: {str(e)}"
        )
    finally:
        # 关闭数据库连接
        close_db_connection(conn)


@router.get("/all")
def get_all_users():
    """获取所有用户的名称和登录时间"""
    conn = None
    try:
        # 获取数据库连接
        conn = get_db_connection()
        cursor = conn.cursor()

        # 查询所有用户的名称和登录时间
        cursor.execute("SELECT username, login_time FROM users")
        users = cursor.fetchall()

        # 构建返回结果
        user_list = []
        for user in users:
            user_list.append({
                "username": user["username"],
                "login_time": user["login_time"]
            })

        # 返回用户列表
        return {
            "message": "获取用户列表成功",
            "users": user_list
        }

    except HTTPException:
        # 重新抛出 HTTP 异常
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户列表失败: {str(e)}"
        )
    finally:
        # 关闭数据库连接
        close_db_connection(conn)
