# Class for ONVIF

from onvif import ONVIFCamera

import logging
import sys


class Camera:
    requests_labels = ['ContinuousMove',
                       'GotoHomePosition',
                       'SetHomePosition',
                       'GetConfigurationOptions',
                       'GetStatus']
    requests = None
    ATTEMPTS = 10

    def __init__(self, ip, port, login, password, wsdl_path, name='Camera'):
        self.name = name
        self.ip = ip
        self.port = port
        self.login = login
        self.password = password
        self.wpath = wsdl_path
        self.logger = logging.getLogger("Main.%s.init" % (self.name))
        i = 0
        while(not self.connect() and i < self.ATTEMPTS):
            self.logger.warning("Can't connect to camera, trying to reconnect")
            i += 1
        if(i == self.ATTEMPTS):
            self.logger.exception('Error with camera connection')
            sys.exit(0)
        self.requests = {k: self.ptz.create_type(k)
                         for k in self.requests_labels}
        self.status = self.getStatus()
        self.requests['ContinuousMove'].Velocity = self.status.Position
        self.requests['ContinuousMove'].ProfileToken = self.profile.token
        self.requests['ContinuousMove'].Velocity.Zoom.x = 0
        self.requests['GotoHomePosition'].ProfileToken = self.profile.token
        self.goHome()

    def getStreamUri(self):
        request = self.media.create_type('GetStreamUri')
        request.StreamSetup = {'Stream': 'RTP-Unicast',
                               'Transport': {'Protocol': 'RTSP'}}
        request.ProfileToken = self.profile.token
        ans = self.media.GetStreamUri(request)
        return ans['Uri']

    def move(self, x, y):
        try:
            self.requests['ContinuousMove'].Velocity.PanTilt.x = x
            self.requests['ContinuousMove'].Velocity.PanTilt.y = y
            self.ptz.ContinuousMove(self.requests['ContinuousMove'])
        except:
            self.connect()
            self.logger.exception('Error with moving camera, reconnecting')
            self.move(x, y)

    def connect(self, substream=1):
        try:
            self.cam = ONVIFCamera(self.ip, self.port, self.login, self.password, self.wpath)
            self.logger.info('Successful conection ONVIFCamera')
        except:
            self.logger.exception('Error with camera connection')
            return False
        self.media = self.cam.create_media_service()
        k = 1 if substream else 0
        self.profile = self.media.GetProfiles()[k]
        self.ptz = self.cam.create_ptz_service()
        return True

    def getStatus(self):
        return self.ptz.GetStatus({'ProfileToken': self.profile.token})

    def goHome(self):
        pass
        #self.ptz.GotoHomePosition(self.requests['GotoHomePosition'])
    def getAbsolute(self):
        points = self.getStatus()['Position']['PanTilt']
        return [points['x'], points['y']]

    def stop(self):
        self.ptz.Stop({'ProfileToken': self.profile.token})
