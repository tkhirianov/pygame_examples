#!/usr/bin python3
import os

class Debugger(object):
    def __init__(self, path):
        self.path = "%s/../%s" % (os.path.dirname(os.path.realpath(__file__)), path)
        f = open(self.path, "w")
        f.close()

    def write(self, msg):
        with open(self.path, "a") as f:
            f.write(msg)