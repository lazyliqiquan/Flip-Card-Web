from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from logic.mqtt import mqtt
from logic.config import MQTT
import asyncio
from threading import Lock

# ==================== 全局安全存储：每个请求独立结果 ====================
result_map = {}  # key: request_id, value: 设备返回的数据
lock = Lock()  # 一把锁保护整个字典，线程安全

# 路由器
router = APIRouter(
    prefix="/device",  # 路由前缀
    tags=["device"],  # 标签，用于 API 文档分组
)


# ==================== MQTT 接收回调（多设备安全） ====================
def handle_receive_msg(topic, payload):
    try:
        # topic = "device/esp32_001/state"
        parts = topic.split("/")  # 切成列表: ["device", "esp32_001", "state"]
        device_id = parts[1]  # 直接拿到设备编号！
        # 把设备返回的结果 存入对应 device_id
        with lock:
            result_map[device_id] = payload

        print(f"✅ 设备返回 | device_id={device_id} | data={payload}")

    except Exception as e:
        print("❌ MQTT 解析错误:", e)


# 先设置，在连接，确保回调函数生效！
mqtt.set_receive_callback(handle_receive_msg)
mqtt.connect()
mqtt.subscribe(MQTT.SUB_TOPIC)


# ==================== 设备控制模型 ====================
class DeviceRequest(BaseModel):
    """设备请求模型"""
    device_id: str  # 设备编号，例如 liqiquan
    cmd: str = ""  # 指令，例如 0 表示时间模式；1 表示日期模式 2 表示显示文本模式 3 表示计算模式 4 表示查询设备状态


# ==================== 设备控制路由 ====================
@router.post("/control")
async def control(device_data: DeviceRequest):
    """设备控制"""
    # 先占位（表示正在等待）
    with lock:
        result_map[device_data.device_id] = None

    # 发送指令
    mqtt.publish(f"{MQTT.PUB_TOPIC}/{device_data.device_id}", device_data.cmd)

    # ==================== 核心：安全等待 5 秒，不会断开 ====================
    timeout = MQTT.WAIT_TIMEOUT  # 总等待时间
    interval = 0.5  # 每0.5秒检查一次
    max_cycles = int(timeout / interval)

    for _ in range(max_cycles):
        # 检查是否收到结果
        with lock:
            res = result_map.get(device_data.device_id)
            if res is not None:
                del result_map[device_data.device_id]
                return {"code": 0, "msg": res}

        # 【关键】每0.5秒等待一次，让连接保持活跃，不断开
        await asyncio.sleep(interval)

    # 超时清理占位（删除 result_map 中的 None）
    with lock:
        result_map.pop(device_data.device_id, None)

    return {
        "code": 1,
        "msg": f"设备响应超时（{MQTT.WAIT_TIMEOUT}秒）"
    }
