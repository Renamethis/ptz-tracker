import os
import sys
import cv2
import configparser
from threading import Thread
import traceback
import time
from time import sleep
import numpy as np
import Utility_Functions as UF
import logging
################################
# 1. The process of taking a frame from a stream
################################

class WebcamVideoStream:
  # 1.1. Initialization
  def __init__(self, name="WebcamVideoStream", GStreamer=True, Jetson=False):
    try:
      self.name = name
      # 1.1.1. Determining the path to the configuration file
      # add_try (count >= 3)


      init_logger = logging.getLogger("Main.%s.init" % (self.name))

      # 1.1.2. Read configuration file (rtsp)
      # modify (receiving rtsp from camera)

      self.mycam_rtsp = UF.get_setting("rtsp")
      print(self.mycam_rtsp)
      self.mycam_ip = UF.get_setting("ip")

      # 1.1.3. Sturt function cv2.VideoCapture

      try:
        if(GStreamer):
            if(Jetson):
                self.mycam_rtsp = 'rtspsrc location="' + self.mycam_rtsp + '" ! rtph264depay ! h264parse ! omxh264dec ! nvvidconv ! appsink'
            else:
                self.mycam_rtsp = 'rtspsrc location="' + self.mycam_rtsp + '" ! rtph264depay ! decodebin ! videoconvert ! appsink'
            self.stream = cv2.VideoCapture(self.mycam_rtsp, cv2.CAP_GSTREAMER)
        else:
            self.stream = cv2.VideoCapture(self.mycam_rtsp, cv2.CAP_FFMPEG)
      except:
        init_logger.critical("Error with cv2.VideoCapture")
        init_logger.exception("Error!")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err_msg = str(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
        #UF.send_msg(msg=err_msg)
        sys.exit(0)

      if self.stream.isOpened() is False:

        err_msg = "Stream is close"
        init_logger.critical(err_msg)
        init_logger.info("Check rtsp in settings file")
        #UF.send_msg(msg=err_msg)
        sys.exit(0)
      else:
        init_logger.info("Process get rtsp stream.")


      # 3.1.4. Read frame
      (self.grabbed, self.frame) = self.stream.read()
      self.stopped = False
    except:
      init_logger.critical("Error in %s.__init__" % (self.name))
      init_logger.exception("Error!")
      exc_type, exc_value, exc_traceback = sys.exc_info()
      err_msg = str(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
      #UF.send_msg(msg=err_msg)
      sys.exit(0)

  # 3.2. Start thread
  def start(self):
    self.stopped = False
    start_logger = logging.getLogger("Main.%s.start" % (self.name))
    start_logger.info("Process starting")
    self.t = Thread(target=self.update, name=self.name, args=())
    self.t.daemon = True
    self.t.start()
    return self

  # 3.3. Infinite loop of receiving frames from a stream
  def update(self):
    try:
      update_logger = logging.getLogger("Main.%s.update" % (self.name))
      stream = self.stream
      update_logger.info("Process started")
      i = 0
      time_1 = time.time()
      err = 0

      while True:
        if self.stopped:
          update_logger.info("%s stopped" % self.name)
          return
        (self.grabbed, self.frame) = stream.read()
        #print self.frame

        i = i + 1
        if (i == 25):
          time_2 = time.time()
          err =  err + time_2 - time_1 - 1
          if err < 0:
            err = 0
          i = 0
          time_1 = time.time()
          update_logger.debug("Delay time: %f" % (err))
    except:
      update_logger.critical("Error in process")
      update_logger.exception("Error!")
      exc_type, exc_value, exc_traceback = sys.exc_info()
      err_msg = str(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
      print(err_msg)
      sys.exit(0)
  def check_connect(self):
    try:
      check_stream = cv2.VideoCapture(self.mycam_rtsp)
    except:
      return False
    if check_stream.isOpened() is False:
      check_stream.release()
      return False
    else:
      check_stream.release()
      return True

  def status(self):
    return self.t.isAlive()
  # 3.4. Get frame
  def read(self):
    return self.frame

  def stop(self):
    self.stopped = True
