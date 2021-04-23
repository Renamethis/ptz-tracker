
import sys
import os

import smtplib
import traceback
import numpy
import cv2
def send_msg(msg,SUBJECT="Error",TO="prostepm21@gmail.com"):
  HOST="smtp.gmail.com"
  FROM = "tensorflow21@gmail.com"
  BODY = "\r\n".join((
    "From: %s" % FROM,
    "To: %s" % TO,
    "Subject: %s" % SUBJECT ,
    "",
    msg
  ))

  server = smtplib.SMTP(HOST, 587)
  server.starttls()
  server.login(FROM, base64.b64decode('VGVuc29yNTUyMQ=='))
  server.sendmail(FROM, [TO], BODY)
  server.quit()


import cv2
cap = cv2.VideoCapture("rtsp://192.168.15.45:554/2")

while(cap.isOpened()):
    ret, frame = cap.read()
    cv2.imshow('frame', frame)
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break
'''
open_cv_image = numpy.array(pil_image) 
# Convert RGB to BGR 
open_cv_image = open_cv_image[:, :, ::-1].copy() 
print (open_cv_image)
'''
client.close()

'''
player=vlc.MediaPlayer('rtsp://192.168.15.45:554')
player.play()
while True:
  print (player.__dict__)

sys.exit(0)

try:
  ###
  ## add_try  - add validation
  ## modify   - it is possible to change
  ## add_func - add function
  ## error    - error 
  ### 



  ################################
  # 1. Starting the virtual environment
  ################################

  # add_func (execute the command: "export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/slim")

  activate_this_file = "venv/bin/activate_this.py"
  execfile(activate_this_file, dict(__file__=activate_this_file))
  import sys
  import os
  os.system('cp -f utility_function/mobilenet_v1.py models/research/slim/nets/') 
  os.system('cp -f utility_function/visualization_utils.py models/research/object_detection/utils/') 
  os.chdir('models/research')
  os.chdir('object_detection')

  ################################
  # 2. Loading the libraries
  ################################

  # add_try (checking libraries)

  import numpy as np
  import math
  import cv2
  import six.moves.urllib as urllib
  import tarfile
  import time
  import base64
  import pyping
  import tensorflow as tf
  import configparser
  from imutils.video import FPS
  from onvif import ONVIFCamera
  from time import sleep
  from threading import Thread
  from object_detection.utils import label_map_util
  from object_detection.utils import visualization_utils as vis_util

  ################################
  # 3. The process of taking a frame from a stream
  ################################

  class WebcamVideoStream:
    # 3.1. Initialization
    def __init__(self, name="WebcamVideoStream"):
      
      # 3.1.1. Determining the path to the configuration file
      # add_try (count >= 3)

      pwd = os.getcwd()
      lst = pwd.split('/')
      count = len(lst)-3
      string = ""
      for i in range(count):
        string = string + lst[i] + "/"
      pwd = string

      # 3.1.2. Read configuration file (rtsp)
      # add_try (checking file existence)
      # add_try (check the existence of settings in Conf. file)
      # modify (receiving rtsp from camera)

      config = configparser.ConfigParser()
      config.read(pwd + "conf/settings.ini")
      mycam_rtsp = config.get("Settings","rtsp")

      # 3.1.3. Sturt function cv2.VideoCapture
      # modify (replace print with logging)
      
      try:
        self.stream = cv2.VideoCapture(mycam_rtsp)
        print "[INFO]     Successful conection VideoCapture"
      except:
        err_msg = "[ERROR]    Error with cv2.VideoCapture..."
        print err_msg
        print "[INFO]     Check the correctness of the entered data in the setings.ini (rtsp)"
        send_msg(msg=err_msg)
        sys.exit(0)


      # 3.1.4. Read frame
      (self.grabbed, self.frame) = self.stream.read()
      #print self.frame
      self.name = name
      self.stopped = False

    # 3.2. Start thread
    def start(self):
      t = Thread(target=self.update, name=self.name, args=())
      t.daemon = False
      t.start()
      return self

    # 3.3. Infinite loop of receiving frames from a stream
    def update(self):
      stream = self.stream
      print "[INFO]     VideoCapture started"
      i = 0
      time_1 = time.time()
      err = 0
      while True:
        #print 1
        if self.stopped:
          print "[INFO]     VideoCapture stopped"
          return
        (self.grabbed, self.frame) = stream.read()
        i = i + 1
        sleep(0.01)
        if (i == 25):
          time_2 = time.time()
          err =  err + time_2 - time_1 - 1
          if err < 0:
            err = 0
          i = 0
          time_1 = time.time()
          print 'WideoStream err = ' + str(err)

    # 3.4. Get frame
    def read(self):
      return self.frame

    # 3.5. Stop frame
    def stop(self):
      self.stopped = True


  
  def main():
    image_np_old = []
    stream = WebcamVideoStream()
    stream.start()


    lenght_float = 720.0 
    width_float = 576.0
    lenght = int(lenght_float)
    width = int(width_float)

    


    
    while True:
      image_np = stream.read()
      #print image_np
      
      #image_np = cv2.resize(image_np, (720,405))
      cv2.imshow('object detection', image_np)

      if cv2.waitKey(25) & 0xFF == ord('q'):
        stream.stop()
        sys.exit(0)

  
  main()

except:
  exc_type, exc_value, exc_traceback = sys.exc_info()
  err_msg = str(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
  send_msg(msg=err_msg)
  
  #main()
'''
