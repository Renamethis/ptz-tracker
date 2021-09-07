# AutoSet script

# Starting the virtual environment
import sys
import os

pwd = os.getcwd()
wsdl_path = pwd + '/wsdl'
sys.path.append(pwd+'/classes')

# Loading the libraries

import numpy as np
import math
import cv2
import six.moves.urllib as urllib
import tarfile
import time
import base64
import logging
import tensorflow.compat.v1 as tf
import configparser
from imutils.video import FPS
from onvif import ONVIFCamera
from time import sleep
from threading import Thread
import WebcamVideoStream as WVS
import Tensor as T
from MoveSet import MoveSet
import Utility_Functions as UF
import Ping as P


# Create log file

pid_path = pwd + '/log/pid'
pwd = UF.get_pwd("log")
logger = logging.getLogger("Main")
logger.setLevel(logging.INFO)
fh = logging.FileHandler(pwd+"/main.log")

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

# Get parameters from settings

ip = UF.get_setting("Onvif", "ip")
port = UF.get_setting("Onvif", "port")
login = UF.get_setting("Onvif", "login")
password = UF.get_setting("Onvif", "password")
speed_coef = float(UF.get_setting("Onvif", "speed_coef"))
tweaking = float(UF.get_setting("Onvif", "tweaking"))/100.0
bounds = [float(i) for i in UF.get_setting("Onvif", "bounds")
          .replace(" ", "").split(",")]
isAbsolute = bool(UF.get_setting("Onvif", "Absolute"))
length = int(UF.get_setting("Processing", "length"))
hight = int(UF.get_setting("Processing", "hight"))
l_h = [hight, length, hight, length]
tracking_box = (np.array([float(i) for i in UF.get_setting("Processing", "box")
                         .replace(" ", "").split(",")]) * l_h).astype(int)
limits = (np.array([float(i) for i in UF.get_setting("AutoSet", "Bounds")
                    .replace(" ", "").split(",")]) * l_h).astype(int)
limits = [float(i) for i in UF.get_setting("Processing", "limits")
          .replace(" ", "").split(",")]
COLOR_LIGHT = np.array([int(i) for i in UF.get_setting("AutoSet", "COLOR_LIGHT")
                       .replace(" ", "").split(",")])
COLOR_DARK = np.array([int(i) for i in UF.get_setting("AutoSet", "COLOR_DARK")
                      .replace(" ", "").split(",")])
# Initializing main classes
tensor = T.Tensor(hight=hight, length=length)
move = MoveSet(speed_coef, ip, port, login, password, wsdl_path,
               [hight, length], [COLOR_LIGHT, COLOR_DARK],
               limits, tracking_box)
rtsp_url = "rtsp://" + login + ":" + password + "@" + \
            move.cam.getStreamUri().split('//')[1]
stream = WVS.WebcamVideoStream(rtsp_url, Jetson=(1 if (UF.get_setting(
                               "Hardware", "device") == 'Jetson') else 0))
RIGHT = limits[2]
LEFT = limits[0]
BOTTOM = limits[1]


# Check pixels function
def check(pixel):
    if(pixel[1] >= RIGHT or pixel[1] <= LEFT or pixel[0] <= BOTTOM):
        return True
    return False


# Starting all threads
ping = P.Ping(mycam_ip=ip)
stream.start()
tensor.start()
move.start()
ping.start()
sleep(10)
# Opencv object tracking tracking init

#tracker = cv2.TrackerCSRT_create()
#isTracking = False

# Main loop

next_time = 0
box_shape = None
while move.isProcessing:
    img = stream.read()
    if False:
        stream.stop()
        logger.warning("Camera conection lost. Reconnect...")
        while ping.read() != 0 or not stream.check_connect() or stream.status():
            sleep(1)
        stream = WVS.WebcamVideoStream(login + ":" + password + "@" + move.cam.getStreamUri(),
                                       Jetson=(1 if (UF.get_setting('device')
                                               == 'Jetson') else 0))
        stream.start()
        logger.info("Camera conection restored.")
        img = stream.read()

    if img is not None:
        img = cv2.resize(img, (length, hight))
        frame = img
        tensor.set_image(img)
        img = tensor.read()
        if img is not None: #and not isTracking:
            scores = tensor.read_scores().numpy()
            image_np = tensor.read()
            classes = tensor.read_classes().numpy()
            boxes = tensor.read_boxes().numpy()
            if (scores is not None and image_np is not None and classes is not None and boxes is not None):
                score = np.where(scores == np.max(scores))
                if (scores[score][0] > 0.6):
                    image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    img = 0*np.zeros((hight, length), dtype=np.uint8)
                    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
                    mask = cv2.inRange(hsv, COLOR_DARK, COLOR_LIGHT)
                    mask = cv2.bitwise_not(mask)
                    pixels = np.argwhere(mask == 255)
                    pixels = pixels[np.array(list(map(check, pixels)))]
                    for pixel in pixels:
                        img[pixel[0]][pixel[1]] = 255
                    _, contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    box = boxes[score][0]
                    box = (l_h*box)
                    move.set_con(contours)
                    move.set_box(box)
                else:
                    move.set_box(None)
stream.stop()
tensor.stop()
ping.stop()
move.stop()
with open(pid_path, 'w') as pid_file:
    pid_file.write('')
