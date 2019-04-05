activate_this_file = "venv/bin/activate_this.py"
execfile(activate_this_file, dict(__file__=activate_this_file))

import sys
import os
#sys.path.append("./models/reserch")
#os.system('pwd')
#os.chdir('models/research')
#os.system('export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/slim')
#os.chdir('object_detection')

import numpy as np
import math
import os
import six.moves.urllib as urllib
import tarfile
import tensorflow as tf
import zipfile
import threading
import configparser

from collections import defaultdict
from io import StringIO
from PIL import Image

import cv2
from imutils.video import VideoStream
from imutils.video import FPS
from onvif import ONVIFCamera
from time import sleep
from threading import Thread

from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
from time import ctime, sleep





class WebcamVideoStream:
  def __init__(self, name="WebcamVideoStream"):
    #def __init__(self, src='rtsp://192.168.11.33:554', name="WebcamVideoStream"):
    #def __init__(self, src='rtsp://192.168.11.43:554', name="WebcamVideoStream"):
    #def __init__(self, src='rtsp://192.168.11.52:554/live/av0', name="WebcamVideoStream"):
    


    config = configparser.ConfigParser()
    config.read("conf/settings.ini")
    mycam_rtsp = config.get("Settings","rtsp")
    
    try:
      self.stream = cv2.VideoCapture(mycam_rtsp)
      print "[INFO]     Successful conection VideoCapture"
    except:
      print "[ERROR]    Error with cv2.VideoCapture..."
      print "[INFO]     Check the correctness of the entered data in the setings.ini (rtsp)"
    (self.grabbed, self.frame) = self.stream.read()
    self.name = name
    self.stopped = False


  def start(self):
    t = Thread(target=self.update, name=self.name, args=())
    t.daemon = True
    t.start()
    return self

  def update(self):
    while True:
      if self.stopped:
        return
      (self.grabbed, self.frame) = self.stream.read()

  def read(self):
    return self.frame

  def stop(self):
    self.stopped = True









config = configparser.ConfigParser()
config.read("conf/settings.ini")
mycam_ip        = config.get("Settings","ip")
mycam_port      = config.get("Settings","port")
mycam_login     = config.get("Settings","login")
mycam_password  = config.get("Settings","password")
mycam_wsdl_path = config.get("Settings","wsdl_path")

mycam = ONVIFCamera(mycam_ip, mycam_port, mycam_login, mycam_password, mycam_wsdl_path)
#mycam = ONVIFCamera('192.168.15.43', 80, 'admin', 'Supervisor', '/etc/onvif/wsdl/')

media = mycam.create_media_service()
profile = media.GetProfiles()[0]
ptz = mycam.create_ptz_service()
request = ptz.create_type('GetConfigurationOptions')
request.ConfigurationToken = profile.PTZConfiguration._token
ptz_configuration_options = ptz.GetConfigurationOptions(request)
request = ptz.create_type('ContinuousMove')
request.ProfileToken = profile._token
print (request)







lenght_float = 1280.0 
width_float = 720.0
lenght = int(lenght_float)
width = int(width_float)
first = []
second = []

#old_image_np = cap.read()
threads = []
stream = WebcamVideoStream()
stream.start()
print ('START')



while True:
  image_np = stream.read()
  cv2.imshow('object detection', image_np)
  if cv2.waitKey(25) & 0xFF == ord('q'):
    request.Velocity.PanTilt._x = 0
    request.Velocity.PanTilt._y = 0
    request.Velocity.Zoom._x = 0
    ptz.ContinuousMove(request)
    break
  elif cv2.waitKey(25) & 0xFF == ord(']'):
    request.Velocity.PanTilt._x = 0
    request.Velocity.PanTilt._y = 0
    request.Velocity.Zoom._x = -1
    ptz.ContinuousMove(request)
  elif cv2.waitKey(25) & 0xFF == ord('d'):
    request.Velocity.PanTilt._x = 1
    request.Velocity.PanTilt._y = 0
    request.Velocity.Zoom._x = 0
    ptz.ContinuousMove(request)
  elif cv2.waitKey(25) & 0xFF == ord('a'):
    request.Velocity.PanTilt._x = -1
    request.Velocity.PanTilt._y = 0
    request.Velocity.Zoom._x = 0
    ptz.ContinuousMove(request)
  elif cv2.waitKey(25) & 0xFF == ord('w'):
    request.Velocity.PanTilt._x = 0
    request.Velocity.PanTilt._y = 1
    request.Velocity.Zoom._x = 0
    ptz.ContinuousMove(request)
  elif cv2.waitKey(25) & 0xFF == ord('s'):
    request.Velocity.PanTilt._x = 0
    request.Velocity.PanTilt._y = -1
    request.Velocity.Zoom._x = 0
    ptz.ContinuousMove(request)
  elif cv2.waitKey(25) & 0xFF == ord('['):
    request.Velocity.PanTilt._x = 0
    request.Velocity.PanTilt._y = 0
    request.Velocity.Zoom._x = 1
    ptz.ContinuousMove(request)
  else:
    request.Velocity.PanTilt._x = 0
    request.Velocity.PanTilt._y = 0
    request.Velocity.Zoom._x = 0
    ptz.ContinuousMove(request)