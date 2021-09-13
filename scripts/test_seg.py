import cv2
import numpy as np
import sys
import os

pwd = os.getcwd()
wsdl_path = pwd + '/wsdl'
sys.path.append(pwd+'/classes')
import WebcamVideoStream
stream = WebcamVideoStream.WebcamVideoStream("rtsp://admin:Supervisor@172.18.191.12:554/stream/sub")
stream.start()
COLOR_LIGHT = (100, 255, 255)
COLOR_DARK = (50, 100, 100)
while True:
    img = stream.read()
    image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = 0*np.zeros((image.shape[1], image.shape[0]), dtype=np.uint8)
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsv, COLOR_DARK, COLOR_LIGHT)
    mask = cv2.bitwise_not(mask)
    cv2.imshow('mask', mask)
    if(cv2.waitKey(1) & 0xFF == ord('q')):
        break
cv2.destroyAllWindows()
