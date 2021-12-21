# Class for checking the connection to the camera
import os
import logging
from time import sleep
from threading import Thread


class Ping:
    def __init__(self, ip, name="Ping"):
        self.name = name
        self.mycam_ip = ip
        self.__logger = logging.getLogger("Main.%s" % (self.name))
        self.__rec = None

    # Start thread of checking camera connection
    def start(self):
        self.__logger.info("Process starting")
        self.running = True
        t = Thread(target=self.__update, name=self.name, args=())
        t.daemon = True
        t.start()
        return self

    # Loop of receiving frames from a stream
    def __update(self):
        self.__logger.info("Process started")
        while self.running:
            self.__rec = os.system("timeout 5 ping -c 1    "
                                   + self.mycam_ip + " > /dev/null 2>&1")
            sleep(1)
        self.__logger.info("Process stopped")

    # Return connection check var
    def read(self):
        return self.__rec

    # Stop thread
    def stop(self):
        self.running = False
