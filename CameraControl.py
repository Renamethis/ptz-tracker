### Control your Camera
from onvif import ONVIFCamera
from time import sleep
import cv2
import os
from queue import Queue
from threading import Thread
from argparse import ArgumentParser
### CLI arguments
parser = ArgumentParser()
parser.add_argument("-i", "--ip", dest="ip_onvif",
                    help="Ip address to camera", action="store", type=str)
parser.add_argument("-p", "--port", dest="port_onvif",
                    help="Port to onvif service on camera", action="store")
parser.add_argument("-u", "--username", dest="user",
                    help="Username to Onvif Camera user", action="store")
parser.add_argument("-c", "--password", dest="passw",
                    help="Password to Onvif Camera user", action="store")
args = parser.parse_args()
ip = args.ip_onvif
port = args.port_onvif if args.port_onvif is not None else "80"
user = args.user if args.user is not None else "admin"
password = args.passw if args.passw is not None else "Supervisor"
pwd = os.path.dirname(os.path.realpath(__file__))
zoom_max = 2
zoom = 0
def nothing(val):
    pass
### Class to grab rtsp_stream from camera
class rtsp_stream(Thread):
    __capture = None
    __img = None
    __isCapturing = False
    def __init__(self, Uri):
        Thread.__init__(self)
        self.__capture = cv2.VideoCapture(Uri)
        self.__isCapturing = True;
    def __del__(self):
        self.__capture.release()
    def run(self):
        while self.__capture.isOpened() and self.__isCapturing :
            ret, frame = self.__capture.read()
            if not ret:
                print('Camera was disconnected')
                self.__capture.release()
                self.__init__(self.Uri)
            frame = cv2.resize(frame, (720,640))
            cv2.putText(frame, 'Use WASD to Control', (10,620),
                        cv2.FONT_HERSHEY_SIMPLEX,1, (255,255,255), 2)
            self.__img = frame
    def get_frame(self):
        return self.__img
    def is_opened(self):
        return self.__capture.isOpened()
    def stop_thread(self):
        self.__isCapturing = False
wsdl = pwd + '/wsdl'
mycam = ONVIFCamera(ip, port, user, password, wsdl)
media = mycam.create_media_service()
profile = media.GetProfiles()[1]
ptz = mycam.create_ptz_service()
request = media.create_type('GetStreamUri')
request.ProfileToken = profile.token
request.StreamSetup = {'Stream': 'RTP-Unicast',
                        'Transport': {'Protocol': 'RTSP'}}
Uri = media.GetStreamUri(request)['Uri']
request = ptz.create_type('ContinuousMove')
status = ptz.GetStatus({'ProfileToken': profile.token})
status.Position.PanTilt.x = 0.0
status.Position.PanTilt.y = 0.0
request.Velocity = status.Position
request.ProfileToken = profile.token
speed = 1
strsplit = Uri.split('//')
keys = [ord('d'), ord('a'), ord('w'), ord('s')]
controls = [(speed, 0), (-speed, 0), (0, speed), (0, -speed)]
direction_labels = ['Right', 'Left', 'Up', 'Down']
rtsp_thread = rtsp_stream(strsplit[0] +
'//' + 'admin:Supervisor@' + strsplit[1])
rtsp_thread.start()
cv2.namedWindow('Coordinates')
cv2.createTrackbar('Zoom', 'Coordinates' , 1, zoom_max, nothing)
while rtsp_thread.get_frame() is None:
    pass
while rtsp_thread.is_opened():
    frame = rtsp_thread.get_frame()
    cv2.imshow('Coordinates', frame)
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = 0
    zoom = cv2.getTrackbarPos('Zoom', 'Coordinates')
    request.Velocity.Zoom.x = zoom-1
    key = cv2.waitKey(1)
    if key & 0xFF in keys:
        request.Velocity.PanTilt.x = controls[keys.index(key & 0xFF)][0]
        request.Velocity.PanTilt.y = controls[keys.index(key & 0xFF)][1]
        while cv2.waitKey(1) == key:
            ptz.ContinuousMove(request)
            frame = rtsp_thread.get_frame()
            cv2.putText(frame, 'Moving to ' +
                        direction_labels[keys.index(key & 0xFF)], (470,620),
                        cv2.FONT_HERSHEY_SIMPLEX,1, (255,255,0), 2)
            cv2.imshow('Coordinates', frame)
    elif key & 0xFF == ord('q'):
        request.Velocity.PanTilt.x = 0
        request.Velocity.PanTilt.y = 0
        ptz.ContinuousMove(request)
        break
    else:
        request.Velocity.PanTilt.x = 0
        request.Velocity.PanTilt.y = 0
        ptz.ContinuousMove(request)
cv2.destroyAllWindows()
rtsp_thread.stop_thread()
