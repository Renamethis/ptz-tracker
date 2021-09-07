import numpy as np
from enum import Flag, auto
from OnvifInteraction import Camera
from threading import Thread
import logging


class Position(Flag):
    NO = 0
    RIGHT = auto()
    LEFT = auto()
    TOP = auto()


class MoveSet:
    contours = None
    box = None

    def __init__(self, speed, ip, port, login, password, wsdl, Shape,
                 Colors, Bounds, tracking_box):
        self.name = "MoveSet"
        self.LIGHT_GREEN = Colors[0]
        self.DARK_GREEN = Colors[1]
        self.LEFT = Bounds[0]
        self.BOT = Bounds[1]
        self.RIGHT = Bounds[2]
        self.UP = Bounds[3]
        self.WIDTH = Shape[1]
        self.HEIGHT = Shape[0]
        self.isProcessing = True
        self.cam = Camera(ip, port, login, password, wsdl)
        self.tbox = tracking_box
        self.speed_coef = speed
        self.logger = logging.getLogger("Main.%s" % (self.name))

    def start(self):
        self.logger.info("Process starting")
        self.thread = Thread(target=self.process, name=self.name, args=())
        self.thread.daemon = True
        self.thread.start()

    def process(self):
        self.logger.info("Process started")
        while self.isProcessing:
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
                if(vec_x == 0 and vec_y == 0):
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
                    print(pos)
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
                        self.isProcessing = False
                    if(pos != Position.NO):
                        self.logger.info("Object found on" + str(pos))
                else:
                    self.cam.ContinuousMove(vec_x, vec_y)
            else:
                self.cam.stop()

    def set_con(self, contours):
        self.contours = contours

    def set_image(self, image):
        self.image = image

    def set_box(self, box):
        self.box = box

    def stop(self):
        self.isProcessing = False
