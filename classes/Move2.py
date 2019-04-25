import os
import sys
import cv2
import configparser
from threading import Thread
from onvif import ONVIFCamera
import traceback
import time
from time import sleep
import numpy as np
import Utility_Functions as UF
import logging
################################
# 3. The process of taking a frame from a stream
################################

class Move:
  # 3.1. Initialization
  def __init__(self, length, hight,speed_coef, mycam_ip, mycam_port, mycam_login, mycam_password, mycam_wsdl_path, name="Move"):
    try:
      self.name = name
      self.box = None
      self.old_box = None
      self.mycam_ip = mycam_ip
      self.mycam_port = mycam_port
      self.mycam_login = mycam_login
      self.mycam_password = mycam_password
      self.mycam_wsdl_path = mycam_wsdl_path
      self.length = length
      self.hight = hight
      self.old_vec_x = 0
      self.old_vec_y = 0
      self.count_frame = 0
      self.speed_coef = speed_coef

      init_logger = logging.getLogger("Main.%s.init" % (self.name))
      try:
        mycam = ONVIFCamera(self.mycam_ip, self.mycam_port, self.mycam_login, self.mycam_password, self.mycam_wsdl_path)
        init_logger.info("Successful conection ONVIFCamera")
      except:
        err_msg = "Error with conect ONVIFCamera..."
        init_logger.critical(err_msg)
        init_logger.info("Check the correctness of the entered data in the setings.ini (ip,port,login, password or wsdl_path)")
        UF.send_msg(msg=err_msg)
        sys.exit(0)


      media = mycam.create_media_service()
      profile = media.GetProfiles()[0]
      self.ptz = mycam.create_ptz_service()
      self.request = self.ptz.create_type('GetConfigurationOptions')
      self.request.ConfigurationToken = profile.PTZConfiguration._token
      ptz_configuration_options = self.ptz.GetConfigurationOptions(self.request)
      self.request = self.ptz.create_type('ContinuousMove')
      self.request.ProfileToken = profile._token
    except:
      init_logger.critical("Error in %s.__init__" % (self.name))
      init_logger.exception("Error!")
      exc_type, exc_value, exc_traceback = sys.exc_info()
      err_msg = str(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
      UF.send_msg(msg=err_msg)
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
      update_logger.info("Process started")
      while True:
        if self.stopped:
          return
        box = self.box
        old_box = self.old_box
        #print box
        if np.array_equal(box,old_box):
          sleep(0.2)
        elif box is not None:
          to_x = int(abs(box[1] - box[3])/2.0 + box[1])
          to_y = int(box[0])
          
          

          if (to_x < self.length/3 - 80 or to_x > self.length/3 + 80):
            if to_x > self.length/3:
              vec_x = float(to_x - self.length/3)/(self.length)
            else:
              vec_x = float(to_x - self.length/3)/(self.length)*2
          else:
            vec_x = 0
          if (to_y < self.hight/3 - 80 or to_y > self.hight/3 + 80):
            vec_y = float(self.hight/3 - to_y)/(self.hight)
          else:
            vec_y = 0

          self.count_frame = 0

          vec_x = vec_x*self.speed_coef
          vec_y = vec_y*self.speed_coef
          self.request.Velocity.PanTilt._x = vec_x
          self.request.Velocity.PanTilt._y = vec_y 
          try:
            self.ptz.ContinuousMove(self.request)
          except:
            update_logger.exception("Error!")
            sleep(2)
            try:
              mycam = ONVIFCamera(self.mycam_ip, self.mycam_port, self.mycam_login, self.mycam_password, self.mycam_wsdl_path)
              print "[INFO]     Successful conection ONVIFCamera"
            except:
              err_msg = "[ERROR]    Error with conect ONVIFCamera..."
              print err_msg
              print "[INFO]     Check the correctness of the entered data in the setings.ini (ip,port,login, password or wsdl_path)"
              UF.send_msg(msg=err_msg)
              sys.exit(0)

          old_box = box

        elif box is None and old_box is not None:
          self.request.Velocity.PanTilt._x = vec_x
          self.request.Velocity.PanTilt._y = vec_y 
          if (self.count_frame == 30):
            self.request.Velocity.PanTilt._x = 0
            self.request.Velocity.PanTilt._y = 0 
            old_box = box
            self.count_frame = 0
            sleep (0.1)
          try:
            self.ptz.ContinuousMove(self.request)
          except:
            update_logger.exception("Error!")
            sleep(2)
            try:
              mycam = ONVIFCamera(self.mycam_ip, self.mycam_port, self.mycam_login, self.mycam_password, self.mycam_wsdl_path)
              print "[INFO]     Successful conection ONVIFCamera"
            except:
              err_msg = "[ERROR]    Error with conect ONVIFCamera..."
              print err_msg
              print "[INFO]     Check the correctness of the entered data in the setings.ini (ip,port,login, password or wsdl_path)"
              UF.send_msg(msg=err_msg)
              sys.exit(0)

          self.count_frame = self.count_frame + 1

        self.old_box = old_box


        
    except:
      update_logger.critical("Error in process")
      update_logger.exception("Error!")
      exc_type, exc_value, exc_traceback = sys.exc_info()
      err_msg = str(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
      print err_msg
      sys.exit(0)

  def status(self):
    return self.t.isAlive()
  def set_box(self, box):
    self.box = box
  def stop(self):
    self.stopped = True
