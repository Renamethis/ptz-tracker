# Camera controll class for tracker
from threading import Thread
from time import sleep
import numpy as np
from classes.zmqgrabber import message_grabber
from classes.Move import Move


class MoveBase(Move):
    # Initialization
    def __init__(self, ip, port, login, password, wsdl, Shape, speed, tweaking,
                 bounds, tracking_box, isAbsolute, name="Move"):
        super().__init__(ip, port, login, password, wsdl, Shape, speed,
                         tracking_box)
        self.tweaking = tweaking
        self.bounds = bounds
        self.isAbsolute = isAbsolute
        self.spaceLimits = bounds

    # Starting thread
    def start(self):
        self.running = super().start()
        self.mt = message_grabber("tcp://*:5555")
        self.mt.start()
        self.__thread = Thread(target=self.__update, name=self._name, args=())
        self.__thread.daemon = True
        self.__thread.start()
        return self.running

    # Main loop for move processing
    def __update(self):
        self._logger.info("Process started")
        while self.running:
            if(self.pause):
                self.cam.pause = True
                continue
            message = self.mt.get_message()
            rotation = self.mt.get_rotation() if message is not None else None
            if self.pause:
                self.cam.stop()
                sleep(self._ddelay)
            box = self._box
            old_box = self.old_box
            if np.array_equal(box, old_box):
                sleep(self._ddelay)
            elif box is not None:
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
                if(self.isAbsolute or message is not None):
                    point = self.cam.getAbsolute() if \
                            self.isAbsolute else rotation
                    if((point[0] < self.spaceLimits[0] and vec_x < 0)
                       or (point[0] > self.spaceLimits[2] and vec_x > 0)):
                        vec_x = 0
                    if(point[1] < self.spaceLimits[1] and vec_y > 0
                       or (point[1] > self.spaceLimits[3] and vec_y < 0)):
                        vec_y = 0
                if(abs(vec_y) < 0.05 and abs(vec_x) < 0.05):
                    self._isAimed = True
                    self.cam.stop()
                else:
                    # self.logger.info('X: ' + str(vec_x)
                    #                 + ' Y: ' + str(vec_y))
                    self._isAimed = False
                    self.cam.ContinuousMove(vec_x, vec_y)
                old_box = box
                self.count_frame = 0
            elif box is None and old_box is not None:
                if (self.count_frame < 20):
                    self.cam.ContinuousMove(vec_x, vec_y)
                elif (self.count_frame == 20):
                    self.cam.stop()
                    sleep(self._ddelay)
                elif (self.count_frame == 60):
                    self.count_frame = 0
                    self.cam.goHome()
                    old_box = box
                    sleep(self._ddelay)
                sleep(self.tweaking)
                self.count_frame = self.count_frame + 1
            self.old_box = old_box
        self._logger.info("Process stopped")

    # Stop threads
    def stop(self):
        super().stop()
        self.mt.stop_thread()
