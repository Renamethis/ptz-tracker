# Class for utility functions
import os
import configparser
import numpy as np
import logging
import cv2


def get_pwd(dir=""):
    pwd = os.getcwd()
    if dir != "":
        lst = pwd.split('/')
        string = ""
        for i in lst:
            string = string + i + "/"
            if(i == 'ptz-tracker'):
                break
        pwd = string + dir
    return pwd


def get_setting(section, setting):
    logger = logging.getLogger("Main.functions.readcfg")
    if setting:
        config = configparser.ConfigParser()
        pwd = os.getcwd()
        config.read(pwd + "/settings.ini")
        try:
            setting = config.get(section, setting)
        except:
            logger.warning("No option '%s' in section: 'Settings'" % (setting))
            return ""
        return setting
    else:
        return None


def init_tracker(stream, tensor, move, length, hight, speed_coef):
    print("[INFO]         Start init")
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

            persons = max(np.where(classes == 1)[1])

            if (str(persons) != '[]'):
                classes = tensor.read_classes()
                person = persons[0]
                box = boxes[0][person]
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
                    print(percent)
                    flag = False

    return speed_coef*(1.1-move.get_zoom())*0.8
