# Class for tensorflow
import traceback
import sys
import numpy as np
import logging
import time
from time import sleep
import tensorflow as tf
import Utility_Functions as UF
from threading import Thread


class Tensor:
    # Initialization
    def __init__(self, length=720, hight=405,
                 model_name="ssd_mobilenet", name="Tensor"):
        self.running = True
        self.name = name
        self.dellay = 0
        self.flag = False
        self.arr = []
        self.new_image = np.zeros((hight, length, 3))
        self.old_image = np.zeros((hight, length, 3))
        self.stopped = False
        self.count = 0

        init_logger = logging.getLogger("Main.%s.init" % (self.name))

        try:
            pwd = UF.get_pwd("models")
            self.model_name = model_name
            PATH_TO_MODEL = pwd + '/' + model_name
            PATH_TO_LABELS = pwd + '/label_map.pbtxt'

            self.detector = tf.saved_model.load(PATH_TO_MODEL)
            self.boxes = None
            self.scores = None
            self.classes = None
            self.num_detections = None
        except:
            init_logger.critical("Error in %s.__init__" % (self.name))
            init_logger.exception("Error!")
            self.running = False

    # Start thread
    def start(self):
        self.stopped = False
        start_logger = logging.getLogger("Main.%s.start" % (self.name))
        start_logger.info("Process starting")
        self.t = Thread(target=self.update, name=self.name, args=())
        self.t.daemon = True
        self.t.start()
        return self

    # Image processing cycle
    def update(self):
        try:
            update_logger = logging.getLogger("Main.%s.update" % (self.name))
            update_logger.info("Process started")
            i = 0
            count = 0
            err = 0
            dellay = 0
            while True:
                image = self.new_image
                if self.stopped:
                    return
                if not np.array_equal(image,self.old_image) and image is not None:
                    try:
                        tensor = tf.convert_to_tensor(image)
                        tensor = tensor[tf.newaxis, ...]
                        tensor = tensor[:, :, :, :3]
                        detections = self.detector(tensor)
                        self.boxes = detections['detection_boxes']
                        self.scores = detections['detection_scores']
                        self.classes = detections['detection_classes']
                        self.num_detections = detections['num_detections']
                    except:
                        update_logger.critical("Error with run tensor")
                        update_logger.exception("Error!")
                    self.flag = True
                    self.old_image = image
                else:
                    sleep(0.05)
        except:
            update_logger.critical("Error in process")
            update_logger.exception("Error!")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err_msg = str(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
            print(err_msg)
            self.running = False

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
