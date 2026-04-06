DB_NAME = "flip_card.db"

class TableName:
    USERS = "users"

'''
数据库需要具备的数据：
- users 表：存储用户信息，
    - id：用户唯一标识符，主键，自增
    - username：用户名，唯一，不能为空
    - password：用户密码，不能为空
    - login_time：用户登录时间，默认最近一次的登陆时间
    - root：是否为管理员，默认，默认值为 False
'''
