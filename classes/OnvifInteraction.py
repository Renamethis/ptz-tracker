from onvif import ONVIFCamera
import logging
class Camera:
    def __init__(self, ip, port, login, password, wsdl_path, name='Camera'):
        self.name = name
        self.ip = ip
        self.port = port
        self.login = login
        self.password = password
        self.wpath = wsdl_path
        self.init_logger = logging.getLogger("Main.%s.init" % (self.name))
    def getStreamUri(self):
        self.request = self.media.create_type('GetStreamUri')
        self.request.ProfileToken = self.profile._token
        ans = self.media.GetStreamUri(self.request)
        return ans['Uri']
    def move(self, x, y):
        self.request = self.ptz.create_type('ContinuousMove')
        self.request.ConfigurationToken = self.profile.PTZConfiguration._token
        self.request.Velocity.PanTilt._x = x
        self.request.Velocity.PanTilt._y = y
        self.ptz.ContinuousMove(self.request)
    def connect(self, substream=1):
        try:
            self.cam = ONVIFCamera(self.ip, self.port, self.login, self.password, self.wpath)
            self.init_logger.info("Successful conection ONVIFCamera")
        except:
            self.init_logger.exception('Error with camera connection')
            return False
        self.media = self.cam.create_media_service()
        k = 1 if substream else 0
        self.profile = self.media.GetProfiles()[k]
        self.ptz = self.cam.create_ptz_service()
        return True
