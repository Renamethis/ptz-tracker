# Class for receiving a rtsp stream

import cv2
from threading import Thread
import logging


class VideoStream:
    # Initialization
    def __init__(self, GStreamer=True, device="CPU", name="VideoStream"):
        self.name = name
        self.__logger = logging.getLogger("Main.%s" % (self.name))
        self.frame = None
        self.running = False
        if(GStreamer):
            if(device == "Jetson"):
                self.rtsp_url = 'rtspsrc location="{rtsp_url}" ! queue' + \
                    '! rtph264depay ! queue ! h264parse ! omxh264dec !' + \
                    ' nvvidconv ! video/x-raw,format=BGRx !' + \
                    ' videoconvert! video/x-raw,format=BGR ! appsink'
            else:
                self.rtsp_url = 'rtspsrc location="{rtsp_url}" latency=0 !' + \
                 'rtph264depay ! queue ! decodebin ! queue !' + \
                 ' videoconvert ! appsink'
            self.cap_flag = cv2.CAP_GSTREAMER
        else:
            self.cap_flag = cv2.CAP_FFMPEG
            self.rtsp_url = "{rtsp_url}"

    # Start thread
    def start(self, rtsp_url):
        self.__logger.info("Process starting")
        self.running = True
        self.rtsp_url = self.rtsp_url.format(rtsp_url=rtsp_url)
        self.__stream = cv2.VideoCapture(self.rtsp_url, self.cap_flag)
        self.__thread = Thread(target=self.__update, name=self.name, args=())
        self.__thread.daemon = True
        self.__thread.start()
        return self

    # Main loop of receiving frames from rtsp-stream
    def __update(self):
        self.__logger.info("Process started")
        while self.running and self.__stream.isOpened():
            (self.grabbed, self.frame) = self.__stream.read()
        self.running = False
        self.__logger.info("Process stopped")

    # Get frame
    def read(self):
        return self.frame

    # Stop thread
    def stop(self):
        self.running = False
        self.__stream.release()
