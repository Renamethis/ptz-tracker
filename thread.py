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

class MyThread(Thread):
  def __init__(self, func, args, name=''):
    Thread.__init__(self)
    self.name = name
    self.func = func
    self.args = args

  def getResult(self):
    return self.res

  def run(self):
    print 'starting', self.name, 'at:', \
    ctime()
    self.res = self.func(*self.args)
    print self.name, 'finished at:', \
    ctime()

class WebcamVideoStream:
  def __init__(self, src='rtsp://192.168.11.52:554/live/av0', name="WebcamVideoStream"):
    #def __init__(self, src='rtsp://192.168.11.33:554', name="WebcamVideoStream"):
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






class Tensor:
  def __init__(self, lenght = 1920, width = 1080, name="Tensor"):
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

    #self.image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
    self.boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
    self.scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
    self.classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
    self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')
    self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')

    #label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
    #categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
    #category_index = label_map_util.create_category_index(categories)
    category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS)
    #cap = cv2.VideoCapture("rtsp://192.168.1.2:8080/out.h264")

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
            self.boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
            self.scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
            self.classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
            self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')
            self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')

            (self.boxes, self.scores, self.classes, self.num_detections) = sess.run(
                [self.boxes, self.scores, self.classes, self.num_detections],
                feed_dict={self.image_tensor: image_np_expanded})
            print 1
            self.old_image = image

  def setImage(self, image):
    self.new_image = image

  def read(self):
    return self.image

  def stop(self):
    self.stopped = True






#cap = VideoStream(src='rtsp://192.168.11.33:554').start()



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
#with detection_graph.as_default():
#  with tf.Session(graph=detection_graph) as sess:
i = 0
while True:
  i = i + 1
  print ('----------------------------')
  #new_image_np = cap.read()

  image_np = stream.read()
  #ret, image_np = cap.read()s
  #print image_np.shape

  if (not np.array_equal(first,image_np)):
    second = first
    first = image_np
    if i%4 == 0:
      tensor.setImage(image_np)
    elif i%4 == 2:
      tensor2.setImage(image_np)

  '''  
  if i%2 == 0:
    tensor.setImage(image_np)
  else:
    tensor2.setImage(image_np)
  '''


  #print np.zeros((width, lenght, 3))
  #image_np = cv2.resize(image_np, (lenght,width))


  cv2.imshow('object detection', image_np)
  if cv2.waitKey(25) & 0xFF == ord('q'):
    cv2.destroyAllWindows()
    fps.stop()

    print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
    cv2.destroyAllWindows()
    break
  fps.update()
    



