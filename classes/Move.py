# Camera control parent class
import logging
from classes.OnvifInteraction import Camera


class Move:
    # Initializing variables
    def __init__(self, ip, port, login, password, wsdl, Shape, speed,
                 tracking_box, isAbsolute, name="Move"):
        self._tbox = tracking_box
        self._name = name
        self._ip = ip
        self._port = port
        self._login = login
        self._password = password
        self._wsdl = wsdl
        self._box = None
        self.old_box = None
        self.old_vec_x = 0
        self.old_vec_y = 0
        self.count_frame = 0
        self.speed_coef = speed
        self.pause = False
        self._ddelay = 0.1
        self._width = Shape[1]
        self._height = Shape[0]
        self._logger = logging.getLogger("Main.%s" % (self._name))
        self._Aimed = False
        self.running = False
        self._isAbsolute = isAbsolute

    # Starting threads
    def start(self):
        self._logger.info("Process starting")
        self.cam = Camera(self._ip, self._port, self._login, self._password,
                          self._wsdl, self._isAbsolute)
        if(not self.cam.connect()):
            return False
        self.cam.start()
        return True

    # Setting box
    def set_box(self, box):
        self._box = box

    # Stopping threads
    def stop(self):
        self.cam.stop_thread()
        del self.cam
        self.running = False

    # Return rtsp-thread from Camera
    def get_rtsp(self):
        return "rtsp://" + self._login + ":" + self._password + "@" + \
                   self.cam.getStreamUri().split('//')[1]

    # Return aimed-state bool
    def isAimed(self):
        return self._Aimed
