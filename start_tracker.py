try:
  ###
  ## add_try  - add validation
  ## modify   - it is possible to change
  ## add_func - add function
  ## error    - error 
  ### 



  ################################
  # 1. Starting the virtual environment
  ################################

  # add_func (execute the command: "export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/slim")

  activate_this_file = "venv/bin/activate_this.py"
  execfile(activate_this_file, dict(__file__=activate_this_file))
  import sys
  import os
  os.system('cp -f utility_function/mobilenet_v1.py models/research/slim/nets/') 
  os.system('cp -f utility_function/visualization_utils.py models/research/object_detection/utils/') 
  os.chdir('models/research')
  os.chdir('object_detection')

  ################################
  # 2. Loading the libraries
  ################################

  # add_try (checking libraries)

  import numpy as np
  import math
  import cv2
  import six.moves.urllib as urllib
  import tarfile
  import smtplib
  import time
  import base64
  import traceback
  import tensorflow as tf
  import configparser
  from imutils.video import FPS
  from onvif import ONVIFCamera
  from time import sleep
  from threading import Thread
  from object_detection.utils import label_map_util
  from object_detection.utils import visualization_utils as vis_util

  ################################
  # 3. The process of taking a frame from a stream
  ################################

  class WebcamVideoStream:
    # 3.1. Initialization
    def __init__(self, name="WebcamVideoStream"):
      
      # 3.1.1. Determining the path to the configuration file
      # add_try (count >= 3)

      pwd = os.getcwd()
      lst = pwd.split('/')
      count = len(lst)-3
      string = ""
      for i in range(count):
        string = string + lst[i] + "/"
      pwd = string

      # 3.1.2. Read configuration file (rtsp)
      # add_try (checking file existence)
      # add_try (check the existence of settings in Conf. file)
      # modify (receiving rtsp from camera)

      config = configparser.ConfigParser()
      config.read(pwd + "conf/settings.ini")
      mycam_rtsp = config.get("Settings","rtsp")

      # 3.1.3. Sturt function cv2.VideoCapture
      # modify (replace print with logging)
      
      try:
        self.stream = cv2.VideoCapture(mycam_rtsp)
        print "[INFO]     Successful conection VideoCapture"
      except:
        err_msg = "[ERROR]    Error with cv2.VideoCapture..."
        print err_msg
        print "[INFO]     Check the correctness of the entered data in the setings.ini (rtsp)"
        send_msg(msg=err_msg)
        sys.exit(0)


      # 3.1.4. Read frame
      (self.grabbed, self.frame) = self.stream.read()
      print self.frame
      self.name = name
      self.stopped = False

    # 3.2. Start thread
    def start(self):
      t = Thread(target=self.update, name=self.name, args=())
      t.daemon = True
      t.start()
      return self

    # 3.3. Infinite loop of receiving frames from a stream
    def update(self):
      stream = self.stream
      print "[INFO]     VideoCapture started"
      i = 0
      time_1 = time.time()
      while True:
        #print 1
        if self.stopped:
          print "[INFO]     VideoCapture stopped"
          return
        (self.grabbed, self.frame) = stream.read()
        i = i + 1
        if (i == 25):
          time_2 = time.time()
          #print time_1 - time_2
          i = 0
          time_1 = time.time()

    # 3.4. Get frame
    def read(self):
      return self.frame

    # 3.5. Stop frame
    def stop(self):
      self.stopped = True


  ################################
  # 4. The process of tensor
  ################################

  class Tensor:
    # 4.1. Initialization
    def __init__(self, lenght = 1280, width = 720, model_name = 'ssd_mobilenet_v2_coco_2018_03_29', name="Tensor"):
      self.flag       = False
      self.arr        = []
      self.name       = name
      self.new_image  = np.zeros((width, lenght, 3))
      self.old_image  = np.zeros((width, lenght, 3))
      self.stopped    = False

      # modify (add models in folder, copy, without tar)
      MODEL_NAME = model_name
      MODEL_FILE = MODEL_NAME + '.tar.gz'
      PATH_TO_FROZEN_GRAPH = MODEL_NAME + '/frozen_inference_graph.pb'
      PATH_TO_LABELS = os.path.join('data', 'mscoco_label_map.pbtxt')


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


      self.boxes          = self.detection_graph.get_tensor_by_name('detection_boxes:0')
      self.scores         = self.detection_graph.get_tensor_by_name('detection_scores:0')
      self.classes        = self.detection_graph.get_tensor_by_name('detection_classes:0')
      self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')
      self.image_tensor   = self.detection_graph.get_tensor_by_name('image_tensor:0')
      self.category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS)


    # 4.2. Start thread
    def start(self):
      t = Thread(target=self.update, name=self.name, args=())
      t.daemon = True
      t.start()
      return self

    # 4.3. Infinite image processing cycle
    def update(self):
      print "[INFO]     Tensor started"
      with self.detection_graph.as_default():
        with tf.Session(graph=self.detection_graph) as sess:
          while True:
            image = self.new_image
            if self.stopped:
              return
            if not np.array_equal(image,self.old_image):

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
                print '[ERROR]     Run tensor error...'
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
              self.flag = True
              self.old_image = image
          print "[INFO]     Tensor stopped"


    def setImage(self, image):
      self.new_image = image


    def read(self):
      if self.flag:
        return self.old_image
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
  

  def send_msg(msg,SUBJECT="Error",TO="prostepm21@gmail.com"):
    HOST="smtp.gmail.com"
    FROM = "tensorflow21@gmail.com"
    BODY = "\r\n".join((
      "From: %s" % FROM,
      "To: %s" % TO,
      "Subject: %s" % SUBJECT ,
      "",
      msg
    ))

    server = smtplib.SMTP(HOST, 587)
    server.starttls()
    server.login(FROM, base64.b64decode('VGVuc29yNTUyMQ=='))
    server.sendmail(FROM, [TO], BODY)
    server.quit()


  def initTracker(stream, tensor):
    print "[INFO]     Start init"
    flag = True
    lenght_float = 1280.0 
    width_float = 720.0
    lenght = int(lenght_float)
    width = int(width_float)
    frame_count = 0
    x1 = 0
    x2 = 0
    while flag:
      image_np = stream.read()
      image_np = cv2.resize(image_np, (lenght,width))
      tensor.setImage(image_np)
      
      scores = tensor.read_scores()
      image_np = tensor.read()
      classes = tensor.read_classes()
      boxes = tensor.read_boxes()
      
      if (scores <> []):
        scores[scores > 0] = 1
        
        classes = classes*scores

        persons = np.where(classes == 1)[1]

        if (str(persons) <> '[]'):
          classes = tensor.read_classes()
          #print (persons_num, ': found person')
          person = persons[0]
          l_w = [width,lenght,width,lenght]
          box = boxes[0][person]
          #print box 

          if (box[1] > 0.05 and box[3] < 0.95):
            frame_count = frame_count + 1
            x1 = x1 + box[1]
            x2 = x2 + box[3]
          else:
            frame_count = 0
            x1 = 0
            x2 = 0

          if frame_count >= 50:
            return round((x2/50 - x1/50) *100)


  def main():
    image_np_old = []
    stream = WebcamVideoStream()
    tensor_person = Tensor(model_name = 'ssd_mobilenet_v2_coco_2018_03_29')
    tensor_face = Tensor(model_name = 'ssd_mobilenet_v2_face')
    stream.start()
    tensor_person.start()
    tensor_face.start()
    face_rec = True
    person_rec = False


    lenght_float = 1280.0 
    width_float = 720.0
    lenght = int(lenght_float)
    width = int(width_float)

    pwd = os.getcwd()
    lst = pwd.split('/')
    count = len(lst)-3
    string = ""
    for i in range(count):
      string = string + lst[i] + "/"
    pwd = string


    config = configparser.ConfigParser()
    config.read(pwd + "conf/settings.ini")
    mycam_ip        = config.get("Settings","ip")
    mycam_port      = config.get("Settings","port")
    mycam_login     = config.get("Settings","login")
    mycam_password  = config.get("Settings","password")
    mycam_wsdl_path = config.get("Settings","wsdl_path")


    try:
      mycam = ONVIFCamera(mycam_ip, mycam_port, mycam_login, mycam_password, mycam_wsdl_path)
      print "[INFO]     Successful conection ONVIFCamera"
    except:
      err_msg = "[ERROR]    Error with conect ONVIFCamera..."
      print err_msg
      print "[INFO]     Check the correctness of the entered data in the setings.ini (ip,port,login, password or wsdl_path)"
      send_msg(msg=err_msg)
      sys.exit(0)


    media = mycam.create_media_service()
    profile = media.GetProfiles()[0]
    ptz = mycam.create_ptz_service()
    request = ptz.create_type('GetConfigurationOptions')
    request.ConfigurationToken = profile.PTZConfiguration._token
    ptz_configuration_options = ptz.GetConfigurationOptions(request)
    request = ptz.create_type('ContinuousMove')
    request.ProfileToken = profile._token
    send_msg(msg = "Started",SUBJECT="Info")
    while True:
      image_np = stream.read()
      #print image_np
      if (image_np is not None):
        image_np = cv2.resize(image_np, (1280,720))


        if (not np.array_equal(image_np_old,image_np)):
          image_np_old = image_np
          
          if (face_rec):
            tensor_face.setImage(image_np)
          
            scores   = tensor_face.read_scores()
            
            image_np = tensor_face.read()
            classes  = tensor_face.read_classes()
            boxes    = tensor_face.read_boxes()

          elif (person_rec):
            tensor_person.setImage(image_np)

            scores   = tensor_person.read_scores()
            image_np = tensor_person.read()
            classes  = tensor_person.read_classes()
            boxes    = tensor_person.read_boxes()

          else:
            err_msg = "[ERROR]     face tracker and people tracking off..."
            print err_msg
            send_msg(msg=err_msg)
            sys.exit(0)

          if (scores <> [] and (person_rec or face_rec)):
            scores[scores > 0.2] = 1
            classes = classes*scores
            persons   = np.where(classes == 1)[1]
            #print persons
            

            if (str(persons) <> '[]'):

              person = persons[0]
              l_w = [width,lenght,width,lenght]
              box = boxes[0][person]

              box = l_w*box
              
              to_x = int(abs(box[1] - box[3])/2.0 + box[1])
              to_y = int(box[0])
              
              
              if (to_x < lenght/3 - 80 or to_x > lenght/3 + 80):
                vec_x = float(to_x - lenght/3)/(lenght)
              else:
                vec_x = 0
              if (to_y < width/3 - 80 or to_y > width/3 + 80):
                vec_y = float(width/3 - to_y)/(width)
              else:
                vec_y = 0

              #print vec_x
              #print vec_y
              speed_kof = 0.5

              request.Velocity.PanTilt._x = vec_x*speed_kof
              request.Velocity.PanTilt._y = vec_y*speed_kof
              try:
                ptz.ContinuousMove(request)
              except:
                sleep(1)
                try:
                  mycam = ONVIFCamera(mycam_ip, mycam_port, mycam_login, mycam_password, mycam_wsdl_path)
                  print "[INFO]     Successful conection ONVIFCamera"
                except:
                  err_msg = "[ERROR]    Error with conect ONVIFCamera..."
                  print err_msg
                  print "[INFO]     Check the correctness of the entered data in the setings.ini (ip,port,login, password or wsdl_path)"
                  send_msg(msg=err_msg)
                  sys.exit(0)


                media = mycam.create_media_service()
                profile = media.GetProfiles()[0]
                ptz = mycam.create_ptz_service()
                request = ptz.create_type('GetConfigurationOptions')
                request.ConfigurationToken = profile.PTZConfiguration._token
                ptz_configuration_options = ptz.GetConfigurationOptions(request)
                request = ptz.create_type('ContinuousMove')
                request.ProfileToken = profile._token
                ptz.ContinuousMove(request)

            else:
              request.Velocity.PanTilt._x = 0
              request.Velocity.PanTilt._y = 0
              try:
                ptz.ContinuousMove(request)
              except:
                sleep(1)
                try:
                  mycam = ONVIFCamera(mycam_ip, mycam_port, mycam_login, mycam_password, mycam_wsdl_path)
                  print "[INFO]     Successful conection ONVIFCamera"
                except:
                  err_msg = "[ERROR]    Error with conect ONVIFCamera..."
                  print err_msg
                  print "[INFO]     Check the correctness of the entered data in the setings.ini (ip,port,login, password or wsdl_path)"
                  send_msg(msg=err_msg)
                  sys.exit(0)


                media = mycam.create_media_service()
                profile = media.GetProfiles()[0]
                ptz = mycam.create_ptz_service()
                request = ptz.create_type('GetConfigurationOptions')
                request.ConfigurationToken = profile.PTZConfiguration._token
                ptz_configuration_options = ptz.GetConfigurationOptions(request)
                request = ptz.create_type('ContinuousMove')
                request.ProfileToken = profile._token
                ptz.ContinuousMove(request)

            

  
  main()

except:
  exc_type, exc_value, exc_traceback = sys.exc_info()
  err_msg = str(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
  send_msg(msg=err_msg)
  
  #main()

