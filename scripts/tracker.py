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
from classes.MoveBase import MoveBase
from classes.MoveSet import MoveSet
from classes.centroidTracker import CentroidTracker
from classes.Ping import Ping
import configparser
from enum import Enum, auto
from datetime import datetime
from time import sleep


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
        self.__amount_person = 0
        pwd = os.getcwd()
        self.wsdl_path = pwd + '/wsdl'
        config_path = pwd + '/settings.ini'
        # Initializing loger
        self.__logger = logging.getLogger("Main")
        self.__logger.setLevel(logging.INFO)
        fh = logging.FileHandler(pwd+"/main.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - '
                                      + '%(levelname)s - %(message)s')
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
        while self.running:
            if(self.__ping.read() != 0):
                self.__logger.error("Camera connection is lost or unstable")
                if(self.mode == Mode.Tracking):
                    mode = self.__move
                elif(self.mode == Mode.AutoSet):
                    mode = self.__moveset
                mode.stop()
                self.__stream.stop()
                while(self.__ping.read() != 0):
                    sleep(5)
                mode.start()
                self.__stream.start(mode.get_rtsp())
                self.__logger.info("Camera connection restored")
            else:
                self.__move.pause = self.__moveset.pause = False
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
                        score = np.where(scores > 0.5)
                        if (len(scores[score]) != 0):
                            box = boxes[score]
                            self.__amount_person = len(box)
                            box = (self.l_h*box)
                            box = self.__to_int(box)
                            objects = self.__centroidTracker.update(box)
                            found_box = None
                            if(len(objects) != 0):
                                centroid = objects[min(objects.keys())]
                                for b in box:
                                    cX = int((b[0] + b[2]) / 2.0)
                                    cY = int((b[1] + b[3]) / 2.0)
                                    if(cX == centroid[0] and cY == centroid[1]):
                                        found_box = b
                                        break
                                if(self.mode == Mode.Tracking):
                                    self.__move.set_box(found_box)
                                    self.status = Status.Aimed if \
                                        self.__move.isAimed else Status.Moving
                                elif(self.mode == Mode.AutoSet):
                                    self.status = Status.Moving
                                    self.__moveset.set_box(found_box,
                                                           self.__get_contours(img))
                        else:
                            self.__amount_person = 0
                            self.status = Status.NoPerson
                            self.__move.set_box(None)
                            self.__moveset.set_box(None, None)
            self.running = self.__stream.running and self.__tensor.running and \
                ((self.mode == Mode.Tracking and self.__move.running)
                    or (self.mode == Mode.AutoSet and self.__moveset.running))

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
        self.__ping.start()
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
        self.__ping.start()
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
            del self.__ping
            self.__logger.info("Data updated")
        except AttributeError:
            pass
        self.__centroidTracker = CentroidTracker()
        self.__move = MoveBase(ip, port, login, password, self.wsdl_path,
                               [self.height, self.width], speed, tweaking,
                               bounds, tracking_box, isAbsolute)
        self.__moveset = MoveSet(ip, port, login, password, self.wsdl_path,
                                 [self.height, self.width], speed, self.scope,
                                 tracking_box)
        self.__stream = VideoStream(device=device)
        self.__ping = Ping(ip)

    def __to_int(self, boxes):
        res = []
        for box in boxes:
            res.append([int(p) for p in box])
        return res

    # Return status log
    def get_status_log(self):
        log = self.__status_log
        self.__status_log = {}
        self.__old_status = None
        return log

    # Status logging thread
    def __status_log_thread(self):
        self.__old_status = None
        self.__status_log = {}
        while self.running:
            now = datetime.now()
            if(self.__old_status != self.status):
                date = now.strftime('%Y-%m-%d %H:%M:%S')
                self.__status_log[date] = {'status': str(self.status).split('.')[1],
                                           'amount': self.__amount_person}
                self.__old_status = self.status
            sleep(5)
