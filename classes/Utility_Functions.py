import os
import sys
import smtplib
import base64
from time import sleep
from threading import Thread
import configparser
import numpy as np
import logging
import cv2

def send_msg(msg,SUBJECT="Error",TO="prostepm21@gmail.com"):
  send_msg_logger = logging.getLogger("Main.functions.send_msg")
  HOST="smtp.gmail.com"
  FROM = "tensorflow21@gmail.com"
  BODY = "\r\n".join((
    "From: %s" % FROM,
    "To: %s" % TO,
    "Subject: %s" % SUBJECT ,
    "",
    msg
  ))
  try:
    server = smtplib.SMTP(HOST, 587)
  except:
    send_msg_logger.critical("Problem with internet connection.")
    send_msg_logger.exception("Error!")
    exit(0)
  server.starttls()
  server.login(FROM, base64.b64decode('VGVuc29yNTUyMQ=='))
  server.sendmail(FROM, [TO], BODY)
  server.quit()



def get_pwd(dir=""):
  pwd = os.getcwd()
  if dir <> "":
    lst = pwd.split('/')
    count = len(lst)-3
    string = ""
    for i in range(count):
      string = string + lst[i] + "/"
    pwd = string + dir
  return pwd

def get_setting(get_setting = ""):
  get_setting_logger = logging.getLogger("Main.functions.get_setting")
  if get_setting <> "":
    config = configparser.ConfigParser()
    pwd = get_pwd("conf")
    config.read(pwd + "/settings.ini")
    try:
      setting = config.get("Settings",get_setting)
    except:
      get_setting_logger.warning("No option '%s' in section: 'Settings'" % (get_setting))
      return ""
    return setting
  else:
    return ""


def init_tracker(stream, tensor, move, length, hight, speed_coef):
  print "[INFO]     Start init"
  flag = True
  frame_count = 0
  x1 = 0
  x2 = 0
  while flag:
    image_np = stream.read()
    image_np = cv2.resize(image_np, (length,hight))
    tensor.set_image(image_np)
    
    scores = tensor.read_scores()
    image_np = tensor.read()
    classes = tensor.read_classes()
    boxes = tensor.read_boxes()
    
    if image_np is not None:
      scores[scores > 0] = 1
      
      classes = classes*scores

      persons = np.where(classes == 1)[1]

      if (str(persons) <> '[]'):
        classes = tensor.read_classes()
        #print (persons_num, ': found person')
        person = persons[0]
        l_w = [hight,length,hight,length]
        box = boxes[0][person]
        #print box 

        if (box[1] > 0.05 and box[3] < 0.95):
          frame_count = frame_count + 1
          x1 = x1 + box[1]
          x2 = x2 + box[3]
        else:
          frame_count = 0
          x1 = 0
          x2 = 0

        if frame_count >= 50:
          percent = round((x2/50 - x1/50) *100)
          print percent
          return 0




