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




'''
class Motion:
  def __init__(self):
    self.

  def start(self):
    t = Thread(target=self.update, name=self.name, args=())
    t.daemon = True
    t.start()
    return self

  def update(self):
    while True:
      if self.stopped:
        return (self.grabbed, self.frame) = self.stream.read()

  def read(self):
    return self.frame

  def stop(self):
    self.stopped = True
'''



class WebcamVideoStream:
  def __init__(self, src='rtsp://192.168.11.33:554', name="WebcamVideoStream"):
    #def __init__(self, src='rtsp://192.168.11.43:554', name="WebcamVideoStream"):
    #def __init__(self, src='rtsp://192.168.11.52:554/live/av0', name="WebcamVideoStream"):
  
    self.stream = cv2.VideoCapture(src)
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




class Motion:
  def __init__(self):
    mycam = ONVIFCamera('192.168.11.33', 80, 'admin', 'Supervisor', '/etc/onvif/wsdl/')
    media = mycam.create_media_service()
    profile = media.GetProfiles()[0]
    ptz = mycam.create_ptz_service()
    request = ptz.create_type('GetConfigurationOptions')
    request.ConfigurationToken = profile.PTZConfiguration._token
    ptz_configuration_options = ptz.GetConfigurationOptions(request)
    request = ptz.create_type('ContinuousMove')
    request.ProfileToken = profile._token
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

  def read(self):
    return self.d

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
            '''vis_util.visualize_boxes_and_labels_on_image_array(
              image,
              np.squeeze(self.boxes),
              np.squeeze(self.classes).astype(np.int32),
              np.squeeze(self.scores),
              self.category_index,
              use_normalized_coordinates=True,
              line_thickness=8)'''
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




def mov_to_face(ptz, request, x, y, to_x, to_y, speed_kof = 1, timeout=0, lenght = 700.0, width = 393.0):
  if x != -1 or y != -1:
    if (x < to_x +40 and x > to_x -40 and y < to_y +40 and y > to_y -40):
      request.Velocity.PanTilt._x = 0
      request.Velocity.PanTilt._y = 0
      ptz.ContinuousMove(request)
    else:
      len_x = -(to_x - x)
      len_y = (to_y - y)
      vec_x = len_x/lenght
      vec_x = int(vec_x*100)/100.0
      vec_x *= speed_kof
      vec_y = len_y/width
      vec_y = int(vec_y*100)/100.0
      vec_y *= speed_kof


      if vec_x > 1:
        vec_x = 1
      if vec_y > 1:
        vec_y = 1
      print (str(vec_y), " : ", str(vec_x))
      request.Velocity.PanTilt._x = vec_x
      request.Velocity.PanTilt._y = vec_y
      ptz.ContinuousMove(request)

  else:
    request.Velocity.PanTilt._x = 0
    request.Velocity.PanTilt._y = 0
    ptz.ContinuousMove(request)



mycam = ONVIFCamera('192.168.11.33', 80, 'admin', 'Supervisor', '/etc/onvif/wsdl/')


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
#old_image_np = cap.read()
threads = []
stream = WebcamVideoStream()
tensor = Tensor()
tensor.start()
tensor2 = Tensor()
tensor2.start()
stream.start()

fps = FPS().start()
persons_num = 0
i = 0
while True:
  i = i + 1
  #print ('----------------------------')
  image_np = stream.read()
  if (not np.array_equal(first,image_np)):
    second = first
    first = image_np
    if i%4 == 0:
      tensor.setImage(image_np)
    elif i%4 == 2:
      tensor2.setImage(image_np)

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
        print (persons_num, ': found person')
        person = persons[0]
        l_w = [width,lenght,width,lenght]
        box = boxes[0][person]

        box = l_w*box
        
        to_x = int(abs(box[1] - box[3])/2.0 + box[1])
        to_y = int(box[0])
        

        mov_to_face(
          ptz, 
          request, 
          to_x, 
          to_y, 
          lenght/3, 
          width/3, 
          speed_kof=2, 
          lenght = lenght_float, 
          width = width_float)
      else:
        mov_to_face(
          ptz, 
          request, 
          -1, 
          -1, 
          lenght/3, 
          width/3, 
          speed_kof=2, 
          lenght = lenght_float, 
          width = width_float)
      

  ''''''
  
  if cv2.waitKey(25) & 0xFF == ord('q'):
    mov_to_face(
          ptz, 
          request, 
          -1, 
          -1, 
          lenght/3, 
          width/3, 
          speed_kof=2, 
          lenght = lenght_float, 
          width = width_float)
    cv2.destroyAllWindows()
    fps.stop()

    print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
    cv2.destroyAllWindows()
    break

    
  
    



