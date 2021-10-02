# Class for ONVIF

import onvif

import logging
from enum import Enum, auto
from threading import Thread
ZOOM = 0.5


class MoveType(Enum):
    Absolute = auto()
    Continuous = auto()
    Relative = auto()


class Camera:
    requests_labels = ['ContinuousMove',
                       'AbsoluteMove',
                       'GotoHomePosition',
                       'SetHomePosition',
                       'GetConfigurationOptions',
                       'GetStatus']
    requests = None
    ATTEMPTS = 10

    # Initialization
    def __init__(self, ip, port, login, password, wsdl_path,
                 isAbsolute=False, name='ONVIF'):
        self.type = None
        self.name = name
        self.ip = ip
        self.port = port
        self.login = login
        self.password = password
        self.wpath = wsdl_path
        self.__logger = logging.getLogger("Main.%s" % (self.name))
        self.isAbsolute = isAbsolute

    # Return url of rtsp-stream
    def getStreamUri(self):
        try:
            request = self.media.create_type('GetStreamUri')
            request.StreamSetup = {'Stream': 'RTP-Unicast',
                                   'Transport': {'Protocol': 'RTSP'}}
            request.ProfileToken = self.profile.token
            ans = self.media.GetStreamUri(request)
        except onvif.exceptions.ONVIFError:
            self.__logger.exception('Error getting rtsp-url')
            return None
        return ans['Uri']

    # PTZ thread for moving Camera and getting status
    def __ptz_thread(self):
        self.__logger.info("Process started")
        while self.running:
            try:
                if(self.type is not None):
                    if(self.type == MoveType.Continuous):
                        self.ptz.ContinuousMove(self.requests['ContinuousMove'])
                    elif(self.type == MoveType.Absolute and self.isAbsolute):
                        self.ptz.AbsoluteMove(self.requests['AbsoluteMove'])
                    elif(self.type == MoveType.Relative and self.isAbsolute):
                        self.ptz.RelativeMove(self.requests['RelativeMove'])
                    self.type = None
                elif(self.isAbsolute):
                    self.status = self.ptz.GetStatus({'ProfileToken':
                                                      self.profile.token})
            except onvif.exceptions.ONVIFError:
                self.__logger.exception('Error sending request, reconnecting')
                self.running = self.connect()
        self.__logger.info("Process stopped")

    # Move camera by vertical and horizontal speed
    def ContinuousMove(self, x, y, zoom=0.0):
        self.requests['ContinuousMove'].Velocity.PanTilt.x = x
        self.requests['ContinuousMove'].Velocity.PanTilt.y = y
        self.requests['ContinuousMove'].Velocity.Zoom.x = zoom
        self.type = MoveType.Continuous

    # Move camera by absolute coordinates
    def AbsoluteMove(self, x, y, zoom=0.0):
        self.requests['AbsoluteMove'].Position.PanTilt.x = x
        self.requests['AbsoluteMove'].Position.PanTilt.y = y
        self.requests['AbsoluteMove'].Position.Zoom.x = zoom
        self.type = MoveType.Absolute

    # Connect camera
    def connect(self, substream=1):
        self.__logger.info("Connecting to the camera")
        try:
            self.cam = onvif.ONVIFCamera(self.ip, self.port, self.login,
                                         self.password, self.wpath)
            self.media = self.cam.create_media_service()
            k = 1 if substream else 0
            self.profile = self.media.GetProfiles()[k]
            self.ptz = self.cam.create_ptz_service()
            self.requests = {k: self.ptz.create_type(k)
                             for k in self.requests_labels}
            self.status = self.ptz.GetStatus({'ProfileToken':
                                              self.profile.token})
            for request in self.requests:
                self.requests[request].ProfileToken = self.profile.token
            self.requests['AbsoluteMove'].Position = self.status.Position
            self.requests['ContinuousMove'].Velocity = self.status.Position
            self.goHome()
            self.__logger.info('Successfully connected to the camera')
        except onvif.exceptions.ONVIFError:
            self.__logger.critical('Error with camera connection')
            return False
        return True

    # Start threads
    def start(self):
        self.__logger.info("Process starting")
        self.running = True
        self.__thread = Thread(target=self.__ptz_thread,
                               name=self.name, args=())
        self.__thread.start()

    # Set camera to home position
    def goHome(self):
        try:
            self.ptz.GotoHomePosition(self.requests['GotoHomePosition'])
        except onvif.exceptions.ONVIFError:
            self.__logger.exception('Error sending request')
            self.running = self.connect()

    # Return absolute coordinates from status
    def getAbsolute(self):
        points = self.status['Position']['PanTilt']
        return [points['x'], points['y']]

    # Stop camera
    def stop(self):
        try:
            self.ptz.Stop({'ProfileToken': self.profile.token})
        except onvif.exceptions.ONVIFError:
            self.__logger.exception('Error sending request')
            self.running = self.connect()

    # Stop ptz thread
    def stop_thread(self):
        self.stop()
        self.running = False
