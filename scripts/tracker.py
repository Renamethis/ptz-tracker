# Main tracker script

# Starting the virtual environment
import sys
import os
wsdl_path = os.path.abspath(os.getcwd()).split('/classes')[0] + '/wsdl'

pwd = os.getcwd()
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

tf.disable_v2_behavior()
pwd = UF.get_pwd("log")
logger = logging.getLogger("Main")
logger.setLevel(logging.INFO)
fh = logging.FileHandler(pwd+"/main.log")
pwd_images_to_recognize = UF.get_pwd("images_to_recognize")
pwd_recognition_queue = UF.get_pwd("recognition_queue")


formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

logger.info("__________________Program_started__________________")


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
stream = WVS.WebcamVideoStream(move.cam.getStreamUri(),
                               Jetson=(1 if (UF.get_setting('device')
                                       == 'Jetson') else 0))
stream.start()
tensor.start()
move.start()
ping = P.Ping(mycam_ip=ip)
ping.start()

next_time = 0

while True:
    img = stream.read()

    if ping.read() != 0:
        stream.stop()
        logger.warning("Camera conection lost. Reconnect...")
        while ping.read() != 0 or not stream.check_connect() or stream.status():
            sleep(1)

        stream = WVS.WebcamVideoStream(move.cam.getStreamUri(),
                                       Jetson=(1 if (UF.get_setting('device')
                                               == 'Jetson') else 0))
        stream.start()
        logger.info("Camera conection restored.")
        img = stream.read()

    if img is not None:

        img = cv2.resize(img, (length, hight))
        tensor.set_image(img)
        img = tensor.read()
        if img is not None:
            scores = tensor.read_scores()
            image_np = tensor.read()
            classes = tensor.read_classes()
            boxes = tensor.read_boxes()
            if (scores.any() and image_np is not None and classes is not None and boxes is not None):
                scores[scores > 0.45] = 1
                classes = classes*scores
                persons = np.where(classes == 1)[1]

                if (str(persons) != '[]'):
                    person = persons[0]
                    l_h = [hight, length, hight, length]
                    box = boxes[0][person]
                    box = l_h*box
                    move.set_box(box)
                else:
                    move.set_box(None)
