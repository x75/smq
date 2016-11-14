"""Robots for use in smq experiments

A robot contains a body, defined set of internal states, given brain, ...

"""

class Robot(object):
    def __init__(self, conf):
        self.conf = conf

    def step(self):
        pass


class Pointmass(Robot):
    def __init__(self, conf):
        print "conf", conf
        Robot.__init__(self, conf)

    def step(self):
        print "self.state", self.conf
        
