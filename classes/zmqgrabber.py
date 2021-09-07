# Zeromq message grabber class

import zmq
from threading import Thread


class message_grabber(Thread):
    __translation = None
    __rotation = None
    __socket = None
    __message = None
    __isRunning = False

    def __init__(self, Uri):
        Thread.__init__(self)
        context = zmq.Context()
        self.__socket = context.socket(zmq.REP)
        self.__socket.bind(Uri)
        self.__isRunning = True

    def __del__(self):
        self.__socket.close()

    def run(self):
        while self.__isRunning:
            self.__message = self.__socket.recv().decode("utf-8")
            self.__socket.send(b"Ok")
            spl = self.__message.split("|")
            self.__rotation = list(map(float, spl[0].split(" ")))
            self.__translation = list(map(float, spl[1].split(" ")))

    def get_message(self):
        return self.__message

    def stop_thread(self):
        self.__socket.close()
        self.__isRunning = False

    def get_translation(self):
        return self.__translation

    def get_rotation(self):
        return self.__rotation
