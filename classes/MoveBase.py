# Camera controll class for tracker
from time import sleep
import numpy as np
# from classes.zmqgrabber import message_grabber
from classes.Move import Move


class MoveBase(Move):
    # Initialization
    def __init__(self, ip, port, login, password, wsdl, Shape, speed, tweaking,
                 bounds, tracking_box, isAbsolute, preset, name="Move"):
        Move.__init__(self, ip, port, login, password, wsdl, Shape, speed,
                      tracking_box, isAbsolute, preset)
        self.__tweaking = tweaking
        self.__spaceLimits = bounds
        self.__isAssistant = False

    # Starting thread
    def start(self, isAssistant=False):
        # Message thread using for ORB_SLAM2
        #self.mt = message_grabber("tcp://*:5555")
        #self.mt.start()
        self.__isAssistant = isAssistant
        return super().start()

    # Main loop for move processing
    def run(self):
        self._logger.info("Process started")
        message = rotation = None
        tweaking_frames = 0
        while not self.running.is_set():
            #message = self.mt.get_message()
            #rotation = self.mt.get_rotation() if message is not None else None
            box, old_box = self._queue.get()
            if(np.array_equal(box, old_box) and box is not None):
                continue
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
                if (to_y > self._tbox[1] + 20 or to_y < self._tbox[1] - 20):
                    vec_y = float(self._tbox[1] - to_y)/(self._height)
                else:
                    vec_y = 0
                vec_x = vec_x*self.speed_coef
                vec_y = vec_y*self.speed_coef
                vec_x = 1 if vec_x > 1 else vec_x
                vec_y = 1 if vec_x > 1 else vec_y
                if(self._isAbsolute or message is not None):
                    point = self._cam.getAbsolute() if \
                            self._isAbsolute else rotation
                    if((point[0] < self.__spaceLimits[0] and vec_x < 0)
                       or (point[0] > self.__spaceLimits[2] and vec_x > 0)):
                        vec_x = 0
                    if(point[1] < self.__spaceLimits[1] and vec_y > 0
                       or (point[1] > self.__spaceLimits[3] and vec_y < 0)):
                        vec_y = 0
                if(abs(vec_y) < 0.03 and abs(vec_x) < 0.03):
                    self._Aimed = True
                    self._cam.stop()
                else:
                    #self._logger.info('X: ' + str(vec_x) + ' Y: ' + str(vec_y))
                    self._Aimed = False
                    self._cam.ContinuousMove(vec_x, vec_y)
                tweaking_frames = 0
            elif box is None and old_box is not None and not self.__isAssistant:
                if (tweaking_frames < 20):
                    self._cam.ContinuousMove(vec_x, vec_y)
                elif (tweaking_frames == 20):
                    self._cam.stop()
                    sleep(self._ddelay)
                elif (tweaking_frames == 60):
                    tweaking_frames = 0
                    self._cam.goHome()
                    sleep(self._ddelay)
                sleep(self.__tweaking)
                tweaking_frames += 1
        self._logger.info("Process stopped")

    # Stop threads
    def stop(self):
        super().stop()
        #self.mt.stop_thread()
