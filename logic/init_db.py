import sqlite3
import os
from logic.config import DB


# 创建数据库文件并新建user数据表
def create_database():
    # 检查数据库文件是否已存在
    if os.path.exists(DB.DB_NAME):
        print(f"数据库文件 {DB.DB_NAME} 已存在，使用原本的数据库")
        return
    else:
        print(f"正在创建数据库文件 {DB.DB_NAME}...")

    # 连接到数据库（如果不存在则创建）
    conn = sqlite3.connect(DB.DB_NAME)
    cursor = conn.cursor()

    # 创建 users 表
    print("创建 users 表...")
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {DB.USERS_TABLE} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        login_time TEXT NOT NULL,
        root BOOLEAN DEFAULT FALSE
    )
    ''')

    # 提交事务
    conn.commit()

    # 验证表是否创建成功
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("\n创建的表：")
    for table in tables:
        print(f"- {table[0]}")

    # 关闭连接
    conn.close()
    print(f"\n数据库 {DB.DB_NAME} 创建完成！")


# 获取数据库连接
def get_db_connection():
    conn = sqlite3.connect(DB.DB_NAME)
    # 设置返回字典形式的结果
    conn.row_factory = sqlite3.Row
    return conn


# 关闭数据库连接
def close_db_connection(conn):
    if conn:
        conn.close()


# 如果没有创建数据库文件，创建数据库文件，并且新建user数据表
create_database()
