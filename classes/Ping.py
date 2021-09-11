# Class for checking the connection to the camera
import os
import logging
from time import sleep
from threading import Thread

class Ping:
    def __init__(self, mycam_ip, name="Ping"):
        self.name = name
        self.mycam_ip = mycam_ip
        self.stopped = False
        self.r = os.system("timeout 0.4 ping -c 1    " + self.mycam_ip + " > /dev/null 2>&1")

    def start(self):
        start_logger = logging.getLogger("Main.Ping.start")
        start_logger.info("Process starting")
        t = Thread(target=self.update, name=self.name, args=())
        t.daemon = True
        t.start()
        return self

    # Loop of receiving frames from a stream
    def update(self):
        update_logger = logging.getLogger("Main.Ping.start")
        update_logger.info("Process started")
        while not self.stopped:
            if self.stopped:
                return
            self.r = os.system("timeout 0.4 ping -c 1    " + self.mycam_ip + " > /dev/null 2>&1")
            sleep(5)

    # Get frame
    def read(self):
        return self.r

    # Stop frame
    def stop(self):
        self.stopped = True
