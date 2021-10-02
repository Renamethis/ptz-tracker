# Class for tensorflow
import sys
import numpy as np
import logging
from time import sleep
import tensorflow as tf
from threading import Thread


class Tensor:
    # Initialization
    def __init__(self, model_name="ssd_mobilenet", name="Tensor"):
        self.name = name
        self.flag = False
        self.__logger = logging.getLogger("Main.%s" % (self.name))
        self.__logger.info("Model loading starting")
        self.new_image = None
        self.old_image = None
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
            self.__logger.critical("Model not exists")
            self.running = False
            sys.exit(1)
        self.__logger.info("Model loading completed")

    # Start thread
    def start(self):
        self.running = True
        self.__logger.info("Process starting")
        self.__thread = Thread(target=self.__update, name=self.name, args=())
        self.__thread.daemon = True
        self.__thread.start()

    # Main loop for tensorflow detection
    def __update(self):
        self.__logger.info("Process started")
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
        self.__logger.info("Process stopped")

    # Set image for tensorflow processing
    def set_image(self, image):
        self.new_image = image

    # Return boxes after detection
    def read_boxes(self):
        if self.flag:
            return self.boxes
        else:
            return None

    # Return scores after detection
    def read_scores(self):
        if self.flag:
            return self.scores
        else:
            return None

    # Return classes after detection
    def read_classes(self):
        if self.flag:
            return self.classes
        else:
            return None

    # Stop thread
    def stop(self):
        self.running = False
