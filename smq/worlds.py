"""Worlds for use in smq experiments

A world contains robots and an additional set of forces, objects, processes, agents, and so on.

"""

from robots import Robot

class World(object):
    def __init__(self, conf):
        self.conf = conf
        self.time = 0
        self.dt   = self.conf["dt"]

    def step(self):
        self.time += self.dt


class RobotWorld(World):
    def __init__(self, conf):
        World.__init__(self, conf)
        self.robots = []

    def add_robots(self, robots):
        for robot in robots:
            self.robots.append(robot)

    def step(self):
        # print "self.time", self.time
        for robot in self.robots:
            # print "robot", robot
            robot.step()
        self.time += self.dt

    def add(self, items):
        """add an item to the world"""
        # print item.__class__
        # print item[0].__class__
        if items.__class__ == list:
            # print "it's a list"
            for i, item in enumerate(items):
                # print "item #%d" % i
                if isinstance(item, Robot):
                    print "it's a robot"
                    self.robots.append(item)
