# AutoSet script

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
from classes.MoveSet import MoveSet
import configparser


wsdl_path = pwd + '/wsdl'
logger = logging.getLogger("Main")
logger.setLevel(logging.INFO)
fh = logging.FileHandler(pwd+"/main.log")
Config = configparser.ConfigParser()
Config.read(pwd + '/settings.ini')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


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
isAbsolute = bool(__get_setting("Onvif", "Absolute"))
length = int(__get_setting("Processing", "width"))
hight = int(__get_setting("Processing", "height"))
l_h = [hight, length, hight, length]
tracking_box = (np.array([float(i) for i in __get_setting("Processing", "box")
                         .replace(" ", "").split(",")]) * l_h).astype(int)
limits = (np.array([float(i) for i in __get_setting("AutoSet", "scope")
                    .replace(" ", "").split(",")]) * l_h).astype(int)
COLOR_LIGHT = np.array([int(i) for i in __get_setting("AutoSet", "color_light")
                       .replace(" ", "").split(",")])
COLOR_DARK = np.array([int(i) for i in __get_setting("AutoSet", "color_dark")
                      .replace(" ", "").split(",")])
# Initializing main classes
tensor = Tensor(hight=hight, length=length)
move = MoveSet(speed_coef, ip, port, login, password, wsdl_path,
               [hight, length], limits, tracking_box)
stream = VideoStream(Jetson=(1 if (__get_setting(
                               "Hardware", "device") == 'Jetson') else 0))
RIGHT = limits[2]
LEFT = limits[0]
BOTTOM = limits[1]


# Check pixels function
def check(pixel):
    if(pixel[1] >= RIGHT or pixel[1] <= LEFT or pixel[0] <= BOTTOM):
        return True
    return False


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
while move.running:
    img = stream.read()
    if img is not None:
        img = cv2.resize(img, (length, hight))
        frame = img
        tensor.set_image(img)
        if tensor.flag: #and not isTracking:
            scores = tensor.read_scores().numpy()
            classes = tensor.read_classes().numpy()
            boxes = tensor.read_boxes().numpy()
            if (scores is not None and classes is not None and boxes is not None):
                score = np.where(scores == np.max(scores))
                if (scores[score][0] > 0.6):
                    image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    img = 0*np.zeros((hight, length), dtype=np.uint8)
                    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
                    mask = cv2.inRange(hsv, COLOR_DARK, COLOR_LIGHT)
                    mask = cv2.bitwise_not(mask)
                    pixels = np.argwhere(mask == 255)
                    pixels = pixels[np.array(list(map(check, pixels)))]
                    for pixel in pixels:
                        img[pixel[0]][pixel[1]] = 255
                    _, contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    box = boxes[score][0]
                    box = (l_h*box)
                    move.set_con(contours)
                    move.set_box(box)
                else:
                    move.set_box(None)
stream.stop()
tensor.stop()
move.stop()
