# Class for tensorflow
import sys
import numpy as np
import logging
from time import sleep
import tensorflow as tf
from threading import Thread


class Tensor:
    # Initialization
    def __init__(self, length=720, hight=405,
                 model_name="ssd_mobilenet", name="Tensor"):
        self.name = name
        self.dellay = 0
        self.flag = False
        self.arr = []
        self.new_image = np.zeros((hight, length, 3))
        self.old_image = np.zeros((hight, length, 3))
        self.stopped = False
        self.count = 0

        self.logger = logging.getLogger("Main.%s.init" % (self.name))
        self.logger.info("Model loading starting")
        try:
            self.model_name = model_name
            PATH_TO_MODEL = "models/" + model_name
            # PATH_TO_LABELS = "models/label_map.pbtxt"

            self.detector = tf.saved_model.load(PATH_TO_MODEL)
            self.boxes = None
            self.scores = None
            self.classes = None
            self.num_detections = None
        except OSError:
            self.logger.critical("Model not exists")
            self.running = False
            sys.exit(1)
        self.logger.info("Model loading completed")

    # Start thread
    def start(self):
        self.running = True
        self.logger.info("Process starting")
        self.t = Thread(target=self.update, name=self.name, args=())
        self.t.daemon = True
        self.t.start()
        return self

    # Image processing cycle
    def update(self):
        self.logger.info("Process started")
        while self.running:
            image = self.new_image
            if not np.array_equal(image, self.old_image) and image is not None:
                tensor = tf.convert_to_tensor(image)
                tensor = tensor[tf.newaxis, ...]
                tensor = tensor[:, :, :, :3]
                detections = self.detector(tensor)
                self.boxes = detections['detection_boxes']
                self.scores = detections['detection_scores']
                self.classes = detections['detection_classes']
                self.num_detections = detections['num_detections']
                self.flag = True
                self.old_image = image
            else:
                self.flag = False
                sleep(0.05)

    def set_image(self, image):
        self.new_image = image

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

    def stop(self):
        self.stopped = True
