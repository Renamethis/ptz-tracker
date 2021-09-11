# Camera controll class
from threading import Thread
from time import sleep
import numpy as np
import logging
from classes.zmqgrabber import message_grabber
from classes.OnvifInteraction import Camera


class Move:
    # Initialization
    def __init__(self, length, hight, speed_coef, ip, port, login, password,
                 wsdl, tweaking, bounds, tracking_box, isAbsolute,
                 name="Move"):
        self.name = name
        self.ip = ip
        self.port = port
        self.login = login
        self.password = password
        self.wsdl = wsdl
        self.box = None
        self.tweaking = tweaking
        self.old_box = None
        self.length = length
        self.hight = hight
        self.old_vec_x = 0
        self.old_vec_y = 0
        self.count_frame = 0
        self.speed_coef = speed_coef
        self.pause = False
        self.bounds = bounds
        self.tbox = tracking_box
        self.__ddelay = 0.1
        self.logger = logging.getLogger("Main.%s" % (self.name))
        self.isAbsolute = isAbsolute
        self.spaceLimits = bounds
        self.isAimed = False

    # Start threads
    def start(self):
        self.cam = Camera(self.ip, self.port, self.login, self.password,
                          self.wsdl, self.isAbsolute)
        self.logger.info("Process starting")
        self.mt = message_grabber("tcp://*:5555")
        self.mt.start()
        self.running = self.cam.running
        self.t = Thread(target=self.update, name=self.name, args=())
        self.t.daemon = True
        self.t.start()
        return self

    # Loop of receiving frames from a stream

    def update(self):
        self.logger.info("Process started")
        while self.running:
            message = self.mt.get_message()
            rotation = self.mt.get_rotation() if message is not None else None
            if self.pause:
                self.cam.stop()
                sleep(self.__ddelay)
            box = self.box
            old_box = self.old_box
            if np.array_equal(box, old_box):
                sleep(self.__ddelay)
            elif box is not None:
                to_x = int(abs(box[1] - box[3])/2.0 + box[1])
                to_y = int(abs(box[0] - box[2])/2.0 + box[0])
                if (to_x < self.tbox[0] or to_x > self.tbox[2]):
                    if to_x < self.tbox[0]:
                        vec_x = float(to_x - self.tbox[0])/(self.length)
                    else:
                        vec_x = float(to_x - self.tbox[2])/(self.length)
                else:
                    vec_x = 0
                if (to_y < self.tbox[1] or to_y > self.tbox[3]):
                    if(to_y < self.tbox[1]):
                        vec_y = float(self.tbox[1] - to_y)/(self.hight)
                    else:
                        vec_y = float(self.tbox[3] - to_y)/(self.hight)
                else:
                    vec_y = 0
                self.count_frame = 0
                vec_x = vec_x*self.speed_coef
                vec_y = vec_y*self.speed_coef
                vec_x = 1 if vec_x > 1 else vec_x
                vec_y = 1 if vec_x > 1 else vec_y
                if(self.isAbsolute or message is not None):
                    point = self.cam.getAbsolute() if self.isAbsolute else rotation
                    if((point[0] < self.spaceLimits[0] and vec_x < 0) or
                       (point[0] > self.spaceLimits[2] and vec_x > 0)):
                        vec_x = 0
                    if(point[1] < self.spaceLimits[1] and vec_y > 0 or
                       (point[1] > self.spaceLimits[3] and vec_y < 0)):
                        vec_y = 0
                if(abs(vec_y) < 0.05 and abs(vec_x) < 0.05):
                    self.isAimed = True
                    self.cam.stop()
                else:
                    # self.logger.info('X: ' + str(vec_x)
                    #                 + ' Y: ' + str(vec_y))
                    self.isAimed = False
                    self.cam.ContinuousMove(vec_x, vec_y)
                old_box = box
            elif box is None and old_box is not None:
                if (self.count_frame < 20):
                    self.cam.ContinuousMove(vec_x, vec_y)
                elif (self.count_frame == 20):
                    self.cam.stop()
                    sleep(self.__ddelay)
                elif (self.count_frame == 60):
                    self.count_frame = 0
                    # self.cam.goHome()
                    old_box = box
                    sleep(self.__ddelay)
                sleep(self.tweaking)
                self.count_frame = self.count_frame + 1
            self.old_box = old_box

    def set_box(self, box):
        self.box = box

    def set_speed_coef(self, speed_coef):
        self.speed_coef = speed_coef

    def stop(self):
        self.cam.stop_thread()
        self.running = False

    def get_rtsp(self):
        return "rtsp://" + self.login + ":" + self.password + "@" + \
                   self.cam.getStreamUri().split('//')[1]
