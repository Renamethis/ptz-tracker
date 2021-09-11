# Class for ONVIF

import onvif

import logging
from enum import Enum, auto
from threading import Thread
ZOOM = 0.0


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

    def __init__(self, ip, port, login, password, wsdl_path,
                 isAbsolute=False, name='ONVIF'):
        self.type = None
        self.name = name
        self.ip = ip
        self.port = port
        self.login = login
        self.password = password
        self.wpath = wsdl_path
        self.logger = logging.getLogger("Main.%s" % (self.name))
        self.logger.info("Process starting")
        self.isAbsolute = isAbsolute
        i = 0
        while(not self.connect() and i < self.ATTEMPTS):
            self.logger.warning("Can't connect to camera, trying to reconnect")
            i += 1
        if(i == self.ATTEMPTS):
            self.logger.exception('Error with camera connection')
            self.running = False
        self.requests = {k: self.ptz.create_type(k)
                         for k in self.requests_labels}
        self.status = self.ptz.GetStatus({'ProfileToken': self.profile.token})
        for request in self.requests:
            self.requests[request].ProfileToken = self.profile.token
        self.requests['AbsoluteMove'].Position = self.status.Position
        self.requests['ContinuousMove'].Velocity = self.status.Position
        self.goHome()
        self.running = True
        self.thread = Thread(target=self.ptzThread, name=self.name, args=())
        self.thread.start()

    def getStreamUri(self):
        request = self.media.create_type('GetStreamUri')
        request.StreamSetup = {'Stream': 'RTP-Unicast',
                               'Transport': {'Protocol': 'RTSP'}}
        request.ProfileToken = self.profile.token
        ans = self.media.GetStreamUri(request)
        return ans['Uri']

    def ptzThread(self):
        self.logger.info("Process started")
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
                self.connect()
                self.logger.exception('Error with moving camera, reconnecting')

    def ContinuousMove(self, x, y, zoom=0.0):
        self.requests['ContinuousMove'].Velocity.PanTilt.x = x
        self.requests['ContinuousMove'].Velocity.PanTilt.y = y
        self.requests['ContinuousMove'].Velocity.Zoom.x = zoom
        self.type = MoveType.Continuous

    def AbsoluteMove(self, x, y, zoom=0.0):
        self.requests['AbsoluteMove'].Position.PanTilt.x = x
        self.requests['AbsoluteMove'].Position.PanTilt.y = y
        self.requests['AbsoluteMove'].Position.Zoom.x = zoom
        self.type = MoveType.Absolute

    def connect(self, substream=1):
        try:
            self.cam = onvif.ONVIFCamera(self.ip, self.port, self.login,
                                         self.password, self.wpath)
            self.logger.info('Successful conection ONVIFCamera')
        except onvif.exceptions.ONVIFError:
            self.logger.exception('Error with camera connection')
            return False
        self.media = self.cam.create_media_service()
        k = 1 if substream else 0
        self.profile = self.media.GetProfiles()[k]
        self.ptz = self.cam.create_ptz_service()
        return True

    def goHome(self):
        self.ptz.GotoHomePosition(self.requests['GotoHomePosition'])

    def getAbsolute(self):
        points = self.status['Position']['PanTilt']
        return [points['x'], points['y']]

    def stop(self):
        self.ptz.Stop({'ProfileToken': self.profile.token})

    def stop_thread(self):
        self.running = False
