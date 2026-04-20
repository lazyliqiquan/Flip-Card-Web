import paho.mqtt.client as mqtt
import time
from typing import Callable
from logic.config import MQTT


# MQTT 客户端封装类
class MQTTClient:
    def __init__(self,
                 host: str,  # MQTT 服务器地址
                 port: int = 1883,  # MQTT 端口（默认1883，8883为SSL端口）
                 username: str = "",  # 用户名
                 password: str = "",  # 密码
                 client_id: str = None  # 客户端ID（默认随机生成）
                 ):

        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client_id = client_id
        self.connected = False  # 连接状态标记
        self.receive_callback = None  # 接收消息的回调函数

        # 创建MQTT客户端实例
        self.client = mqtt.Client(client_id=self.client_id)
        # 设置账号密码
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)

        # 绑定MQTT内置回调函数
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, rc):
        """
        【内部函数】连接结果回调
        rc=0: 连接成功
        """
        if rc == 0:
            self.connected = True
            print(f"✅ MQTT 连接成功 | 服务器: {self.host}:{self.port}")
        else:
            self.connected = False
            print(f"❌ MQTT 连接失败，错误码: {rc}")

    def _on_message(self, client, userdata, msg):
        """
        【内部函数】收到消息时自动触发
        """
        topic = msg.topic
        payload = msg.payload.decode("utf-8", errors="ignore")  # 解码消息
        print(f"📥 收到消息 | 主题: {topic} | 内容: {payload}")

        # 如果外部设置了接收回调，自动调用
        if self.receive_callback is not None:
            self.receive_callback(topic, payload)

    def set_receive_callback(self, callback: Callable[[str, str], None]):
        """
        设置接收消息的回调函数（外部调用）
        :param callback: 自定义处理函数，参数为(topic, payload)
        """
        self.receive_callback = callback

    def connect(self, keepalive: int = 60):
        """
        连接MQTT服务器
        :param keepalive: 心跳时间，默认60秒
        """
        try:
            self.client.connect(self.host, self.port, keepalive)
            # 启动后台线程处理MQTT消息（非阻塞）
            self.client.loop_start()
            # 等待连接成功
            time.sleep(0.5)
        except Exception as e:
            print(f"⚠️ 连接服务器失败: {str(e)}")

    def disconnect(self):
        """断开MQTT连接"""
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False
        print("🔌 已断开MQTT连接")

    def publish(self, topic: str, payload: str, qos: int = 0):
        """
        发送消息（外部调用核心函数）
        :param topic: 发布主题
        :param payload: 消息内容（字符串）
        :param qos: 服务质量，0/1/2
        """
        if not self.connected:
            print("⚠️ 未连接MQTT服务器，无法发送消息")
            return False

        result = self.client.publish(topic, payload, qos=qos)
        # 检查是否发送成功
        status = result[0]
        if status == 0:
            print(f"📤 发送成功 | 主题: {topic} | 内容: {payload}")
            return True
        else:
            print(f"⚠️ 发送失败 | 主题: {topic}")
            return False

    def subscribe(self, topic: str, qos: int = 0):
        """
        订阅主题（外部调用核心函数）
        :param qos: 服务质量，0/1/2
        :param topic: 订阅的主题
        """
        if not self.connected:
            print("⚠️ 未连接MQTT服务器，无法订阅主题")
            return

        self.client.subscribe(topic, qos=qos)
        print(f"🔔 已订阅主题: {topic}")


# 初始化MQTT客户端配置
mqtt = MQTTClient(
    host=MQTT.SERVER_IP,
    port=MQTT.PORT,
    username=MQTT.USER,
    password=MQTT.PASSWORD
)

# 在Linux上测试订阅主题的命令
# mosquitto_sub -h localhost -p 1883 -t "esp32/clock" -u "lazyman" -P "lazyman" -v
