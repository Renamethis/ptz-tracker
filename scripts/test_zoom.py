import cv2
import os
import sys
import numpy as np
pwd = os.getcwd()
sys.path.append(pwd)
from classes.Tensor import Tensor

video_path = '/home/ivan/Downloads/stock.mp4'
cap = cv2.VideoCapture(video_path, cv2.CAP_FFMPEG)
tensor = Tensor()
tensor.start()
height = 640
width = 720
l_h = [height, width, height, width]
while not tensor.running:
    pass
ret, frame = cap.read()
image = cv2.resize(frame, (640, 720))
tensor.set_image(image)
while(cap.isOpened()):
    body = tensor.return_body()
    face = tensor.return_face()
    if(body is not None and face is not None):
        cv2.rectangle(image, (body[1], body[0]), (body[3], body[2]), (0,255,0), 1)
        cv2.imshow('test', image)
        cv2.imshow()
        ret, frame = cap.read()
        image = cv2.resize(frame, (640, 720))
        tensor.set_image(image)
tensor.stop()
cv2.destroyAllWindows()
