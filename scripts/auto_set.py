import sys
import os
pwd = os.getcwd()
wsdl_path = pwd + '/wsdl'
sys.path.append(pwd+'/classes')
import cv2
import Tensor
import Move2
import Utility_Functions as UF
import logging
import WebcamVideoStream
import numpy as np
ip = UF.get_setting("ip")
length = int(UF.get_setting("length"))
hight = int(UF.get_setting("hight"))
port = UF.get_setting("port")
login = UF.get_setting("login")
password = UF.get_setting("password")
speed_coef = float(UF.get_setting("speed_coef"))
tweaking = float(UF.get_setting("tweaking"))/100.0
zone = int(UF.get_setting("trackingzone"))
bounds = [float(UF.get_setting("x1")),
          float(UF.get_setting("y1")),
          float(UF.get_setting("x2")),
          float(UF.get_setting("y2"))]
tensor = Tensor.Tensor(hight=hight, length=length)
move = Move2.Move(length, hight, speed_coef, ip, port, login,
               password, wsdl_path, tweaking, bounds, zone)
rtsp_url = "rtsp://" + login + ":" + password + "@" + move.cam.getStreamUri().split('//')[1]
stream = WebcamVideoStream.WebcamVideoStream(rtsp_url,
                               Jetson=(1 if (UF.get_setting('device')
                                       == 'Jetson') else 0))
stream.start()
tensor.start()
move.start()
# Logger setup
logger = logging.getLogger("AutoSet")
logger.setLevel(logging.INFO)
fh = logging.FileHandler(pwd+"/main.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.info("Programm started")
while move.isProcessing:
    img = stream.read()
    img = cv2.resize(img, (length, hight))
    tensor.set_image(img)
    img = tensor.read()
    if img is not None:
        scores = tensor.read_scores().numpy()
        image_np = tensor.read()
        classes = tensor.read_classes().numpy()
        boxes = tensor.read_boxes().numpy()
        if (scores is not None and image_np is not None and classes is not None and boxes is not None):
            score = np.where(scores > 0.5)
            classes = classes
            persons = np.where(classes == 1)[1]
            if (len(scores[scores > 0.5]) != 0):
                person = persons[0]
                l_h = [hight, length, hight, length]
                box = boxes[score][0]
                box = (l_h*box)
                move.set_box(box)
            else:
                move.set_box(None)
move.stop()
tensor.stop()
stream.stop()
