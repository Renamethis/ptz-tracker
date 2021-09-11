# Main tracker script

# Starting the virtual environment
import os
import sys
pwd = os.getcwd()
sys.path.append(pwd)
import numpy as np
import cv2
import logging
from classes.VideoStream import VideoStream
from classes.Tensor import Tensor
from classes.Move import Move
import configparser


# Create log file
pwd = os.getcwd()
wsdl_path = pwd + '/wsdl'
logger = logging.getLogger("Main")
logger.setLevel(logging.INFO)
fh = logging.FileHandler(pwd+"/main.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
Config = configparser.ConfigParser()
Config.read(pwd + '/settings.ini')


def __get_setting(section, setting):
    try:
        return Config.get(section, setting)
    except configparser.NoOptionError:
        logger.critical("Option " + setting + " not found in section "
                             + section)
        sys.exit(1)
    except configparser.NoSectionError:
        logger.critical("Section " + section + " not found")
        sys.exit(1)


# Get parameters from settings
ip = __get_setting("Onvif", "ip")
port = __get_setting("Onvif", "port")
login = __get_setting("Onvif", "login")
password = __get_setting("Onvif", "password")
speed_coef = float(__get_setting("Onvif", "speed"))
tweaking = float(__get_setting("Onvif", "tweaking"))/100.0
bounds = [float(i) for i in __get_setting("Processing", "bounds")
          .replace(" ", "").split(",")]
isAbsolute = bool(__get_setting("Onvif", "Absolute"))
length = int(__get_setting("Processing", "width"))
hight = int(__get_setting("Processing", "height"))
l_h = [hight, length, hight, length]
tracking_box = (np.array([float(i) for i in __get_setting("Processing", "box")
                         .replace(" ", "").split(",")]) * l_h).astype(int)
# Initializing main classes
tensor = Tensor(hight=hight, length=length)
move = Move(length, hight, speed_coef, ip, port, login,
            password, wsdl_path, tweaking, bounds, tracking_box, isAbsolute)
stream = VideoStream(Jetson=(1 if (__get_setting(
                               "Hardware", "device") == 'Jetson') else 0))

# Starting all threads

tensor.start()
move.start()
stream.start(move.get_rtsp())

# Opencv object tracking tracking init

#tracker = cv2.TrackerCSRT_create()
#isTracking = False

# Main loop

next_time = 0
box_shape = None
while move.running and stream.running and tensor.running:
    img = stream.read()
    if img is not None:
        img = cv2.resize(img, (length, hight))
        frame = img
        tensor.set_image(img)
        if tensor.flag: #and not isTracking:
            scores = tensor.read_scores().numpy()
            boxes = tensor.read_boxes().numpy()
            if (scores is not None and boxes is not None):
                score = np.where(scores == np.max(scores))
                #print(np.max(scores))
                if (scores[score][0] > 0.5):
                    box = boxes[score][0]
                    box = (l_h*box)
                    move.set_box(box)
                    #tracking_box = [box[1], box[0], box[3], box[2]]
                    #img = img[int(box[0]):int(box[2]), int(box[1]):int(box[3])]
                    #tracker.init(frame, box)
                    #isTracking = True
                else:
                    move.set_box(None)
'''
        elif isTracking:
            (success, box) = tracker.update(frame)
            print(success)
            if(success):
               # box = (l_h*box).astype(int)
                #print(np.asarray(box))
                img = img[int(box[0]):int(box[2]), int(box[1]):int(box[3])]
                #box = [box[1], box[0], box[3], box[2]]
                move.set_box(np.asarray(box))
            else:
                move.set_box(None)
                isTracking = False
'''
stream.stop()
tensor.stop()
move.stop()
