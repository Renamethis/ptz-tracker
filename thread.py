activate_this_file = "venv/bin/activate_this.py"
execfile(activate_this_file, dict(__file__=activate_this_file))
import sys
import os

os.system('cp -f utility_function/mobilenet_v1.py models/research/slim/nets/') 
os.system('cp -f utility_function/visualization_utils.py models/research/object_detection/utils/') 
os.chdir('models/research')
# don't work (((
#os.system('export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/slim')
os.chdir('object_detection')


import numpy as np
import math
import os
import six.moves.urllib as urllib
import tarfile
import tensorflow as tf
import zipfile
import threading
import configparser
import math

from collections import defaultdict
from io import StringIO
from PIL import Image

import cv2
from imutils.video import VideoStream
from imutils.video import FPS
from onvif import ONVIFCamera
from time import sleep
from threading import Thread

from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
from time import ctime, sleep




class WebcamVideoStream:
  def __init__(self, name="WebcamVideoStream"):
    #def __init__(self, src='rtsp://192.168.11.33:554', name="WebcamVideoStream"):
    #def __init__(self, src='rtsp://192.168.11.43:554', name="WebcamVideoStream"):
    #def __init__(self, src='rtsp://192.168.11.52:554/live/av0', name="WebcamVideoStream"):
    
    pwd = os.getcwd()
    lst = pwd.split('/')
    count = len(lst)-3
    string = ""
    for i in range(count):
      string = string + lst[i] + "/"
    pwd = string


    config = configparser.ConfigParser()
    config.read(pwd + "conf/settings.ini")
    mycam_rtsp = config.get("Settings","rtsp")
    
    try:
      self.stream = cv2.VideoCapture(mycam_rtsp)
      print "[INFO]     Successful conection VideoCapture"
    except:
      print "[ERROR]    Error with cv2.VideoCapture..."
      print "[INFO]     Check the correctness of the entered data in the setings.ini (rtsp)"
      sys.exit(0)
    (self.grabbed, self.frame) = self.stream.read()
    self.name = name
    self.stopped = False


  def start(self):
    t = Thread(target=self.update, name=self.name, args=())
    t.daemon = True
    t.start()
    return self

  def update(self):
    while True:
      if self.stopped:
        return
      (self.grabbed, self.frame) = self.stream.read()

  def read(self):
    return self.frame

  def stop(self):
    self.stopped = True





class Tensor:
  def __init__(self, lenght = 1280, width = 720, name="Tensor"):
    self.flag = False
    self.arr = []
    self.name = name
    self.new_image = np.zeros((width, lenght, 3))
    self.old_image = np.zeros((width, lenght, 3))
    self.stopped = False

    MODEL_NAME = 'ssd_mobilenet_v2_coco_2018_03_29'
    #MODEL_NAME = 'ssd_mobilenet_v2_face'
    MODEL_FILE = MODEL_NAME + '.tar.gz'
    DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'
    PATH_TO_FROZEN_GRAPH = MODEL_NAME + '/frozen_inference_graph.pb'
    PATH_TO_LABELS = os.path.join('data', 'mscoco_label_map.pbtxt')

    #opener = urllib.request.URLopener()
    #opener.retrieve(DOWNLOAD_BASE + MODEL_FILE, MODEL_FILE)
    tar_file = tarfile.open(MODEL_FILE)
    for file in tar_file.getmembers():
      file_name = os.path.basename(file.name)
      if 'frozen_inference_graph.pb' in file_name:
        tar_file.extract(file, os.getcwd())


    self.detection_graph = tf.Graph()
    with self.detection_graph.as_default():
      od_graph_def = tf.GraphDef()
      with tf.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')
    self.boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
    self.scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
    self.classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
    self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')
    self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
    self.category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS)
  def start(self):
    t = Thread(target=self.update, name=self.name, args=())
    t.daemon = True
    t.start()
    return self
  def update(self):
    with self.detection_graph.as_default():
      with tf.Session(graph=self.detection_graph) as sess:
        while True:
          image = self.new_image
          if self.stopped:
            return
          if not np.array_equal(image,self.old_image):

            image_np_expanded = np.expand_dims(image, axis=0)
            boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
            scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
            classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
            num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')
            self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
            (self.boxes, self.scores, self.classes, self.num_detections) = sess.run(
                [boxes, scores, classes, num_detections],
                feed_dict={self.image_tensor: image_np_expanded})
            vis_util.visualize_boxes_and_labels_on_image_array(
              image,
              np.squeeze(self.boxes),
              np.squeeze(self.classes).astype(np.int32),
              np.squeeze(self.scores),
              self.category_index,
              use_normalized_coordinates=True,
              line_thickness=8)
            #print 1
            self.flag = True
            self.old_image = image
  def setImage(self, image):
    self.new_image = image
  def read(self):
    if self.flag:
      return self.old_image
    else:
      return self.arr
  def read_boxes(self):
    if self.flag:
      return self.boxes
    else:
      return self.arr
  def read_scores(self):
    if self.flag:
      return self.scores
    else:
      return self.arr
  def read_classes(self):
    if self.flag:
      return self.classes
    else:
      return self.arr
  def stop(self):
    self.stopped = True


