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




def init():
  MODEL_NAME = 'ssd_mobilenet_v2_coco_2018_03_29'
  MODEL_FILE = MODEL_NAME + '.tar.gz'
  DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'


  # Path to frozen detection graph. This is the actual model that is used for the object detection.
  PATH_TO_FROZEN_GRAPH = MODEL_NAME + '/frozen_inference_graph.pb'

  # List of the strings that is used to add correct label for each box.
  PATH_TO_LABELS = os.path.join('data', 'mscoco_label_map.pbtxt')


  #opener = urllib.request.URLopener()
  #opener.retrieve(DOWNLOAD_BASE + MODEL_FILE, MODEL_FILE)
  tar_file = tarfile.open(MODEL_FILE)
  for file in tar_file.getmembers():
    file_name = os.path.basename(file.name)
    if 'frozen_inference_graph.pb' in file_name:
      tar_file.extract(file, os.getcwd())


  detection_graph = tf.Graph()
  with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
      serialized_graph = fid.read()
      od_graph_def.ParseFromString(serialized_graph)
      tf.import_graph_def(od_graph_def, name='')


  #label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
  #categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
  #category_index = label_map_util.create_category_index(categories)
  category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS)


  print ('conection with camera...')
  return detection_graph, tf



def loop0(detection_graph, tf):	
  #cap = VideoStream(src='rtsp://192.168.1.102:554/Streaming/Channels/101').start()
  ##cap = VideoStream(src='rtsp://192.168.11.52:554/live/av0').start()
  #cap = VideoStream(src='rtsp://192.168.11.42:554/Streaming/Channels/101?transportmode=unicast&profile=Profile_1').start()

  ##mycam = ONVIFCamera('192.168.11.52', 2000, 'admin', 'Supervisor', '/home/ilya/git/MM.Tracker/venv/wsdl')

  image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
  boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
  scores = detection_graph.get_tensor_by_name('detection_scores:0')
  classes = detection_graph.get_tensor_by_name('detection_classes:0')
  num_detections = detection_graph.get_tensor_by_name('num_detections:0')
  cap = VideoStream(src='rtsp://192.168.11.51:554/live/av0').start()


  lenght_float = 1280.0
  width_float = 720.0

  lenght = int(lenght_float)
  width = int(width_float)
  fps = FPS().start()
  with detection_graph.as_default():
    with tf.Session(graph=detection_graph) as sess:
      while True:    
        print ('----------------------------')
        image_np = cap.read()
        image_np = cv2.resize(image_np, (lenght,width))
        print ('image_np sucsess')

        image_np_expanded = np.expand_dims(image_np, axis=0)
        
        print (' sucsess')

        (boxes, scores, classes, num_detections) = sess.run(
          [boxes, scores, classes, num_detections],
          feed_dict={image_tensor: image_np_expanded})
        print ('read sucsess')
        print boxes
        print scores
        print classes
        print num_detections
        cv2.imshow('object detection', image_np)
        if cv2.waitKey(25) & 0xFF == ord('q'):
          cv2.destroyAllWindows()
          fps.stop()


          print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
          print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
          cv2.destroyAllWindows()
          break
        fps.update()

def loop1():
  while True:
  	print 'loop1'
  	sleep(10)


detection_graph, tf = init()
threads = []
t = threading.Thread(target=loop0, args = (detection_graph, tf))
threads.append(t)
threads[0].start()
t2 = threading.Thread(target=loop1)
threads.append(t2)
threads[1].start()
threads[0].join()
threads[1].join()