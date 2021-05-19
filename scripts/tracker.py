import smtplib
import traceback




################################
# 1. Starting the virtual environment
################################
import sys
import os
wsdl_path = os.path.abspath(os.getcwd()).split('/classes')[0] + '/wsdl'
print(wsdl_path)
os.system('cp -f utility_function/mobilenet_v1.py models/research/slim/nets/')
os.system('cp -f utility_function/visualization_utils.py models/research/object_detection/utils/')

pwd = os.getcwd()
sys.path.append(pwd+'/classes')

os.chdir('models/research')

pwd = os.getcwd()
sys.path.append(pwd)
sys.path.append(pwd+'/slim')

os.chdir('object_detection')


################################
# 2. Loading the libraries
################################


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
from object_detection.utils import visualization_utils as vis_util
import WebcamVideoStream as WVS
import Tensor as T
import Move as M
import Move2 as M2
import Utility_Functions as UF
import Ping as P


################################
# 3. Create log file
################################

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


################################
# 4. Get settings from settings
################################

ip = UF.get_setting("ip")
length = int(UF.get_setting("length"))
hight = int(UF.get_setting("hight"))
port = UF.get_setting("port")
login = UF.get_setting("login")
password = UF.get_setting("password")
visible = UF.get_setting("visible")
speed_coef = float(UF.get_setting("speed_coef"))
init = UF.get_setting("init")


stream = WVS.WebcamVideoStream()
tensor = T.Tensor(visible = visible,model_name = 'ssd_mobilenet_v2_body')
move = M2.Move(length = length, hight = hight, speed_coef = speed_coef,  mycam_ip = ip, mycam_port = port, mycam_login = login, mycam_password = password, mycam_wsdl_path = wsdl_path)

stream.start()
tensor.start()
move.start()
ping = P.Ping(mycam_ip = ip)
ping.start()

if init == 'Yes':
  speed_coef = UF.init_tracker(stream=stream, tensor=tensor, move=move, length=length, hight=hight, speed_coef=speed_coef)
  print(speed_coef)
  move.set_speed_coef(speed_coef)


move.goto_home()
next_time = 0

while True:
  img = stream.read()

  if ping.read()  != 0:
    stream.stop()
    logger.warning("Camera conection lost. Reconnect...")
    while ping.read() != 0 or not stream.check_connect() or stream.status():
      sleep(1)


    stream = WVS.WebcamVideoStream()
    stream.start()
    logger.info("Camera conection restored.")


    img = stream.read()


  if img is not None:

    img = cv2.resize(img, (length,hight))
    tensor.set_image(img)
    img = tensor.read()
    #print tensor.get_tps()

    if img is not None:
      scores   = tensor.read_scores()
      image_np = tensor.read()
      classes  = tensor.read_classes()
      boxes    = tensor.read_boxes()


      if (scores.any() and image_np is not None and classes is not None and boxes is not None):
        scores[scores > 0.45] = 1
        classes = classes*scores
        persons   = np.where(classes == 1)[1]
        #####print tensor.get_tps()

        if (str(persons) != '[]'):

          person = persons[0]
          l_h = [hight,length,hight,length]
          box = boxes[0][person]
          box = l_h*box
          move.set_box(box)
          #print box
        else:
          move.set_box(None)
      if (visible == 'Yes'):
        cv2.imshow('frame', img)

  if cv2.waitKey(20) & 0xFF == ord('q'):
    move.set_box(None)
    sleep(1)
    logger.info("Done!")
    break