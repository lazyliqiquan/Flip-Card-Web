# 数据库配置
class DB:
    DB_NAME = "flip_card.db"  # 数据库文件名
    USERS_TABLE = "users"  # 用户表名


# MQTT 配置
class MQTT:
    SERVER_IP = "112.124.52.31"  # MQTT 服务器IP
    PORT = 1883  # 1883 是默认端口
    USER = "lazyman"  # MQTT 用户名
    PASSWORD = "lazyman"  # MQTT 密码
    PUB_TOPIC = 'clock/control'  # 后面需要添加设备ID，例如 'clock/control/liqiquan'
    SUB_TOPIC = 'clock/+/status'  # 订阅主题，接受所有设备的状态更新，例如 'clock/liqiquan/status'
    WAIT_TIMEOUT = 5  # 等待esp32设备响应超时时间（秒）
