# Class for ONVIF

import onvif

import logging
from enum import Enum, auto
from threading import Thread
ZOOM = 0.5


class ptzType(Enum):
    Absolute = auto()
    Continuous = auto()
    Relative = auto()
    Stop = auto()
    GoHome = auto()


class Camera:
    __ptz_labels = ['ContinuousMove',
                    'AbsoluteMove',
                    'RelativeMove',
                    'Stop',
                    'GotoHomePosition',
                    'GetStatus']
    requests = None
    ATTEMPTS = 10

    # Initialization
    def __init__(self, ip, port, login, password, wsdl_path,
                 isAbsolute=False, name='ONVIF'):
        self.name = name
        self.__type = None
        self.__ip = ip
        self.__port = port
        self.__login = login
        self.__password = password
        self.__wpath = wsdl_path
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
                new_type = self.__type
                if(new_type is not None):
                    if(new_type == ptzType.Continuous):
                        self.ptz.ContinuousMove(
                            self.requests['ContinuousMove'])
                    elif(new_type == ptzType.Absolute and self.isAbsolute):
                        self.ptz.AbsoluteMove(self.requests['AbsoluteMove'])
                    elif(new_type == ptzType.Relative and self.isAbsolute):
                        self.ptz.RelativeMove(self.requests['RelativeMove'])
                    elif(new_type == ptzType.Stop):
                        self.ptz.Stop(self.requests['Stop'])
                    elif(new_type == ptzType.GoHome):
                        self.ptz.GotoHomePosition(
                            self.requests['GotoHomePosition'])
                    self.__type = None
                elif(self.isAbsolute):
                    self.status = self.ptz.GetStatus(
                        self.requests['GetStatus'])
            except (onvif.exceptions.ONVIFError, ConnectionResetError):
                self.__logger.exception('Error sending request, reconnecting')
                self.running = False
        self.__logger.info("Process stopped")

    # Move camera by vertical and horizontal speed
    def ContinuousMove(self, x, y, zoom=0.0):
        self.requests['ContinuousMove'].Velocity.PanTilt.x = x
        self.requests['ContinuousMove'].Velocity.PanTilt.y = y
        self.requests['ContinuousMove'].Velocity.Zoom.x = zoom
        self.__type = ptzType.Continuous

    # Move camera by absolute coordinates
    def AbsoluteMove(self, x, y, zoom=0.0):
        self.requests['AbsoluteMove'].Position.PanTilt.x = x
        self.requests['AbsoluteMove'].Position.PanTilt.y = y
        self.requests['AbsoluteMove'].Position.Zoom.x = zoom
        self.__type = ptzType.Absolute

    # Connect camera
    def connect(self, substream=1):
        self.__logger.info("Connecting to the camera")
        try:
            self.cam = onvif.ONVIFCamera(self.__ip, self.__port, self.__login,
                                         self.__password, self.__wpath)
            self.media = self.cam.create_media_service()
            k = 1 if substream else 0
            self.profile = self.media.GetProfiles()[k]
            self.ptz = self.cam.create_ptz_service()
            self.requests = {k: self.ptz.create_type(k)
                             for k in self.__ptz_labels}
            self.status = self.ptz.GetStatus({'ProfileToken':
                                              self.profile.token})
            for request in self.requests:
                self.requests[request].ProfileToken = self.profile.token
            self.requests['AbsoluteMove'].Position = self.status.Position
            self.requests['RelativeMove'].Position = self.status.Position
            self.requests['ContinuousMove'].Velocity = self.status.Position
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
        self.goHome()

    # Set camera to home position
    def goHome(self):
        self.__type = ptzType.GoHome

    # Return absolute coordinates from status
    def getAbsolute(self):
        points = self.status['Position']['PanTilt']
        return [points['x'], points['y']]

    # Stop camera
    def stop(self):
        self.__type = ptzType.Stop

    # Stop ptz thread
    def stop_thread(self):
        self.stop()
        while(self.__type is not None):
            pass
        self.running = False
