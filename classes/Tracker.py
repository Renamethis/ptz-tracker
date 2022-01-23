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
from classes.CentroidTracker import CentroidTracker
from classes.Ping import Ping
import configparser
from enum import Enum, auto
from datetime import datetime
from time import sleep
from random import randint
from paho.mqtt import client as mqtt_client
from json import dumps


class Mode(Enum):
    Tracking = auto()
    AutoSet = auto()
    Assistant = auto()


class Status(Enum):
    Starting = auto()
    Waiting = auto()
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
        self.config_path = pwd + '/settings.ini'
        # Initializing logger
        self.__logger = logging.getLogger("Main")
        self.__logger.setLevel(logging.INFO)
        fh = logging.FileHandler(pwd+"/main.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - '
                                      + '%(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.__logger.addHandler(fh)
        # Initialize tensor class
        self.__tensor = Tensor()
        self.__status_log = None
        self.__person_id = None
        self.__persons = {}

    # Main loop function
    def __update(self):
        self.__logger.info("Tracker started")
        while self.running:
            # Check connection to camera, if it falls - reinitialize tracker
            # classes
            if(self.__move_type != Mode.AutoSet and \
               self.__ping.read() and self.__ping.read() is not None):
                self.__logger.error("Camera connection is lost or unstable")
                self.__stream.stop()
                self.__move_mode.stop()
                while(self.__ping.read() != 0):
                    sleep(1)
                self.__ping.stop()
                self.update_data()
                self.__move_mode = self.__move
                self.__move_mode.start()
                self.__stream.start(self.__move_mode.get_rtsp())
                self.__ping.start()
                self.__logger.info("Camera connection restored")
            # Read images from stream
            img = self.__stream.read()
            if img is not None:
                img = cv2.resize(img, (self.width, self.height))
                # Pass image in tensor class and get scores and boxes
                self.__tensor.set_image(img)
                if self.__tensor.flag:
                    scores = self.__tensor.read_scores()
                    boxes = self.__tensor.read_boxes()
                    if (scores is not None and boxes is not None):
                        scores = scores.numpy()
                        boxes = boxes.numpy()
                        score = np.where(scores > 0.5)
                        # Convert boxes and pass it to CentroidTracker
                        if (len(scores[score]) != 0):
                            boxes = boxes[score]
                            self.__amount_person = len(boxes)
                            lbox = self.__to_int(self.l_h*boxes)
                            objects = self.__centroidTracker.update(lbox)
                            # Creating id: box dict
                            boxes_dict = {}
                            for b in range(0, len(boxes)):
                                cX = int((lbox[b][0] + lbox[b][2]) / 2.0)
                                cY = int((lbox[b][1] + lbox[b][3]) / 2.0)
                                for key in objects.keys():
                                    centroid = objects[key]
                                    if(centroid[0] == cX and centroid[1] == cY):
                                        boxes_dict[key] = boxes[b]
                                        break
                            self.__persons = boxes_dict
                            if(self.__move_type == Mode.Tracking
                               or self.__move_type == Mode.AutoSet):
                                # If tracker started as default tracker or
                                # autoset, then choose fist person
                                if(self.__move_type == Mode.Tracking and bool(boxes_dict)):
                                    self.__move_mode.set_box(
                                        boxes_dict[min(boxes_dict.keys())])
                                elif(self.__move_type == Mode.AutoSet):
                                    self.__move_mode.set_box(
                                        boxes_dict[min(boxes_dict.keys())],
                                        self.__get_contours(img))
                                self.status = Status.Aimed if self.__move_mode.isAimed() else Status.Moving
                            elif(self.__move_type == Mode.Assistant):
                                # If tracker started as assistent, then
                                # waiting for the choice of a person or track
                                # the chosen one
                                self.__mqtt_client.publish(self.__mqtt_topic,
                                                           dumps(boxes_dict))
                                if(self.__person_id is not None
                                   and self.__person_id in self.__persons.keys()):
                                    self.status = Status.Aimed if self.__move_mode.isAimed() else Status.Moving
                                    self.__move_mode.set_box(
                                         self.__persons[self.__person_id])
                                else:
                                    self.status = Status.Waiting
                                    self.__move_mode.set_box(None)
                        else:
                            self.__amount_person = 0
                            self.status = Status.NoPerson
                            self.__move_mode.set_box(None) if \
                                self.__move_type == Mode.Tracking \
                                or self.__move_type == Mode.Assistant \
                                else self.__move_mode.set_box(None, None)
            self.running = self.__stream.running and \
                self.__tensor.running and not self.__move_mode.running.is_set()
        self.status = self.status.Stopped
        self.stop()
        self.__logger.info("Tracker stopped")

    # Start assistant function
    def start_assistant(self):
        self.status = Status.Starting
        self.__logger.info("Assistant starting...")
        if(not self.__move.start(isAssistant=True)):
            return False
        self.__move_mode = self.__move
        self.running = True
        self.__mqtt_client = self.__connect_mqtt(self.__mqtt_adress,
                                                 self.__mqtt_user,
                                                 self.__mqtt_password,
                                                 self.__mqtt_port)
        self.__mqtt_client.loop_start()
        self.__move_type = Mode.Assistant
        return self.__start_general()

        # Start tracker function
    def start_tracker(self):
        self.status = Status.Starting
        self.__logger.info("Tracker starting...")
        if(not self.__move.start()):
            return False
        self.__move_mode = self.__move
        self.running = True
        if(self.isLogging):
            self.__status_thread = Thread(target=self.__status_log_thread,
                                          name="status_log")
            self.__status_thread.start()
        self.__move_type = Mode.Tracking
        return self.__start_general()

    # Start autoset function
    def start_autoset(self):
        self.status = Status.Starting
        self.__logger.info("Autoset starting...")
        if(not self.__moveset.start()):
            return not self.__moveset.running.is_set()
        self.__move_mode = self.__moveset
        self.running = True
        self.__move_type = Mode.AutoSet
        return self.__start_general()

    # Stop function
    def stop(self):
        self.__stream.stop()
        self.__tensor.stop()
        self.__move_mode.stop()
        self.__ping.stop()
        self.status = Status.Stopped

    # Updating parameters from config
    def update_data(self):
        # Update/Init configparser
        self.Config = configparser.ConfigParser()
        self.Config.read(self.config_path)
        # ONVIF settings
        ip = self.__get_setting("Onvif", "ip")
        port = self.__get_setting("Onvif", "port")
        login = self.__get_setting("Onvif", "login")
        password = self.__get_setting("Onvif", "password")
        speed = float(self.__get_setting("Onvif", "speed"))
        tweaking = float(self.__get_setting("Onvif", "tweaking")) / 100.0
        isAbsolute = self.__get_setting("Onvif", "absolute") == "True"
        preset = self.__get_setting("Onvif", "preset")
        # Streaming settings
        isGstreamer = self.__get_setting("Streaming", "source") == "GStreamer"
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
        # Assistant settings
        self.__mqtt_adress = self.__get_setting("Assistant", "mqtt_adress")
        self.__mqtt_topic = self.__get_setting("Assistant", "mqtt_topic")
        self.__mqtt_port = int(self.__get_setting("Assistant", "mqtt_port"))
        self.__mqtt_user = self.__get_setting("Assistant", "mqtt_user")
        self.__mqtt_password = self.__get_setting("Assistant", "mqtt_password")
        # AutoRecord settings
        self.isLogging = self.__get_setting("AutoRecord", "logging") == "True"
        self.log_frequency = int(self.__get_setting("AutoRecord", "frequency"))
        # Hardware settings
        device = self.__get_setting("Hardware", "device")
        # Initializing
        try:
            del self.__move
            del self.__moveset
            del self.__stream
            del self.__ping
            self.__logger.info("Configuration updated")
        except AttributeError:
            self.__logger.info("Configuration loaded")
        self.__centroidTracker = CentroidTracker()
        self.__move = MoveBase(ip, port, login, password, self.wsdl_path,
                               [self.height, self.width], speed, tweaking,
                               bounds, tracking_box, isAbsolute, preset)
        self.__moveset = MoveSet(ip, port, login, password, self.wsdl_path,
                                 [self.height, self.width], speed, self.scope,
                                 tracking_box, preset)
        self.__stream = VideoStream(GStreamer=isGstreamer, device=device)

        self.__ping = Ping(ip)

    # Is tracker running as assistant
    def is_assistant(self):
        return self.__move_type == Mode.Assistant

    # Setting person id variable
    def set_track(self, id):
        if(int(id) in self.__persons.keys()):
            self.__person_id = int(id)
            return True
        return False

    # Pixels coordinates checking function
    def __check(self, pixel):
        if(pixel[1] >= self.scope[2] or pixel[1] <= self.scope[0]
           or pixel[0] <= self.scope[1]):
            return True
        return False

    # Start general threads
    def __start_general(self):
        self.status = Status.Starting
        print(self.__move_mode.get_rtsp())
        self.__stream.start(self.__move_mode.get_rtsp())
        self.__tensor.start()
        self.__ping.start()
        self.main = Thread(target=self.__update, name=self.name)
        self.main.start()
        return self.running and not self.__move.running.is_set() and \
            self.__stream.running and self.__tensor.running

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
        contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE,
                                               cv2.CHAIN_APPROX_SIMPLE)
        return contours

    # Connect to mqtt server
    def __connect_mqtt(self, adress, user, password, port):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                self.__logger.info("Connected to MQTT Broker")
            else:
                self.__logger.critical("Failed to connect to MQTT Broker - " + \
                                       str(rc) + " Error")
        # Set Connecting Client ID
        client_id = f'python-mqtt-{randint(0, 1000)}'
        client = mqtt_client.Client(client_id)
        client.username_pw_set(user, password)
        client.on_connect = on_connect
        client.connect(adress, port)
        return client
    # Get setting from config file
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

    # Convert float values in box to int values
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
        delay = self.log_frequency
        while self.running:
            now = datetime.now()
            if(self.__old_status != self.status):
                date = now.strftime('%Y-%m-%d %H:%M:%S')
                self.__status_log[date] = {'status': str(self.status).split('.')[1],
                                           'amount': self.__amount_person}
                self.__old_status = self.status
            sleep(delay)
