# Class for tensorflow
import sys
import numpy as np
import logging
from time import sleep
import tensorflow as tf
from threading import Thread


class Tensor:
    # Initialization
    def __init__(self, width=720, height=405,
                 model_name="ssd_mobilenet", name="Tensor"):
        self.name = name
        self.flag = False
        self.new_image = np.zeros((height, width, 3))
        self.old_image = np.zeros((height, width, 3))
        self.logger = logging.getLogger("Main.%s" % (self.name))
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

    # Main loop for tensorflow detection
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
        self.logger.info("Process stopped")

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
