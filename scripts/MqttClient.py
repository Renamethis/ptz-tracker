### TRACKER ASSISTANT TEST CLIENT
import argparse
from paho.mqtt import client as mqtt_client
import random
from json import loads
import cv2
from threading import Thread
import numpy as np
import sys
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
parser.add_argument('-t','--topic', type=str, help='MQTT Password')
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
            new_boxes = loads(msg.payload.decode())
        except:
            print('Broken')
    client.subscribe(topic)
    client.on_message = on_message

# Stream displaying thread
running = False
def stream_thread(stream):
    global running
    while stream.isOpened() or running:
        ret, frame = stream.read()
        cv2.resize(frame, (720, 640))
        if(new_boxes is not None and np.array_equal(new_boxes, old_boxes)):
            for box in new_boxes.values():
                cv2.rectangle(frame, box, (255, 0, 0), 2)
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
