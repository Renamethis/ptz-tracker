rtsp = "rtsp://172.18.191.72:554/"
gst = "rtspsrc location=" + rtsp + '" latency=2000 ! rtph264depay ! h264parse ! nvv4l2decoder enable-max-performance=1 ! nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! video/x-raw,format=BGR ! appsink'
print(gst)
import cv2
import time
import os
import sys
pwd = os.getcwd()
sys.path.append(pwd+'/classes')
import Tensor
tensor = tensor = Tensor.Tensor(hight=640, length=640)
tensor.start()
cap = cv2.VideoCapture(gst, cv2.CAP_GSTREAMER)
start = 0
sum = 0
i = 1
while(cap.isOpened()):
    start = time.time()
    print('Cap')
    ret, frame = cap.read()
    tensor.set_image(frame)
    #print(frame.shape)
    cv2.imwrite('image.png', frame)
    stop = time.time()
    dur = stop - start
    sum += 1/dur
    print(sum/i)
    i+=1
