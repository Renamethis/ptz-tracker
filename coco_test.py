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


detection_graph = tf.Graph()
with detection_graph.as_default():
  od_graph_def = tf.GraphDef()
  with tf.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
    serialized_graph = fid.read()
    od_graph_def.ParseFromString(serialized_graph)
    tf.import_graph_def(od_graph_def, name='')

category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS)

print('complite load model')


print ('conection with camera...')
'''
cap = VideoStream(src='rtsp://192.168.11.51:554/live/av0').start()
mycam = ONVIFCamera('192.168.11.52', 2000, 'admin', 'Supervisor', '/home/ilya/git/MM.Tracker/venv/wsdl')
'''
cap = VideoStream(src='rtsp://192.168.11.33:554/Streaming/Channels/1').start()
mycam = ONVIFCamera('192.168.11.33', 80, 'admin', 'Supervisor', '/home/ilya/git/MM.Tracker/venv/wsdl')
media = mycam.create_media_service()
profile = media.GetProfiles()[0]
ptz = mycam.create_ptz_service()
request = ptz.create_type('GetConfigurationOptions')
request.ConfigurationToken = profile.PTZConfiguration._token
ptz_configuration_options = ptz.GetConfigurationOptions(request)
request = ptz.create_type('ContinuousMove')
request.ProfileToken = profile._token

print ('sucsess conection.')


goal_person = ['person',-1,-1,-1]
lenght_float = 1280.0
width_float = 720.0
lenght = int(lenght_float)
width = int(width_float)

fps = FPS().start()
with detection_graph.as_default():
  with tf.Session('',detection_graph,None) as sess:
    image_np = cap.read()
    image_np = cv2.resize(image_np, (lenght,width))
    
    image_np_expanded = np.expand_dims(image_np, axis=0)
    print 'np: ',image_np_expanded.shape
    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
    print 'image_tensor: ',image_tensor
    boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
    print 'boxes: ',boxes
    scores = detection_graph.get_tensor_by_name('detection_scores:0')
    classes = detection_graph.get_tensor_by_name('detection_classes:0')
    print 'classes: ',classes
    num_detections = detection_graph.get_tensor_by_name('num_detections:0')

    (boxes, scores, classes, num_detections) = sess.run(
          [boxes, scores, classes, num_detections],
          feed_dict={image_tensor: image_np_expanded})

    print 'classes: ',np.argwhere(classes == 1)
    print 'scores: ',scores
    print 'boxes: ',boxes
    print 'num_detections: ',num_detections



