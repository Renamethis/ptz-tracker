class Tensor:
  def __init__(self, lenght = 1280, width = 720, name="Tensor"):
    self.flag = False
    self.arr = []
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
    self.boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
    self.scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
    self.classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
    self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')
    self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
    category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS)
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
            boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
            scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
            classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
            num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')
            self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
            (self.boxes, self.scores, self.classes, self.num_detections) = sess.run(
                [boxes, scores, classes, num_detections],
                feed_dict={self.image_tensor: image_np_expanded})
            #print 1
            self.flag = True
            self.old_image = image
  def setImage(self, image):
    self.new_image = image
  def read(self):
    if self.flag:
      return self.new_image
    else:
      return self.arr
  def read_boxes(self):
    if self.flag:
      return self.boxes
    else:
      return self.arr
  def read_scores(self):
    if self.flag:
      return self.scores
    else:
      return self.arr
  def read_classes(self):
    if self.flag:
      return self.classes
    else:
      return self.arr
  def stop(self):
    self.stopped = True
