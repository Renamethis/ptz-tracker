# Camera control class for autoset
from threading import Thread
import numpy as np
from enum import Flag, auto
from classes.Move import Move
import time

# Enum class for object positions on greenscreen


class Position(Flag):
    NO = 0
    RIGHT = auto()
    LEFT = auto()
    TOP = auto()


TOTALFRAMES = 100


class MoveSet(Move):

    # Initialization
    def __init__(self, ip, port, login, password, wsdl, Shape, speed,
                 Bounds, tracking_box, name="Move"):
        super().__init__(ip, port, login, password, wsdl, Shape, speed,
                         tracking_box, False)
        self.LEFT = Bounds[0]
        self.BOT = Bounds[1]
        self.RIGHT = Bounds[2]
        self.UP = Bounds[3]
        self.frames = 0

    # Starting thread
    def start(self):
        self.running = super().start()
        self.__thread = Thread(target=self.__update, name=self._name, args=())
        self.__thread.daemon = True
        self.__thread.start()
        return self.running

    # Main loop
    def __update(self):
        self._logger.info("Process started")
        while self.running:
            if(self.pause):
                self.cam.pause = True
                continue
            if(self._box is not None and self.contours is not None):
                box = self._box
                to_x = int(abs(box[1] - box[3])/2.0 + box[1])
                to_y = int(box[0])
                if (to_x < self.tbox[0] or to_x > self.tbox[2]):
                    if to_x < self.tbox[0]:
                        vec_x = float(to_x - self.tbox[0])/(self._width)
                    else:
                        vec_x = float(to_x - self.tbox[2])/(self._width)
                else:
                    vec_x = 0
                if (to_y > self.tbox[1] + 40 or to_y < self.tbox[1] - 40):
                    vec_y = float(self.tbox[1] - to_y)/(self._height)
                else:
                    vec_y = 0
                vec_x = vec_x*self.speed_coef
                vec_y = vec_y*self.speed_coef
                vec_x = 1 if vec_x > 1 else vec_x
                vec_y = 1 if vec_x > 1 else vec_y
                if(abs(vec_y) < 0.03 and abs(vec_x) < 0.03):
                    vec_x = 0
                    vec_y = 0
                    self._Aimed = True
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
                        elif(medx > 2*self._width/3 + 50):
                            pos = pos | Position.RIGHT
                        elif(medx < self._width/3 - 50):
                            pos = pos | Position.LEFT
                        elif(medy < self.BOT):
                            pos = pos | Position.TOP
                    if(pos == Position.LEFT | Position.RIGHT
                       or pos == Position.LEFT | Position.RIGHT | Position.TOP):
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
                        self._logger.info("Object found on" + str(pos))
                else:
                    self.frames = 0
                    self._Aimed = False
                    self.cam.ContinuousMove(vec_x, vec_y)
            else:
                self.cam.stop()
        self._logger.info("Process stopped")

    # Set person box, greenscreen contours
    def set_box(self, box, con):
        self._box = box
        self.contours = con