'''
class Motion:
  def __init__(self, lenght = 1280, width = 720, name="Motion"):
    self.x = -1
    self.y = -1
    self.to_x = 0
    self.to_y = 0
    self.lenght = lenght
    self.width = width
    self.speed_kof = 0
    self.name = name


    pwd = os.getcwd()
    lst = pwd.split('/')
    count = len(lst)-3
    string = ""
    for i in range(count):
      string = string + lst[i] + "/"
    pwd = string


    config = configparser.ConfigParser()
    config.read(pwd + "conf/settings.ini")
    mycam_ip        = config.get("Settings","ip")
    mycam_port      = config.get("Settings","port")
    mycam_login     = config.get("Settings","login")
    mycam_password  = config.get("Settings","password")
    mycam_wsdl_path = config.get("Settings","wsdl_path")


    #mycam = ONVIFCamera('192.168.11.33', 80, 'admin', 'Supervisor', '/etc/onvif/wsdl/')
    #mycam = ONVIFCamera('192.168.15.43', 80, 'admin', 'Supervisor', '/etc/onvif/wsdl/')
    try:
      mycam = ONVIFCamera(mycam_ip, mycam_port, mycam_login, mycam_password, mycam_wsdl_path)
      print "[INFO]     Successful conection ONVIFCamera"
    except:
      print "[ERROR]    Error with conect ONVIFCamera..."
      print "[INFO]     Check the correctness of the entered data in the setings.ini (ip,port,login, password or wsdl_path)"
      sys.exit(0)
    


    media = mycam.create_media_service()
    profile = media.GetProfiles()[0]
    self.ptz = mycam.create_ptz_service()
    self.request = self.ptz.create_type('GetConfigurationOptions')
    self.request.ConfigurationToken = profile.PTZConfiguration._token
    ptz_configuration_options = self.ptz.GetConfigurationOptions(self.request)
    self.request = self.ptz.create_type('ContinuousMove')
    self.request.ProfileToken = profile._token
    self.stopped = False

  def start(self):
    t = Thread(target=self.update, name=self.name, args=())
    t.daemon = True
    t.start()
    return self

  def update(self):
    while True:
      x = self.x
      y = self.y
      to_x = self.to_x
      to_y = self.to_y

      if x != -1 or y != -1:
        
        if (x < to_x +80 and x > to_x -80 and y < to_y +80 and y > to_y -80):
          #print(0)
          self.request.Velocity.PanTilt._x = 0
          self.request.Velocity.PanTilt._y = 0
          self.ptz.ContinuousMove(self.request)
        else:
          #print(self.x," & ", self.y)
          len_x = float(-(to_x - x))
          len_y = float((to_y - y))
          vec_x = len_x/self.lenght
          vec_x = int(vec_x*100)/100.0
          vec_x *= self.speed_kof
          vec_y = len_y/self.width
          vec_y = int(vec_y*100)/100.0
          vec_y *= self.speed_kof


          if vec_x > 1:
            vec_x = 1
          if vec_y > 1:
            vec_y = 1
          print (str(vec_y), " : ", str(vec_x))
          self.request.Velocity.PanTilt._x = vec_x
          self.request.Velocity.PanTilt._y = vec_y
          self.ptz.ContinuousMove(self.request)

      else:
        self.request.Velocity.PanTilt._x = 0
        self.request.Velocity.PanTilt._y = 0
        self.ptz.ContinuousMove(self.request)
      if self.stopped:
        return
  def setParam(self, x, y, to_x, to_y, speed_kof = 1):
    self.x = x
    self.y = y
    self.to_x = to_x
    self.to_y = to_y
    self.speed_kof = speed_kof

  def stop(self):
    self.stopped = True
'''


