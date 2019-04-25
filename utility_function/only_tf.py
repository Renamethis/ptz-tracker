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

sys.path.append("..")

from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util




MODEL_NAME = 'ssd_mobilenet_v2_face'
MODEL_FILE = MODEL_NAME + '.tar.gz'
DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'
PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'
PATH_TO_LABELS = os.path.join('data', 'mscoco_label_map.pbtxt')
NUM_CLASSES = 90


detection_graph = tf.Graph()
with detection_graph.as_default():
  od_graph_def = tf.GraphDef()
  with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
    serialized_graph = fid.read()
    od_graph_def.ParseFromString(serialized_graph)
    tf.import_graph_def(od_graph_def, name='')


label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)




print ('conection with camera...')
#cap = VideoStream(src='rtsp://192.168.11.33').start()
#cap = VideoStream(src='rtsp://192.168.1.102:554/Streaming/Channels/101').start()
cap = VideoStream(src=0).start()
#mycam = ONVIFCamera('192.168.1.102', 80, 'admin', 'Supervisor', '/etc/onvif/wsdl/')
#mycam = ONVIFCamera('192.168.11.33', 80, 'admin', 'Supervisor', '/etc/onvif/wsdl/')

#mycam = ONVIFCamera('172.16.83.102:554', 80, 'admin', 'Supervisor')
#mycam = ONVIFCamera('192.168.13.12', 80, 'admin', 'Supervisor')
'''media = mycam.create_media_service()
profile = media.GetProfiles()[0]
ptz = mycam.create_ptz_service()
request = ptz.create_type('GetConfigurationOptions')
request.ConfigurationToken = profile.PTZConfiguration._token
ptz_configuration_options = ptz.GetConfigurationOptions(request)
request = ptz.create_type('ContinuousMove')
request.ProfileToken = profile._token'''

print ('sucsess conection.')




goal_person = ['person',-1,-1,-1]
lenght_float = 1280.0
width_float = 720.0
lenght = int(lenght_float)
width = int(width_float)


fps = FPS().start()
with detection_graph.as_default():
  with tf.Session(graph=detection_graph) as sess:
    while True:
      print ('--')
      image_np = cap.read()
      image_np = cv2.resize(image_np, (lenght,width))


      cv2.rectangle(image_np,(lenght/3 - 30, width/3 -30),
        (lenght/3 + 30,width/3 + 30),(100,100,100),2)
      cv2.rectangle(image_np,(2*lenght/3 - 30, width/3 -30),
        (2*lenght/3 + 30,width/3 + 30),(100,100,100),2)
      cv2.rectangle(image_np,(lenght/3 - 30, 2*width/3 -30),
        (lenght/3 + 30,2*width/3 + 30),(100,100,100),2)
      cv2.rectangle(image_np,(2*lenght/3 - 30, 2*width/3 -30),
        (2*lenght/3 + 30,2*width/3 + 30),(100,100,100),2)

      
      image_np_expanded = np.expand_dims(image_np, axis=0)
      image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
      boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
      scores = detection_graph.get_tensor_by_name('detection_scores:0')
      classes = detection_graph.get_tensor_by_name('detection_classes:0')
      num_detections = detection_graph.get_tensor_by_name('num_detections:0')


      (boxes, scores, classes, num_detections) = sess.run(
          [boxes, scores, classes, num_detections],
          feed_dict={image_tensor: image_np_expanded})


      final_list = vis_util.visualize_boxes_and_labels_on_image_array(
          image_np,
          np.squeeze(boxes),
          np.squeeze(classes).astype(np.int32),
          np.squeeze(scores),
          category_index,
          use_normalized_coordinates=True,
          line_thickness=8)
      '''goal_person = ['person',-1,-1,-1]
      count = 0
      for i in range(len(final_list)):
        final_list[i][2] *= lenght
        final_list[i][3] *= width
        final_list[i][4] *= lenght
        final_list[i][5] *= width
        if final_list[i][0] == 'person' and goal_person[1] < final_list[i][1]:
          count += 1
          s[1] = final_list[i][1]
          goal_person[2] = int(abs(final_list[i][2] - final_list[i][4])/2.0 + final_list[i][4])
          goal_person[3] = int(final_list[i][5])
          break'''
      #print ("person: ", str(count))
      #print (len(final_list))
      #print (goal_person)


      cv2.imshow('object detection', image_np)
      if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        fps.stop()


        ptz.Stop({'ProfileToken': request.ProfileToken})


        print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
        cv2.destroyAllWindows()
        break
      fps.update()
