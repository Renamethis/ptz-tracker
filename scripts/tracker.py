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
import configparser
from enum import Enum, auto


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
        # Injtializing variables
        self.name = "MAIN"
        self.running = False
        self.status = Status.Stopped
        pwd = os.getcwd()
        wsdl_path = pwd + '/wsdl'
        config_path = pwd + '/settings.ini'
        # Initializing loger
        self.logger = logging.getLogger("Main")
        self.logger.setLevel(logging.INFO)
        fh = logging.FileHandler(pwd+"/main.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - ' +
                                      '%(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        # Initializing configparser
        self.Config = configparser.ConfigParser()
        self.Config.read(config_path)
        # Get parameters from settings
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
        # Initializing classes
        self.tensor = Tensor(self.height, self.width)
        self.move = Move(self.width, self.height, speed, ip, port,
                         login, password, wsdl_path, tweaking,
                         tracking_box, isAbsolute, bounds)
        self.moveset = MoveSet(speed, ip, port, login, password, wsdl_path,
                               [self.height, self.width],
                               self.scope, tracking_box)
        self.stream = VideoStream(device)

    def __get_setting(self, section, setting):
        try:
            return self.Config.get(section, setting)
        except configparser.NoOptionError:
            self.logger.critical("Option " + setting + " not found in section "
                                 + section)
            sys.exit(1)
        except configparser.NoSectionError:
            self.logger.critical("Section " + section + " not found")
            sys.exit(2)

    # Main loop function
    def update(self):
        self.logger.info("Tracker started")
        while self.running:
            img = self.stream.read()
            if img is not None:
                img = cv2.resize(img, (self.width, self.height))
                self.tensor.set_image(img)
                if self.tensor.flag:
                    scores = self.tensor.read_scores()
                    boxes = self.tensor.read_boxes()
                    if (scores is not None and boxes is not None):
                        scores = scores.numpy()
                        boxes = boxes.numpy()
                        score = np.where(scores == np.max(scores))
                        if (scores[score][0] > 0.5):
                            box = boxes[score][0]
                            box = (self.l_h*box)
                            if(self.mode == Mode.Tracking):
                                self.move.set_box(box)
                                self.status = Status.Aimed if \
                                    self.move.isAimed else Status.Moving
                            elif(self.mode == Mode.AutoSet):
                                self.status = Status.Moving
                                self.moveset.set_box(box)
                                self.moveset.set_con(self.__get_contours(img))
                        else:
                            self.status = Status.NoPerson
                            self.move.set_box(None)
                            self.moveset.set_box(None)
            self.running = self.stream.running and self.tensor.running and \
                ((self.mode == Mode.Tracking and self.move.running) or
                    (self.mode == Mode.AutoSet and self.moveset.running))
        self.logger.info("Tracker stopped")

    # Start tracker function
    def start_tracker(self):
        self.status = Status.Starting
        self.logger.info("Tracker starting...")
        if(not self.move.start()):
            return self.move.running
        self.running = True
        self.stream.start(self.move.get_rtsp())
        self.tensor.start()
        self.mode = Mode.Tracking
        self.main = Thread(target=self.update, name=self.name)
        self.main.start()
        return self.running and self.move.running and \
            self.stream.running and self.tensor.running

    # Start autoset function
    def start_autoset(self):
        self.status = Status.Starting
        self.logger.info("Tracker starting...")
        if(not self.moveset.start()):
            return self.moveset.running
        self.running = True
        self.stream.start(self.moveset.get_rtsp())
        self.tensor.start()
        self.mode = Mode.AutoSet
        self.main = Thread(target=self.update, name=self.name)
        self.main.start()
        return self.running and self.moveset.running and \
            self.stream.running and self.tensor.running

    # Stop function
    def stop(self):
        self.stream.stop()
        self.tensor.stop()
        if(self.mode == Mode.Tracking):
            self.move.stop()
        elif(self.mode == Mode.AutoSet):
            self.moveset.stop()
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