class Motion:
  def __init__(self, lenght = 1280, width = 720, name="Motion"):
    self.x = -1
    self.y = -1
    self.old_x = self.x
    self.old_y = self.y
    self.to_x = 0
    self.to_y = 0
    self.lenght = lenght
    self.width = width
    self.speed_kof = 0
    self.name = name


    pwd = os.getcwd()
    lst = pwd.split('/')
    count = len(lst)-3
    string = ""
    for i in range(count):
      string = string + lst[i] + "/"
    pwd = string


    config = configparser.ConfigParser()
    config.read(pwd + "conf/settings.ini")
    mycam_ip        = config.get("Settings","ip")
    mycam_port      = config.get("Settings","port")
    mycam_login     = config.get("Settings","login")
    mycam_password  = config.get("Settings","password")
    mycam_wsdl_path = config.get("Settings","wsdl_path")


    #mycam = ONVIFCamera('192.168.11.33', 80, 'admin', 'Supervisor', '/etc/onvif/wsdl/')
    #mycam = ONVIFCamera('192.168.15.43', 80, 'admin', 'Supervisor', '/etc/onvif/wsdl/')
    try:
      mycam = ONVIFCamera(mycam_ip, mycam_port, mycam_login, mycam_password, mycam_wsdl_path)
      print "[INFO]     Successful conection ONVIFCamera"
    except:
      print "[ERROR]    Error with conect ONVIFCamera..."
      print "[INFO]     Check the correctness of the entered data in the setings.ini (ip,port,login, password or wsdl_path)"
      sys.exit(0)
    


    media = mycam.create_media_service()
    profile = media.GetProfiles()[0]
    self.ptz = mycam.create_ptz_service()
    self.request = self.ptz.create_type('GetConfigurationOptions')
    self.request.ConfigurationToken = profile.PTZConfiguration._token
    ptz_configuration_options = self.ptz.GetConfigurationOptions(self.request)
    self.request = self.ptz.create_type('ContinuousMove')
    self.request.ProfileToken = profile._token
    self.stopped = False

  def start(self):
    t = Thread(target=self.update, name=self.name, args=())
    t.daemon = True
    t.start()
    return self

  def update(self):
    while True:
      x = self.x
      y = self.y
      to_x = self.to_x 
      to_y = self.to_y 
      print 'x    = ' + str(x)
      print 'y    = ' + str(y)
      print 'to_x = ' + str(to_x)
      print 'to_y = ' + str(to_y)
      if x != -1 and (x < to_x - 80 or x > to_x + 80):
        vec_x = float(x - to_x)/(to_x*3)
        print vec_x
        self.request.Velocity.PanTilt._x = vec_x
        self.request.Velocity.PanTilt._y = 0
        self.ptz.ContinuousMove(self.request)
      else:
        self.request.Velocity.PanTilt._x = 0
        self.request.Velocity.PanTilt._y = 0
        self.ptz.ContinuousMove(self.request)
      '''if self.stopped:
        self.request.Velocity.PanTilt._x = 0
        self.request.Velocity.PanTilt._y = 0
        self.ptz.ContinuousMove(self.request)
        return'''
  def setParam(self, x, y, to_x, to_y, speed_kof = 1):
    self.x = x
    self.y = y
    self.to_x = to_x
    self.to_y = to_y
    self.speed_kof = speed_kof

  def stop(self):
    self.stopped = True


def initTracker(stream, tensor):
  print "[INFO]     Start init"
  flag = True
  frame_count = 0
  x1 = 0
  x2 = 0
  while flag:
    image_np = stream.read()
    tensor.setImage(image_np)

    scores = tensor.read_scores()
    image_np = tensor.read()
    classes = tensor.read_classes()
    boxes = tensor.read_boxes()
    
    if (scores <> []):
      cv2.imshow('object detection', image_np)
      scores[scores > 0] = 1
      
      classes = classes*scores

      persons = np.where(classes == 1)[1]

      if (str(persons) <> '[]'):
        classes = tensor.read_classes()
        #print (persons_num, ': found person')
        person = persons[0]
        l_w = [width,lenght,width,lenght]
        box = boxes[0][person]


        if (box[1] > 0.1 and box[3] < 0.9):
          frame_count = frame_count + 1
          x1 = x1 + box[1]
          x2 = x2 + box[3]
        else:
          frame_count = 0
          x1 = 0
          x2 = 0

        if frame_count >= 50:
          return round((x2/50 - x1/50) *100)

      if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        sys.exit(0)

        





#print "[INFO]:     Start init"



pwd = os.getcwd()
lst = pwd.split('/')
count = len(lst)-3
string = ""
for i in range(count):
  string = string + lst[i] + "/"
pwd = string


config = configparser.ConfigParser()
config.read(pwd + "conf/settings.ini")
mycam_ip        = config.get("Settings","ip")
mycam_port      = config.get("Settings","port")
mycam_login     = config.get("Settings","login")
mycam_password  = config.get("Settings","password")
mycam_wsdl_path = config.get("Settings","wsdl_path")


#mycam = ONVIFCamera('192.168.11.33', 80, 'admin', 'Supervisor', '/etc/onvif/wsdl/')
#mycam = ONVIFCamera('192.168.15.43', 80, 'admin', 'Supervisor', '/etc/onvif/wsdl/')
try:
  mycam = ONVIFCamera(mycam_ip, mycam_port, mycam_login, mycam_password, mycam_wsdl_path)
  print "[INFO]     Successful conection ONVIFCamera"
