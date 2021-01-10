from onvif import ONVIFCamera
from time import sleep
import cv2
mycam = ONVIFCamera('172.18.191.72', '80', 'admin', 'Supervisor', '/home/ivangavrilov/Documents/ptz-tracker/wsdl')
media = mycam.create_media_service()
profile = media.GetProfiles()[0]
ptz = mycam.create_ptz_service()
request = ptz.create_type('ContinuousMove')
status = ptz.GetStatus({'ProfileToken': profile.token})
status.Position.PanTilt.x = 0.0
status.Position.PanTilt.y = 0.0
request.Velocity = status.Position
request.ProfileToken = profile.token
speed = 50
#ptz.GetScopes(request)
#scp = mycam.devicemgmt.create_type('GeoLocation')
#resp = mycam.devicemgmt.GeoLocation(scp)
cap = cv2.VideoCapture("rtsp://172.18.191.72:554/Channels/Streaming/2")
str = 'Use WASD to control'
keys = [ord('d'), ord('a'), ord('w'), ord('s')]
controls = [(speed, 0), (-speed, 0), (0, speed), (0, -speed)]
while cap.isOpened():
    ret, frame = cap.read()
    if frame is None:
        continue
    frame = cv2.resize(frame, (1080, 720))
    #cv2.putText(frame, str, (10,500), cv2.FONT_HERSHEY_SIMPLEX,
    #1, (255,255,255), 2)
    cv2.imshow('Coordinates', frame)
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = 0
    request.Velocity.Zoom.x = 0
    key = cv2.waitKey(0)
    if key & 0xFF in keys:
        request.Velocity.PanTilt.x = controls[keys.index(key & 0xFF)][0]
        request.Velocity.PanTilt.x = controls[keys.index(key & 0xFF)][1]
        while cv2.waitKey(0) == key:
            ptz.ContinuousMove(request)
            ret, frame = cap.read()
            if frame is None:
                continue
            frame = cv2.resize(frame, (1080, 720))
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
    print('Hey')
cap.release()
cv2.destroyAllWindows()
def move(x, y):
    request.Velocity.PanTilt.x = x
    request.Velocity.PanTilt.y = y
    self.ptz.ContinuousMove(self.request)
class point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
