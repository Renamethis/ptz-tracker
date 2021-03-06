### TRACKER ASSISTANT TEST CLIENT
import argparse
from paho.mqtt import client as mqtt_client
import random
import json
import cv2
from threading import Thread
import numpy as np
import sys
import requests
### USAGE
# python3 MqttClient.py --rtsp_url [URL of rtsp-stream]
# [optional] --broker [MQTT Broker] default - brokekr.emqx.io
# [optional] --port [MQTT Port] default - 1883
# [optional] --topic [MQTT Topic] default - /python/mqtt
# [optional] --username [MQTT username] default - emqx
# [optional] --password [MQTT password] default - public
# Get parser arguments
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-u','--rtsp_url', type=str, help='Stream RTSP-url')
parser.add_argument('-b','--broker', type=str, help='MQTT Broker')
parser.add_argument('-p','--port', type=str, help='MQTT Port')
parser.add_argument('-n','--username', type=str, help='MQTT Username')
parser.add_argument('-w','--password', type=str, help='MQTT Password')
parser.add_argument('-t','--topic', type=str, help='MQTT Topic')
args = parser.parse_args()
broker = args.brokker if (args.broker is not None) else 'broker.emqx.io'
port = args.port if (args.port is not None) else 1883
topic = args.topic if (args.topic is not None) else "/python/mqtt"
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = args.username if (args.username is not None) else 'emqx'
password = args.password if (args.password is not None) else 'public'
if(args.rtsp_url is None):
    print("RTSP-Url is not provided")
    sys.exit(0)
# Global boxes
new_boxes = None
old_boxes = None
# Get mouse position and send request
def mouse_click(event, x, y, flags, param):
    global new_boxes
    if(new_boxes is None):
        return
    if event == cv2.EVENT_LBUTTONDOWN:
        for key in new_boxes.keys():
            box = new_boxes[key]
            if(x > box[1] and x < box[3] and y > box[0] and y < box[2]):
                response = requests.post("http://ptz.miem.vmnet.top/", data=json.dumps({
                    "command": "track",
                    "id": key,
                    "room_name": "Studio"
                }))
                print(response.content)
# Connection to mqtt broker
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
# Read message from broker
def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        global old_boxes
        global new_boxes
        old_boxes = new_boxes
        try:
            new_boxes = json.loads(msg.payload.decode())
        except json.decoder.JSONDecodeError:
            print('Not JSON Message\nRaw message: ' + msg.payload.decode())
    client.subscribe(topic)
    client.on_message = on_message

# Stream displaying thread
running = False
def stream_thread(stream):
    global running
    cv2.namedWindow('Preview')
    cv2.setMouseCallback('Preview', mouse_click)
    while stream.isOpened() or running:
        ret, frame = stream.read()
        frame = cv2.resize(frame, (720, 640))
        if(new_boxes is not None and np.array_equal(new_boxes, old_boxes)):
            boxes = new_boxes
            for key in boxes.keys():
                box = boxes[key]
                cv2.rectangle(frame, (box[1], box[0]), (box[3], box[2]), (255, 0, 0), 2)
                cv2.putText(frame,"id:" + key, (box[1], box[2]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1, 1)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        cv2.imshow('Preview', frame)
    cv2.destroyAllWindows()

# Main thread
if __name__ == '__main__':
    stream = cv2.VideoCapture(args.rtsp_url, cv2.CAP_FFMPEG)
    thread = Thread(target=stream_thread, args = [stream], name="stream")
    thread.start()
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()