except:
  print "[ERROR]    Error with conect ONVIFCamera..."
  print "[INFO]     Check the correctness of the entered data in the setings.ini (ip,port,login, password or wsdl_path)"
  sys.exit(0)

media = mycam.create_media_service()
profile = media.GetProfiles()[0]
ptz = mycam.create_ptz_service()
request = ptz.create_type('GetConfigurationOptions')
request.ConfigurationToken = profile.PTZConfiguration._token
ptz_configuration_options = ptz.GetConfigurationOptions(request)
request = ptz.create_type('ContinuousMove')
request.ProfileToken = profile._token

lenght_float = 1280.0 
width_float = 720.0
lenght = int(lenght_float)
width = int(width_float)




first = []
second = []
threads = []
stream = WebcamVideoStream()
tensor = Tensor()
#tensor2 = Tensor()
motion = Motion()

tensor.start()
#tensor2.start()
#motion.start()
stream.start()
  
#initTracker(stream, tensor)

fps = FPS().start()
persons_num = 0
i = 0
while True:
  i = i + 1
  #print ('----------------------------')
  image_np = stream.read()
  image_np = cv2.resize(image_np, (lenght,width))
  if (not np.array_equal(first,image_np)):
    second = first
    first = image_np
    tensor.setImage(image_np)
    '''if i%4 == 0:
      tensor.setImage(image_np)
    elif i%4 == 2:
      tensor2.setImage(image_np)'''

    #print('START')
    scores = tensor.read_scores()
    image_np = tensor.read()
    classes = tensor.read_classes()
    boxes = tensor.read_boxes()

    '''
    print('scores')
    print(scores)
    print('classes')
    print(classes)
    print('boxes')
    print(boxes)
    '''


    if (scores <> []):
      cv2.imshow('object detection', image_np)
      fps.update()
      #scores = scores[a>0.0] = 1
      #scores = np.array(tensor.read_scores())
      scores[scores > 0] = 1
      
      classes = classes*scores

      '''
      print('scores[scores > 0] = 1')
      print(scores)
      print('classes = classes*scores')
      print(classes)
      '''

      #print(classes)
      '''if i%2 == 0:
        cv2.imshow('object detection', tensor.read())
      elif i%2 == 1:
        cv2.imshow('object detection', tensor2.read())'''


      persons = np.where(classes == 1)[1]
      '''
      print('persons = np.where(classes == 1)[1]')
      print(str(persons))'''
      if (str(persons) <> '[]'):
        persons_num = persons_num + 1
        classes = tensor.read_classes()
        #print (persons_num, ': found person')
        person = persons[0]
        l_w = [width,lenght,width,lenght]
        box = boxes[0][person]

        box = l_w*box
        
        to_x = int(abs(box[1] - box[3])/2.0 + box[1])
        to_y = int(box[0])
        
        
        #print 'x    = ' + str(to_x)
        #print 'y    = ' + str(to_y)
        #print 'to_x = ' + str(lenght/3)
        #print 'to_y = ' + str(width/3)
        if (to_x < lenght/3 - 80 or to_x > lenght/3 + 80):
          vec_x = float(to_x - lenght/3)/(lenght)
        else:
          vec_x = 0
        if (to_y < width/3 - 80 or to_y > width/3 + 80):
          vec_y = float(width/3 - to_y)/(width)
        else:
          vec_y = 0
        print vec_x
        print vec_y
        request.Velocity.PanTilt._x = vec_x
        request.Velocity.PanTilt._y = vec_y
        ptz.ContinuousMove(request)
        
        '''
        
        motion.setParam(
          to_x, 
          to_y, 
          lenght/3, 
          width/3, 
          speed_kof=1)'''
      else:
        request.Velocity.PanTilt._x = 0
        request.Velocity.PanTilt._y = 0
        ptz.ContinuousMove(request)
        '''
        motion.setParam(
          -1, 
          -1, 
          lenght/3, 
          width/3, 
          speed_kof=0.1)'''
      

  ''''''
  
  if cv2.waitKey(25) & 0xFF == ord('q'):
    request.Velocity.PanTilt._x = 0
    request.Velocity.PanTilt._y = 0
    ptz.ContinuousMove(request)
    '''
    motion.setParam(
          -1, 
          -1, 
          lenght/3, 
          width/3, 
          speed_kof=0.1)
    '''
    cv2.destroyAllWindows()
    fps.stop()
    motion.stop()
    sleep(2)

    print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
    cv2.destroyAllWindows()
    break

    
  
    



