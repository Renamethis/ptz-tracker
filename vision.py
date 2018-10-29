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



#t model to download.
#MODEL_NAME = 'ssd_mobilenet_v1_coco_2017_11_17'
#MODEL_FILE = MODEL_NAME + '.tar.gz'
#DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'
#http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v1_fpn_shared_box_predictor_640x640_coco14_sync_2018_07_03.tar.gz
#http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v2_coco_2018_03_29.tar.gz
#http://download.tensorflow.org/models/object_detection/ssd_inception_v2_coco_2018_01_28.tar.gz
#http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v1_fpn_shared_box_predictor_640x640_coco14_sync_2018_07_03.tar.gz
#http://download.tensorflow.org/models/object_detection/ssd_resnet50_v1_fpn_shared_box_predictor_640x640_coco14_sync_2018_07_03.tar.gz
#http://download.tensorflow.org/models/object_detection/faster_rcnn_nas_coco_2018_01_28.tar.gz
#http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v1_0.75_depth_300x300_coco14_sync_2018_07_03.tar.gz
#http://download.tensorflow.org/models/object_detection/faster_rcnn_resnet101_ava_v2.1_2018_04_30.tar.gz
#http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v1_0.75_depth_quantized_300x300_coco14_sync_2018_07_18.tar.gz
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


'''

def mov_to_face(ptz, request, x, y, to_x, to_y, speed_kof = 1, timeout=0, lenght = 700.0, width = 393.0):
  centr_x = 114.0
  centr_y = -116.0
  mov_x = 1899.0
  mov_y = 3937.0

  if x != -1 or y != -1:
    camera_x = ptz.GetStatus().Position.PanTilt._x
    camera_y = ptz.GetStatus().Position.PanTilt._y
    
    camera_x = camera_x * 10000
    camera_y = camera_y * 10000


    len_x = (centr_x - mov_x + (mov_x*2/lenght)*x-camera_x)
    len_y = (centr_y + mov_y - (mov_y*2/width)*y-camera_y)
    #len_y = -(camera_y - centr_y + mov_y + (mov_y*2/width)*y)


    vec_x = len_x/(mov_x*2)
    vec_x = int(vec_x*100)/100.0
    vec_y = len_y/(mov_y*2)
    vec_y = int(vec_y*100)/100.0
    

    if vec_y > 1.0:
      vec_y = 1.0
    if vec_y < -1.0:
      vec_y = -1.0
    if vec_x > 1.0:
      vec_x = 1.0
    if vec_x < -1.0:
      vec_x = -1.0

    print (vec_x, " : ", vec_y)

    request.Velocity.PanTilt._x = vec_x * speed_kof
    request.Velocity.PanTilt._y = vec_y * speed_kof#/((mov_y*2/width)/(mov_x*2/lenght))
    ptz.ContinuousMove(request)
    
  else:
    request.Velocity.PanTilt._x = 0.00001
    request.Velocity.PanTilt._y = 0.00001
    print ('stop')
    ptz.ContinuousMove(request)
    print ('stop')
'''
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




print ('conection with camera...')
#
#cap = VideoStream(src='rtsp://192.168.1.102:554/Streaming/Channels/101').start()
##cap = VideoStream(src='rtsp://192.168.11.52:554/live/av0').start()
#cap = VideoStream(src='rtsp://192.168.11.42:554/Streaming/Channels/101?transportmode=unicast&profile=Profile_1').start()

##mycam = ONVIFCamera('192.168.11.52', 2000, 'admin', 'Supervisor', '/home/ilya/git/MM.Tracker/venv/wsdl')


cap = VideoStream(src='rtsp://192.168.11.42:554').start()
mycam = ONVIFCamera('192.168.11.42', 80, 'admin', 'Supervisor', '/home/ilya/git/MM.Tracker/venv/wsdl')


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
  with tf.Session(graph=detection_graph) as sess:
    while True:
      print ('----------------------------')
      image_np = cap.read()
      image_np = cv2.resize(image_np, (lenght,width))
      print ('image_np sucsess')


      cv2.rectangle(image_np,(lenght/3 - 30, width/3 -30),
        (lenght/3 + 30,width/3 + 30),(100,100,100),2)
      cv2.rectangle(image_np,(2*lenght/3 - 30, width/3 -30),
        (2*lenght/3 + 30,width/3 + 30),(100,100,100),2)
      cv2.rectangle(image_np,(lenght/3 - 30, 2*width/3 -30),
        (lenght/3 + 30,2*width/3 + 30),(100,100,100),2)
      cv2.rectangle(image_np,(2*lenght/3 - 30, 2*width/3 -30),
        (2*lenght/3 + 30,2*width/3 + 30),(100,100,100),2)
      print ('rectangle sucsess')
      
      image_np_expanded = np.expand_dims(image_np, axis=0)
      image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
      boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
      scores = detection_graph.get_tensor_by_name('detection_scores:0')
      classes = detection_graph.get_tensor_by_name('detection_classes:0')
      num_detections = detection_graph.get_tensor_by_name('num_detections:0')
      print (' sucsess')

      (boxes, scores, classes, num_detections) = sess.run(
          [boxes, scores, classes, num_detections],
          feed_dict={image_tensor: image_np_expanded})
      print ('read sucsess')

      final_list = vis_util.visualize_boxes_and_labels_on_image_array(
          image_np,
          np.squeeze(boxes),
          np.squeeze(classes).astype(np.int32),
          np.squeeze(scores),
          category_index,
          use_normalized_coordinates=True,
          line_thickness=8)
      print ('final_list sucsess')
      goal_person = ['person',-1,-1,-1]
      count = 0
      for i in range(len(final_list)):
        final_list[i][2] *= lenght
        final_list[i][3] *= width
        final_list[i][4] *= lenght
        final_list[i][5] *= width
        if final_list[i][0] == 'person' and goal_person[1] < final_list[i][1]:
          count += 1
          goal_person[1] = final_list[i][1]
          goal_person[2] = int(abs(final_list[i][2] - final_list[i][4])/2.0 + final_list[i][4])
          goal_person[3] = int(final_list[i][5])
          break
      #os.system('clear')          
      if count != 0:  
        print ("person: ", str(count))
        print (len(final_list))
        print (goal_person)
      '''

      mov_to_face(
        ptz, 
        request, 
        goal_person[2], 
        goal_person[3], 
        lenght/3, 
        width/3, 
        speed_kof=0.5, 
        lenght = lenght_float, 
        width = width_float)
      '''

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

