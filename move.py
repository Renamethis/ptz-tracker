activate_this_file = "venv/bin/activate_this.py"
exec(compile(open(activate_this_file, "rb").read(), activate_this_file, 'exec'), dict(__file__=activate_this_file))
import sys
import os
os.system('cp -f utility_function/mobilenet_v1.py models/research/slim/nets/')
os.system('cp -f utility_function/visualization_utils.py models/research/object_detection/utils/')

pwd = os.getcwd()
sys.path.append(pwd+'/classes')

os.chdir('models/research')

pwd = os.getcwd()
sys.path.append(pwd)
sys.path.append(pwd+'/slim')

os.chdir('object_detection')

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
import Utility_Functions as UF





class WebcamVideoStream:
  def __init__(self, name="WebcamVideoStream"):
    #def __init__(self, src='rtsp://192.168.11.33:554', name="WebcamVideoStream"):
    #def __init__(self, src='rtsp://192.168.11.43:554', name="WebcamVideoStream"):
    #def __init__(self, src='rtsp://192.168.11.52:554/live/av0', name="WebcamVideoStream"):




    mycam_rtsp = UF.get_setting("rtsp")

    try:
      self.stream = cv2.VideoCapture(mycam_rtsp)
      print("[INFO]     Successful conection VideoCapture")
    except:
      print("[ERROR]    Error with cv2.VideoCapture...")
      print("[INFO]     Check the correctness of the entered data in the setings.ini (rtsp)")
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
mycam_ip        = UF.get_setting("ip")
mycam_port      = UF.get_setting("port")
mycam_login     = UF.get_setting("login")
mycam_password  = UF.get_setting("password")
mycam_wsdl_path = UF.get_setting("wsdl_path")

print(mycam_ip)
print(mycam_port)
print(mycam_login)
print(mycam_password)
print(mycam_wsdl_path)

mycam = ONVIFCamera(mycam_ip, mycam_port, mycam_login, mycam_password, mycam_wsdl_path)
#mycam = ONVIFCamera('192.168.15.43', 80, 'admin', 'Supervisor', '/etc/onvif/wsdl/')

media = mycam.create_media_service()
profile = media.GetProfiles()[1]
ptz = mycam.create_ptz_service()
request = media.create_type('GetStreamUri')
request.ProfileToken = profile.token
rtsp = self.media.GetStreamUri(self.request)['Uri']
request = ptz.create_type('GetConfigurationOptions')
request.ConfigurationToken = profile.PTZConfiguration.token
ptz_configuration_options = ptz.GetConfigurationOptions(request)
request = ptz.create_type('ContinuousMove')
request.ProfileToken = profile.token
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
status = ptz.GetStatus({'ProfileToken': profile.token})
status.Position.PanTilt.x = 0.0
status.Position.PanTilt.y = 0.0
request.Velocity = status.Position


while True:
  image_np = stream.read()
  cv2.imshow('object detection', image_np)
  if cv2.waitKey(1) & 0xFF == ord('q'):
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = 0
    request.Velocity.Zoom._x = 0
    ptz.ContinuousMove(request)
    break
  elif cv2.waitKey(1) & 0xFF == ord(']'):
    while cv2.waitKey(1) & 0xFF == ord(']'):
      request.Velocity.PanTilt.x = 0
      request.Velocity.PanTilt.y = 0
      request.Velocity.Zoom.x = -1
      ptz.ContinuousMove(request)
  elif cv2.waitKey(1) & 0xFF == ord('d'):
    while cv2.waitKey(1) & 0xFF == ord('d'):
      request.Velocity.PanTilt.x = 1
      request.Velocity.PanTilt.y = 0
      request.Velocity.Zoom.x = 0
      ptz.ContinuousMove(request)
  elif cv2.waitKey(1) & 0xFF == ord('a'):
    while  cv2.waitKey(1) & 0xFF == ord('a'):
      request.Velocity.PanTilt.x = -1
      request.Velocity.PanTilt.y = 0
      request.Velocity.Zoom.x = 0
      ptz.ContinuousMove(request)
  elif cv2.waitKey(1) & 0xFF == ord('w'):
    while cv2.waitKey(1) & 0xFF == ord('w'):
      request.Velocity.PanTilt.x = 0
      request.Velocity.PanTilt.y = 1
      request.Velocity.Zoom.x = 0
      ptz.ContinuousMove(request)
  elif cv2.waitKey(1) & 0xFF == ord('s'):
    while cv2.waitKey(1) & 0xFF == ord('s'):
      request.Velocity.PanTilt.x = 0
      request.Velocity.PanTilt.y = -1
      request.Velocity.Zoom.x = 0
      ptz.ContinuousMove(request)
  elif cv2.waitKey(1) & 0xFF == ord('['):
    while cv2.waitKey(1) & 0xFF == ord('['):
      request.Velocity.PanTilt.x = 0
      request.Velocity.PanTilt.y = 0
      request.Velocity.Zoom.x = 1
      ptz.ContinuousMove(request)
  else:
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = 0
    request.Velocity.Zoom.x = 0
    ptz.ContinuousMove(request)
