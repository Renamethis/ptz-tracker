# Class for receiving a rtsp stream

import sys
import cv2
from threading import Thread
import traceback
import time
import Utility_Functions as UF
import logging


class WebcamVideoStream:
    # Initialization
    def __init__(self, rtsp, name="WebcamVideoStream", GStreamer=True, Jetson=False):
        try:
            self.running = True
            self.name = name
            # Determining the path to the configuration file
            # add_try (count >= 3)

            self.mycam_rtsp = rtsp
            print(rtsp)
            init_logger = logging.getLogger("Main.%s.init" % (self.name))

            # Read configuration file (rtsp)
            # modify (receiving rtsp from camera)

            try:
                if(GStreamer):
                        if(Jetson):
                            self.mycam_rtsp = 'rtspsrc location="' + self.mycam_rtsp + '" ! queue ! rtph264depay ! queue ! h264parse ! omxh264dec ! nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! video/x-raw,format=BGR ! appsink'
                        else:
                            self.mycam_rtsp = 'rtspsrc location="' + self.mycam_rtsp + '" latency=0 ! rtph264depay ! queue ! decodebin ! queue ! videoconvert ! appsink'
                        self.stream = cv2.VideoCapture(self.mycam_rtsp, cv2.CAP_GSTREAMER)
                else:
                    self.stream = cv2.VideoCapture(self.mycam_rtsp, cv2.CAP_FFMPEG)
            except:
                init_logger.critical("Error with cv2.VideoCapture")
                init_logger.exception("Error!")
                exc_type, exc_value, exc_traceback = sys.exc_info()
                err_msg = str(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
                self.running = False

            if self.stream.isOpened() is False:

                err_msg = "Stream is close"
                init_logger.critical(err_msg)
                init_logger.info("Check rtsp in settings file")
                #UF.send_msg(msg=err_msg)
                self.running = False
            else:
                init_logger.info("Process get rtsp stream.")

            # 3.1.4. Read frame
            (self.grabbed, self.frame) = self.stream.read()
            self.stopped = False
        except:
            init_logger.critical("Error in %s.__init__" % (self.name))
            init_logger.exception("Error!")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err_msg = str(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
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

    # Infinite loop of receiving frames from a stream
    def update(self):
        try:
            update_logger = logging.getLogger("Main.%s.update" % (self.name))
            stream = self.stream
            update_logger.info("Process started")
            while True:
                if self.stopped:
                    update_logger.info("%s stopped" % self.name)
                    return
                (self.grabbed, self.frame) = stream.read()

        except:
            update_logger.critical("Error in process")
            update_logger.exception("Error!")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err_msg = str(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
            print(err_msg)
            self.running = False

    def check_connect(self):
        try:
            check_stream = cv2.VideoCapture(self.mycam_rtsp)
        except:
            return False
        if check_stream.isOpened() is False:
            check_stream.release()
            return False
        else:
            check_stream.release()
            return True

    def status(self):
        return self.t.isAlive()

    # Get frame
    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
