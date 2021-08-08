
# Main tracker script

# Starting the virtual environment
import sys
import os

pwd = os.getcwd()
wsdl_path = pwd + '/wsdl'
sys.path.append(pwd+'/classes')

pwd = os.getcwd()
sys.path.append(pwd)
sys.path.append(pwd+'/slim')

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
import Move2 as M2
import Utility_Functions as UF
import Ping as P


# Create log file

pwd = UF.get_pwd("log")
logger = logging.getLogger("Main")
logger.setLevel(logging.INFO)
fh = logging.FileHandler(pwd+"/main.log")

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
# Get parameters from settings

ip = UF.get_setting("ip")
length = int(UF.get_setting("length"))
hight = int(UF.get_setting("hight"))
port = UF.get_setting("port")
login = UF.get_setting("login")
password = UF.get_setting("password")
speed_coef = float(UF.get_setting("speed_coef"))
tweaking = float(UF.get_setting("tweaking"))/100.0
zone = int(UF.get_setting("trackingzone"))
bounds = [float(UF.get_setting("x1")),
          float(UF.get_setting("y1")),
          float(UF.get_setting("x2")),
          float(UF.get_setting("y2"))]
tensor = T.Tensor(hight=hight, length=length)
move = M2.Move(length, hight, speed_coef, ip, port, login,
               password, wsdl_path, tweaking, bounds, zone)
rtsp_url = "rtsp://" + login + ":" + password + "@" + move.cam.getStreamUri().split('//')[1]
stream = WVS.WebcamVideoStream(rtsp_url,
                               Jetson=(1 if (UF.get_setting('device')
                                       == 'Jetson') else 0))

stream.start()
tensor.start()
move.start()
ping = P.Ping(mycam_ip=ip)
ping.start()

#tracker = cv2.TrackerCSRT_create()
isTracking = False

next_time = 0
box_shape = None
while True:
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
        if img is not None and not isTracking:
            scores = tensor.read_scores().numpy()
            image_np = tensor.read()
            classes = tensor.read_classes().numpy()
            boxes = tensor.read_boxes().numpy()
            if (scores is not None and image_np is not None and classes is not None and boxes is not None):
                score = np.where(scores == max(scores))
                if (scores[score][0] > 0.6):
                    l_h = [hight, length, hight, length]
                    box = boxes[score][0]
                    box = (l_h*box)
                    move.set_box(box)
                    cv2.imwrite('test.png', img)
                    #box_shape = [int(box[2] - box[0]), int(box[3] - box[1])]
                    #tracker.init(frame, box)
                    #isTracking = True
                else:
                    move.set_box(None)
        '''elif isTracking:
            (success, box) = tracker.update(frame)
            print(success)
            if(success):
                l_h = [hight, length, hight, length]
               # box = (l_h*box).astype(int)
                #print(np.asarray(box))
                shape = [int(box[2] - box[0]), int(box[3] - box[1])]
                img = img[int(box[0]):int(box[2]), int(box[1]):int(box[3])]
                cv2.imshow('BOX', img)
                if(shape[0]/box_shape[0] < 0.7 and shape[1]/box_shape[1] < 0.7):
                    isTracking = False
                move.set_box(np.asarray(box))
            else:
                move.set_box(None)
                isTracking = False
        '''
