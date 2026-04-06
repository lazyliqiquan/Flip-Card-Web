'''
MQTT服务器用户名密码
username: lazyman
password: lazyman
'''

import paho.mqtt.client as mqtt

# ====================== 改成你自己的信息 ======================
MQTT_SERVER = "112.124.52.31"
MQTT_PORT = 1883
MQTT_USER = "lazyman"  # 有就填
MQTT_PASS = "lazyman"  # 有就填
MQTT_TOPIC = "esp32/clock"
# ==============================================================

def on_publish(client, userdata, mid):
    print("✅ MQTT 服务器已确认收到消息！mid =", mid)

client = mqtt.Client()
client.on_publish = on_publish  # 加上这句

if MQTT_USER:
    client.username_pw_set(MQTT_USER, MQTT_PASS)

client.connect(MQTT_SERVER, MQTT_PORT, 60)
client.publish(MQTT_TOPIC, "NEXT")

client.loop()  # 必须加，否则回调来不及跑
client.disconnect()
# mosquitto_sub -h localhost -p 1883 -t "esp32/clock" -u "lazyman" -P "lazyman" -v
