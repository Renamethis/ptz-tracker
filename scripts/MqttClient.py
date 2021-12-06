from paho.mqtt import client as mqtt_client
import random
from json import loads
import cv2
import numpy as np
broker = 'broker.emqx.io'
port = 1883
topic = "/python/mqtt"
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = 'emqx'
password = 'public'
new_boxes = None
old_boxes = None


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        global old_boxes
        global new_boxes
        old_boxes = new_boxes
        new_boxes = loads(msg.payload.decode())
    client.subscribe(topic)
    client.on_message = on_message


client = connect_mqtt()
subscribe(client)
stream = cv2.VideoCapture(
    'rtsp://admin:Supervisor@172.18.191.12:554/stream/sub', cv2.CAP_FFMPEG)
while stream.isOpened():
    ret, frame = stream.read()
    cv2.resize(frame, (720, 640))
    if(new_boxes is not None and np.array_equal(new_boxes, old_boxes)):
        for box in new_boxes:
            cv2.rectangle(frame, box, (255, 0, 0), 2)
    if cv2.waitKey(0) & 0xFF == ord('q'):
        break
    cv2.imshow('Preview', frame)
cv2.destroyAllWindows()
