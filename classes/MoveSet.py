# Camera control class for autoset
from multiprocessing import Process
import numpy as np
from enum import Flag, auto
from classes.Move import Move
from time import sleep

# Enum class for object positions on greenscreen


class Position(Flag):
    NO = 0
    RIGHT = auto()
    LEFT = auto()
    TOP = auto()


class MoveSet(Move):

    # Initialization
    def __init__(self, ip, port, login, password, wsdl, Shape, speed,
                 Bounds, tracking_box, preset, name="Move"):
        Move.__init__(self, ip, port, login, password, wsdl, Shape, speed,
                      tracking_box, False, preset)
        self.LEFT = Bounds[0]
        self.BOT = Bounds[1]
        self.RIGHT = Bounds[2]
        self.UP = Bounds[3]
        self.__moveset_delay = 5

    # Main loop
    def run(self):
        self._logger.info("Process started")
        while not self.running.is_set():
            if(self.pause):
                self.cam.pause = True
                continue
            box, old_box, contours = self._queue.get()
            if(box is not None and contours is not None):
                to_x = int(abs(box[1] - box[3])/2.0 + box[1])
                to_y = int(box[0])
                if (to_x < self._tbox[0] or to_x > self._tbox[2]):
                    if to_x < self._tbox[0]:
                        vec_x = float(to_x - self._tbox[0])/(self._width)
                    else:
                        vec_x = float(to_x - self._tbox[2])/(self._width)
                else:
                    vec_x = 0
                if (to_y > self._tbox[1] + 40 or to_y < self._tbox[1] - 40):
                    vec_y = float(self._tbox[1] - to_y)/(self._height)
                else:
                    vec_y = 0
                vec_x = vec_x*self.speed_coef
                vec_y = vec_y*self.speed_coef
                vec_x = 1 if vec_x > 1 else vec_x
                vec_y = 1 if vec_x > 1 else vec_y
                if(abs(vec_y) < 0.03 and abs(vec_x) < 0.03 and not self._Aimed):
                    vec_x = 0
                    vec_y = 0
                    self._Aimed = True
                    self.cam.stop()
                    sleep(self.__moveset_delay)
                elif(abs(vec_x) < 0.03 and abs(vec_y) < 0.03):
                    pos = Position.NO
                    for con in contours:
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
                    '''
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
                    '''
                    #self.cam.ContinuousMove(0, 0)
                    self.cam.stop()
                    self.running.set()
                    if(pos != Position.NO):
                        self._logger.info("Object found on" + str(pos))
                else:
                    self._Aimed = False
                    self.cam.ContinuousMove(vec_x, vec_y)
            else:
                self.cam.stop()
        self._logger.info("Process stopped")

    # Set person box, greenscreen contours
    def set_box(self, box, con):
        if(not np.array_equal(box, self.old_box)):
            self._queue.put((box, self.old_box, con))
            self.old_box = box
