import smtplib
import traceback
import sys



import numpy as np
import logging
import tarfile
import time
from time import sleep
import tensorflow.compat.v1 as tf
import Utility_Functions as UF
from threading import Thread

class Tensor:
  # 4.1. Initialization
  def __init__(self, visible, length = 720, hight = 405, model_name = 'ssd_mobilenet_v2_coco_2018_03_29', name="Tensor"):
    tf.disable_v2_behavior()
    self.name       = name
    self.dellay     = 0
    self.flag       = False
    self.arr        = []
    self.new_image  = np.zeros((hight, length, 3))
    self.old_image  = np.zeros((hight, length, 3))
    self.stopped    = False
    self.visible    = visible
    self.count      = 0

    init_logger = logging.getLogger("Main.%s.init" % (self.name))

    try:
      pwd = UF.get_pwd("detection_models")
      self.model_name = model_name
      PATH_TO_FROZEN_GRAPH = pwd + '/' + self.model_name + '.pb'
      PATH_TO_LABELS = pwd + '/mscoco_label_map.pbtxt'


      self.detection_graph = tf.Graph()
      with self.detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
          serialized_graph = fid.read()
          od_graph_def.ParseFromString(serialized_graph)
          tf.import_graph_def(od_graph_def, name='')


      self.boxes          = self.detection_graph.get_tensor_by_name('detection_boxes:0')
      self.scores         = self.detection_graph.get_tensor_by_name('detection_scores:0')
      self.classes        = self.detection_graph.get_tensor_by_name('detection_classes:0')
      self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')
      self.image_tensor   = self.detection_graph.get_tensor_by_name('image_tensor:0')
    except:
      init_logger.critical("Error in %s.__init__" % (self.name))
      init_logger.exception("Error!")
      exc_type, exc_value, exc_traceback = sys.exc_info()
      err_msg = str(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
      #UF.send_msg(msg=err_msg)
      sys.exit(0)


  # 4.2. Start thread
  def start(self):
    self.stopped = False
    start_logger = logging.getLogger("Main.%s.start" % (self.name))
    start_logger.info("Process starting")
    self.t = Thread(target=self.update, name=self.name, args=())
    self.t.daemon = True
    self.t.start()
    return self

  # 4.3. Infinite image processing cycle
  def update(self):
    try:
      update_logger = logging.getLogger("Main.%s.update" % (self.name))
      update_logger.info("Process started")
      i = 0
      count = 0
      err = 0
      dellay = 0
      with self.detection_graph.as_default():
        with tf.Session(graph=self.detection_graph) as sess:
          while True:
            image = self.new_image
            if self.stopped:
              return
            if not np.array_equal(image,self.old_image) and image is not None:




              time_1 = time.time()
              image_np_expanded = np.expand_dims(image, axis=0)
              boxes             = self.detection_graph.get_tensor_by_name('detection_boxes:0')
              scores            = self.detection_graph.get_tensor_by_name('detection_scores:0')
              classes           = self.detection_graph.get_tensor_by_name('detection_classes:0')
              num_detections    = self.detection_graph.get_tensor_by_name('num_detections:0')
              self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
              try:
                (self.boxes, self.scores, self.classes, self.num_detections) = sess.run(
                    [boxes, scores, classes, num_detections],
                    feed_dict={self.image_tensor: image_np_expanded})
              except:
                update_logger.critical("Error with run tensor")
                update_logger.exception("Error!")
                exc_type, exc_value, exc_traceback = sys.exc_info()
                err_msg = str(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
                #UF.send_msg(msg=err_msg)

              if (self.visible == 'Yes'):
                '''
                vis_util.visualize_boxes_and_labels_on_image_array(
                  image,
                  np.squeeze(self.boxes),
                  np.squeeze(self.classes).astype(np.int32),
                  np.squeeze(self.scores),
                  self.category_index,
                  use_normalized_coordinates=True,
                  line_thickness=8)
                '''
              time_2 = time.time()
              err =  time_2 - time_1
              dellay = dellay + err
              count = count + 1
              if count == 10:
                self.dellay = dellay
                #print dellay
                self.count = count
                dellay = 0
                count = 0


              self.flag = True
              self.old_image = image
            else:
              sleep(0.1)
    except:
      update_logger.critical("Error in process")
      update_logger.exception("Error!")
      exc_type, exc_value, exc_traceback = sys.exc_info()
      err_msg = str(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
      print(err_msg)
      sys.exit(0)

  def set_image(self, image):
    self.new_image = image


  def read(self):
    if self.flag:
      return self.old_image
    else:
      return None


  def read_boxes(self):
    if self.flag:
      return self.boxes
    else:
      return None


  def read_scores(self):
    if self.flag:
      return self.scores
    else:
      return None


  def read_classes(self):
    if self.flag:
      return self.classes
    else:
      return None

  def status(self):
    try:
      return self.t.isAlive()
    except:
      return False
  def get_tps(self):
    try:
      result = (float(self.count) / self.dellay)
    except:
      result = 0
    return result



  def stop(self):
    self.stopped = True
