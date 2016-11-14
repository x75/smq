"""Worlds for use in smq experiments

A world contains robots and an additional set of forces, objects, processes, agents, and so on.

"""

import numpy as np

import smq.logging as log

from robots import Robot

class World(object):
    def __init__(self, conf):
        self.conf  = conf
        self.time  = 0
        self.dt    = self.conf["dt"]
        self.dim   = self.conf["dim"]
        # world state: state of world minus robots themselves
        self.state = np.zeros((1, self.dim)).T
        self.x = {
            "world": self.state,
            }

    def step(self):
        self.time += self.dt

class RobotWorld(World):
    def __init__(self, conf):
        World.__init__(self, conf)
        self.robots = []
        self.update = lambda x: x # identity
        self.update_robot = []
        # self.X = np.zeros((1, self.dim )).T
        self.X    = None # full state information
        self.Xidx = None #
        # self.update_robot_f = lambda x: x.x
        # noisyness?
        self.noise = 1e-3

    def update_robot_f(self, x):
        """update function for a given robot, arg x is a robot instance"""
        return x.y + np.random.normal(0, self.noise, x.y.shape)
        
    # def add_robots(self, robots):
    #     for i, robot in enumerate(robots):
    #         self.robots.append({"robot": robot})
    #         self.update_robot.append(lambda x: x.x)

    def step(self):
        # print "self.time", self.time
        # Y = []
        for i,robot in enumerate(self.robots):
            # update (step) robot, returns y (motor vector, or proprio description)
            # FIXME: this is awkward, rather get/set x directly from outside
            y = robot.step(robot.x)
            # update robot's state by interaction with world
            robot.x = self.update_robot[i](robot)
            # 
            log.log(robot.conf["name"], np.vstack((robot.x, robot.y)))
            
        # Y = np.array(Y)
        # self.X = self.update(Y)
        # print "RobotWorld.step X", self.X
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
                    self.update_robot.append(self.update_robot_f)
                    log.init_log2_block(item.conf["name"], item.sdim + item.mdim)
        else:
            print self.__class__.__name__, "add(): requires list"
