import os
import sys
import smtplib
import base64
from time import sleep
from threading import Thread
import configparser
import logging

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


