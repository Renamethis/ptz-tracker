# Main tracker script

# Loading the libraries and classes
import os
import sys
import numpy as np
import cv2
import logging
from threading import Thread
from classes.VideoStream import VideoStream
from classes.Tensor import Tensor
from classes.Move import Move
from classes.MoveSet import MoveSet
from classes.centroidTracker import CentroidTracker
import configparser
from enum import Enum, auto
from datetime import datetime
import time


class Mode(Enum):
    Tracking = auto()
    AutoSet = auto()


class Status(Enum):
    Starting = auto()
    Moving = auto()
    NoPerson = auto()
    Aimed = auto()
    Stopped = auto()


class Tracker:
    # Init function
    def __init__(self):
        # Initializing variables
        self.name = "MAIN"
        self.running = False
        self.status = Status.Stopped
        pwd = os.getcwd()
        self.wsdl_path = pwd + '/wsdl'
        config_path = pwd + '/settings.ini'
        # Initializing loger
        self.__logger = logging.getLogger("Main")
        self.__logger.setLevel(logging.INFO)
        fh = logging.FileHandler(pwd+"/main.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - ' +
                                      '%(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.__logger.addHandler(fh)
        # Initializing configparser
        self.Config = configparser.ConfigParser()
        self.Config.read(config_path)
        # Get parameters from settings
        self.update_data()
        self.__tensor = Tensor()

    def __get_setting(self, section, setting):
        try:
            return self.Config.get(section, setting)
        except configparser.NoOptionError:
            self.__logger.critical("Option " + setting + " not found in section "
                                 + section)
            sys.exit(1)
        except configparser.NoSectionError:
            self.__logger.critical("Section " + section + " not found")
            sys.exit(2)

    # Main loop function
    def __update(self):
        self.__logger.info("Tracker started")
        time.sleep(10)
        while self.running:
            img = self.__stream.read()
            if img is not None:
                img = cv2.resize(img, (self.width, self.height))
                self.__tensor.set_image(img)
                if self.__tensor.flag:
                    scores = self.__tensor.read_scores()
                    boxes = self.__tensor.read_boxes()
                    if (scores is not None and boxes is not None):
                        scores = scores.numpy()
                        boxes = boxes.numpy()
                        score = np.where(scores > 0.55)
                        #print(scores)
                        if (len(scores[score]) != 0):
                            box = boxes[score]
                            box = (self.l_h*box)
                            box = self.__to_int(box)
                            #print(box)
                            objects = self.__centroidTracker.update(box)
                            if(len(objects) != 0):
                                k = 0
                                flag = False
                                for (id, cent) in objects.items():
                                    if(id == 0):
                                        flag = True
                                        break
                                    k += 1
                                if(flag):
                                    box = box[k]
                                else:
                                    box = None
                                if(self.mode == Mode.Tracking):
                                    self.__move.set_box(box)
                                    self.status = Status.Aimed if \
                                        self.__move.isAimed else Status.Moving
                                elif(self.mode == Mode.AutoSet):
                                    self.status = Status.Moving
                                    self.__moveset.set_box(box)
                                    self.__moveset.set_con(self.__get_contours(img))
                        else:
                            self.status = Status.NoPerson
                            self.__move.set_box(None)
                            self.__moveset.set_box(None)
            self.running = self.__stream.running and self.__tensor.running and \
                ((self.mode == Mode.Tracking and self.__move.running) or
                    (self.mode == Mode.AutoSet and self.__moveset.running))
        self.__logger.info("Tracker stopped")

    # Start tracker function
    def start_tracker(self):
        self.status = Status.Starting
        self.__logger.info("Tracker starting...")
        if(not self.__move.start()):
            return self.__move.running
        self.running = True
        self.__status_log_thread = Thread(target=self.__status_log_thread,
                                          name="status_log")
        self.__status_log_thread.start()
        self.__stream.start(self.__move.get_rtsp())
        self.__tensor.start()
        self.mode = Mode.Tracking
        self.main = Thread(target=self.__update, name=self.name)
        self.main.start()
        return self.running and self.__move.running and \
            self.__stream.running and self.__tensor.running

    # Start autoset function
    def start_autoset(self):
        self.status = Status.Starting
        self.__logger.info("Tracker starting...")
        if(not self.__moveset.start()):
            return self.__moveset.running
        self.running = True
        self.__stream.start(self.__moveset.get_rtsp())
        self.__tensor.start()
        self.mode = Mode.AutoSet
        self.main = Thread(target=self.__update, name=self.name)
        self.main.start()
        return self.running and self.__moveset.running and \
            self.__stream.running and self.__tensor.running

    # Stop function
    def stop(self):
        self.__stream.stop()
        self.__tensor.stop()
        if(self.mode == Mode.Tracking):
            self.__move.stop()
        elif(self.mode == Mode.AutoSet):
            self.__moveset.stop()
        self.status = Status.Stopped

    # Pixels coordinates checking function
    def __check(self, pixel):
        if(pixel[1] >= self.scope[2] or pixel[1] <= self.scope[0]
           or pixel[0] <= self.scope[1]):
            return True
        return False

    # Find contours on greenscreen
    def __get_contours(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        img = 0*np.zeros((self.height, self.width), dtype=np.uint8)
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(hsv, self.COLOR_DARK, self.COLOR_LIGHT)
        mask = cv2.bitwise_not(mask)
        pixels = np.argwhere(mask == 255)
        pixels = pixels[np.array(list(map(self.__check, pixels)))]
        for pixel in pixels:
            img[pixel[0]][pixel[1]] = 255
        _, contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE,
                                                  cv2.CHAIN_APPROX_SIMPLE)
        return contours

    # Updating parameters from config
    def update_data(self):
        # ONVIF settings
        ip = self.__get_setting("Onvif", "ip")
        port = self.__get_setting("Onvif", "port")
        login = self.__get_setting("Onvif", "login")
        password = self.__get_setting("Onvif", "password")
        speed = float(self.__get_setting("Onvif", "speed"))
        tweaking = float(self.__get_setting("Onvif", "tweaking")) / 100.0
        isAbsolute = bool(self.__get_setting("Onvif", "Absolute"))
        # Image processing settings
        bounds = [float(i) for i in self.__get_setting("Processing", "bounds")
                                        .replace(" ", "").split(",")]
        self.width = int(self.__get_setting("Processing", "width"))
        self.height = int(self.__get_setting("Processing", "height"))
        self.l_h = [self.height, self.width, self.height, self.width]
        tracking_box = (np.array([float(i) for i in self.__get_setting(
            "Processing", "box").replace(" ", "")
                .split(",")]) * self.l_h).astype(int)
        # AutoSet settings
        self.COLOR_LIGHT = np.array([int(i) for i in self.
                                     __get_setting("AutoSet", "color_light")
                                    .replace(" ", "").split(",")])
        self.COLOR_DARK = np.array([int(i) for i in self.
                                    __get_setting("AutoSet", "color_dark")
                                   .replace(" ", "").split(",")])
        self.scope = (np.array([float(i) for i in
                               self.__get_setting("AutoSet", "scope").
                               replace(" ",
                                       "").split(",")]) * self.l_h).astype(int)
        # Hardware settings
        device = self.__get_setting("Hardware", "device")
        try:
            del self.__move
            del self.__moveset
            del self.__stream
            self.__logger.info("Data updated")
        except AttributeError:
            pass
        self.__centroidTracker = CentroidTracker()
        self.__move = Move(self.width, self.height, speed, ip, port,
                           login, password, self.wsdl_path, tweaking, bounds,
                           tracking_box, isAbsolute)
        self.__moveset = MoveSet(speed, ip, port, login, password,
                                 self.wsdl_path, [self.height, self.width],
                                 self.scope, tracking_box)
        self.__stream = VideoStream(device=device)

    def __to_int(self, boxes):
        res = []
        for box in boxes:
            buf = []
            for point in box:
                buf.append(int(point))
            res.append(buf)
        return res
    # Return status log
    def get_status_log(self):
        return self.__status_log

    # Status logging thread
    def __status_log_thread(self):
        old_status = None
        self.__status_log = {}
        while self.running:
            now = datetime.now()
            if(old_status != self.status):
                date = now.strftime('%Y-%m-%d %H:%M:%S')
                self.__status_log[date] = str(self.status).split('.')[1]
                old_status = self.status
            if(now.minute % 15 == 0):
                self.__status_log = {}
                old_status = None
            time.sleep(10)
