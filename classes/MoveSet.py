# Camera control class for autoset
import numpy as np
from enum import Flag, auto
from classes.OnvifInteraction import Camera
from threading import Thread
import logging
import time


# Enum class for object positions on greenscreen
class Position(Flag):
    NO = 0
    RIGHT = auto()
    LEFT = auto()
    TOP = auto()


TOTALFRAMES = 100


class MoveSet:
    contours = None
    box = None

    # Initialization
    def __init__(self, speed, ip, port, login, password, wsdl, Shape,
                 Bounds, tracking_box):
        self.name = "MoveSet"
        self.ip = ip
        self.port = port
        self.login = login
        self.password = password
        self.wsdl = wsdl
        self.LEFT = Bounds[0]
        self.BOT = Bounds[1]
        self.RIGHT = Bounds[2]
        self.UP = Bounds[3]
        self.WIDTH = Shape[1]
        self.HEIGHT = Shape[0]
        self.tbox = tracking_box
        self.speed_coef = speed
        self.__logger = logging.getLogger("Main.%s" % (self.name))
        self.frames = 0

    # Start threads
    def start(self):
        self.__logger.info("Process starting")
        self.cam = Camera(self.ip, self.port, self.login, self.password,
                          self.wsdl, True)
        if(not self.cam.connect()):
            return False
        self.cam.start()
        self.running = True
        self.__thread = Thread(target=self.__update, name=self.name, args=())
        self.__thread.daemon = True
        self.__thread.start()
        return True

    # Main loop
    def __update(self):
        self.__logger.info("Process started")
        time.sleep(5)
        while self.running:
            if(self.box is not None and self.contours is not None):
                box = self.box
                to_x = int(abs(box[1] - box[3])/2.0 + box[1])
                to_y = int(box[0])
                if (to_x < self.tbox[0] or to_x > self.tbox[2]):
                    if to_x < self.tbox[0]:
                        vec_x = float(to_x - self.tbox[0])/(self.WIDTH)
                    else:
                        vec_x = float(to_x - self.tbox[2])/(self.WIDTH)
                else:
                    vec_x = 0
                if (to_y > self.tbox[1] + 40 or to_y < self.tbox[1] - 40):
                    vec_y = float(self.tbox[1] - to_y)/(self.HEIGHT)
                else:
                    vec_y = 0
                vec_x = vec_x*self.speed_coef
                vec_y = vec_y*self.speed_coef
                vec_x = 1 if vec_x > 1 else vec_x
                vec_y = 1 if vec_x > 1 else vec_y
                if(abs(vec_y) < 0.03 and abs(vec_x) < 0.03):
                    vec_x = 0
                    vec_y = 0
                    self.cam.stop()
                if(vec_x == 0 and vec_y == 0 and self.frames != TOTALFRAMES):
                    self.frames += 1
                elif(vec_x == 0 and vec_y == 0):
                    pos = Position.NO
                    for con in self.contours:
                        pointsx = con[:, 0, 1]
                        pointsy = con[:, 0, 0]
                        medx = int(np.median(pointsx))
                        medy = int(np.median(pointsy))
                        if(medy > self.UP):
                            pos = pos | Position.NO
                        elif(medx > 2*self.WIDTH/3 + 50):
                            pos = pos | Position.RIGHT
                        elif(medx < self.WIDTH/3 - 50):
                            pos = pos | Position.LEFT
                        elif(medy < self.BOT):
                            pos = pos | Position.TOP
                    if(pos == Position.LEFT | Position.RIGHT or
                       pos == Position.LEFT | Position.RIGHT | Position.TOP):
                        self.cam.ContinuousMove(0, 0, self.speed_coef*0.1)
                    elif(pos == Position.RIGHT):
                        self.cam.ContinuousMove(-self.speed_coef * 0.2, 0)
                    elif(pos == Position.LEFT):
                        self.cam.ContinuousMove(-self.speed_coef * 0.2, 0)
                    elif(pos == Position.TOP):
                        self.cam.ContinuousMove(0, -self.speed_coef * 0.2)
                    else:
                        self.cam.ContinuousMove(0, 0)
                        self.cam.stop()
                        self.running = False
                    if(pos != Position.NO):
                        self.__logger.info("Object found on" + str(pos))
                else:
                    self.frames = 0
                    self.cam.ContinuousMove(vec_x, vec_y)
            else:
                self.cam.stop()
        self.__logger.info("Process stopped")

    # Set greenscreen contours
    def set_con(self, contours):
        self.contours = contours

    # Set person box
    def set_box(self, box):
        self.box = box

    # Stop threads
    def stop(self):
        self.cam.stop_thread()
        self.running = False

    # Return rtsp_url from Camera object
    def get_rtsp(self):
        return "rtsp://" + self.login + ":" + self.password + "@" + \
                   self.cam.getStreamUri().split('//')[1]
