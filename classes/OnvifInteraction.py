# Class for ONVIF

import onvif
import logging
from enum import Enum, auto
from multiprocessing import Process, Event, Queue

ZOOM = 0.5


class ptzType(Enum):
    Absolute = auto()
    Continuous = auto()
    Relative = auto()
    Stop = auto()
    GoHome = auto()
    GoPreset = auto()
    GetStatus = auto()


class Camera(Process):
    __ptz_labels = ['ContinuousMove',
                    'AbsoluteMove',
                    'RelativeMove',
                    'Stop',
                    'GotoHomePosition',
                    'GetStatus',
                    'GetPresets',
                    'GotoPreset']
    requests = None
    # Initialization

    def __init__(self, ip, port, login, password, wsdl_path, preset,
                 isAbsolute=False, name='ONVIF'):
        Process.__init__(self)
        self.name = name
        self.__type = None
        self.__ip = ip
        self.__port = port
        self.__login = login
        self.__password = password
        self.__wpath = wsdl_path
        self.__preset = preset
        self.__logger = logging.getLogger("Main.%s" % (self.name))
        self.__isAbsolute = isAbsolute
        self.__ptz_thread = None
        self.__running = Event()
        self.__queue = Queue()

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
    def run(self):
        '''
        __switch_ptz_dict = {
            ptzType.Continuous:
                self.ptz.ContinuousMove(self.requests['ContinuousMove']),
            ptzType.Absolute:
                self.ptz.AbsoluteMove(self.requests['AbsoluteMove']),
            ptzType.Relative:
                self.ptz.RelativeMove(self.requests['RelativeMove']),
            ptzType.Stop:
                self.ptz.Stop(self.requests['Stop']),
            ptzType.GoPreset:
                self.ptz.GotoHomePosition(self.requests['GotoHomePosition']) if self.__preset == 'Home' else self.ptz.GotoPreset(
                    self.requests['GotoPreset']),
            ptzType.GetStatus:
                self.ptz.GetStatus(self.requests['GetStatus'])
        }
        '''
        self.__logger.info("Process started")
        while not self.__running.is_set():
            try:
                new_type, request = self.__queue.get()
                if(new_type is not None):
                    if(new_type == ptzType.Continuous):
                        self.ptz.ContinuousMove(request)
                    elif(new_type == ptzType.Absolute and self.isAbsolute):
                        self.ptz.AbsoluteMove(request)
                    elif(new_type == ptzType.Relative and self.isAbsolute):
                        self.ptz.RelativeMove(request)
                    elif(new_type == ptzType.Stop):
                        self.ptz.Stop(request)
                    elif(new_type == ptzType.GoPreset):
                        self.ptz.GotoPreset(request)
                    elif(new_type == ptzType.GoHome):
                        self.ptz.GotoHomePosition(request)
                elif(self.__isAbsolute):
                    self.status = self.ptz.GetStatus(
                        self.requests['GetStatus'])
            except (onvif.exceptions.ONVIFError, ConnectionResetError):
                self.__logger.exception('Error sending request, reconnecting')
                self.stop_thread()
        self.__logger.info("Process stopped")

    # Move camera by vertical and horizontal speed
    def ContinuousMove(self, x, y, zoom=0.0):
        self.requests['ContinuousMove'].Velocity.PanTilt.x = x
        self.requests['ContinuousMove'].Velocity.PanTilt.y = y
        self.requests['ContinuousMove'].Velocity.Zoom.x = zoom
        self.__queue.put((ptzType.Continuous, self.requests['ContinuousMove']))

    # Move camera by absolute coordinates
    def AbsoluteMove(self, x, y, zoom=0.0):
        self.requests['AbsoluteMove'].Position.PanTilt.x = x
        self.requests['AbsoluteMove'].Position.PanTilt.y = y
        self.requests['AbsoluteMove'].Position.Zoom.x = zoom
        self.__queue.put((ptzType.Absolute, self.requests['AbsoluteMove']))

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
            preset_token = None
            for preset in self.ptz.GetPresets(self.requests['GetPresets']):
                if(preset['Name'] == self.__preset):
                    preset_token = preset['token']
                    break
            if(preset_token is None):
                self.__preset = 'Home'
            self.status.Position.Zoom.x = 0.0
            self.status.Position.PanTilt.x = 0.0
            self.status.Position.PanTilt.y = 0.0
            self.requests['GotoPreset'].PresetToken = self.__preset
            self.requests['GotoPreset'].Speed = self.status.Position
            self.requests['AbsoluteMove'].Position = self.status.Position
            self.requests['RelativeMove'].Translation = self.status.Position
            self.requests['ContinuousMove'].Velocity = self.status.Position
            self.__logger.info('Successfully connected to the camera')
        except onvif.exceptions.ONVIFError:
            self.__logger.critical('Error with camera connection')
            return False
        return True

    # Start threads
    def start(self):
        self.__logger.info("Process starting")
        Process.start(self)
        self.goHome()

    # Set camera to home position
    def goHome(self):
        if(self.__preset == 'Home'):
            self.__queue.put(
                (ptzType.GoHome, self.requests['GotoHomePosition']))
        else:
            self.__queue.put((ptzType.GoPreset, self.requests['GotoPreset']))
    # Return absolute coordinates from status

    def getAbsolute(self):
        points = self.status['Position']['PanTilt']
        return [points['x'], points['y']]

    # Stop camera
    def stop(self):
        self.__queue.put((ptzType.Stop, self.requests['Stop']))

    # Stop ptz thread
    def stop_thread(self):
        self.stop()
        while(self.__type is not None):
            pass
        self.__running.set()
