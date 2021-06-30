import sys
from threading import Thread
from onvif import ONVIFCamera
import traceback
from time import sleep
import numpy as np
import logging
from zmqgrabber import message_grabber
from OnvifInteraction import Camera
################################
# 3. The process of taking a frame from a stream
################################


class Move:
    # 3.1. Initialization
    def __init__(self, length, hight, speed_coef, ip, port, login, password, wsdl, tweaking, bounds, name="Move"):
        self.name = name
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
        self.__ddelay = 0.5
        self.logger = logging.getLogger("Main.%s" % (self.name))
        self.cam = Camera(ip, port, login, password, wsdl)

    # 3.2. Start thread
    def start(self):
        self.stopped = False
        self.logger.info("Process starting")
        self.t = Thread(target=self.update, name=self.name, args=())
        self.t.daemon = True
        self.t.start()
        self.mt = message_grabber("tcp://*:5555")
        self.mt.start()
        return self

    # 3.3. Infinite loop of receiving frames from a stream
    def update(self):
        self.logger.info("Process started")
        while True:
            message = self.mt.get_message()
            if(message is not None):
                translation = self.mt.get_translation()
                rotation = self.mt.get_rotation()
            if self.pause:
                self.ptz.Stop({'ProfileToken': self.token})
                sleep(self.__ddelay)
            if self.stopped:
                return
            box = self.box
            old_box = self.old_box
            if np.array_equal(box, old_box):
                sleep(self.__ddelay)
            elif box is not None:
                to_x = int(abs(box[1] - box[3])/2.0 + box[1])
                to_y = int(box[0])
                if (to_x < self.length/3 - 40 or to_x > self.length/3 + 40):
                    if to_x > self.length/3:
                        vec_x = float(to_x - self.length/3)/(self.length)
                    else:
                        vec_x = float(to_x - self.length/3)/(self.length)*2
                else:
                    vec_x = 0
                if (to_y < self.hight/5 - 40 or to_y > self.hight/5 + 40):
                    vec_y = float(self.hight/5 - to_y)/(self.hight)
                else:
                    vec_y = 0
                self.count_frame = 0
                vec_x = vec_x*self.speed_coef
                vec_y = vec_y*self.speed_coef
                if vec_x > 1:
                    vec_x = 1
                if vec_y > 1:
                    vec_y = 1
                if(vec_y < 0.05 and vec_x < 0.05):
                    self.cam.stop()
                else:
                    self.logger.info('X: ' + str(vec_x)
                                     + ' Y: ' + str(vec_y))
                    self.cam.move(vec_x, vec_y)
                old_box = box

            elif box is None and old_box is not None:
                if (self.count_frame < 20):
                    self.cam.move(vec_x, vec_y)
                if (self.count_frame == 20):
                    self.cam.stop()
                    sleep(self.__ddelay)
                if (self.count_frame == 60):
                    self.count_frame = 0
                    self.cam.goHome()
                    old_box = box
                    sleep(self.__ddelay)
                if(not (rotation[0] > self.bounds[0] and rotation[0]
                        < self.bounds[2] and rotation[1] > self.bounds[1]
                        and rotation[1] < self.bounds[3])):
                    self.cam.stop()
                sleep(self.tweaking)
                self.count_frame = self.count_frame + 1
            self.old_box = old_box

    def set_box(self, box):
        self.box = box

    def set_speed_coef(self, speed_coef):
        self.speed_coef = speed_coef

    def stop(self):
        self.stopped = True
