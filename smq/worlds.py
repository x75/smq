"""Worlds for use in smq experiments

A world contains robots and an additional set of forces, objects, processes, agents, and so on.

"""

import numpy as np

import smq.logging as log

from robots import Robot

class World(object):
    def __init__(self, conf):
        self.conf     = conf
        self.time     = 0
        self.dt       = self.conf["dt"]
        self.dim      = self.conf["dim"]
        self.numsteps = self.conf["numsteps"]
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

    def update_robot_f(self, robot):
        """update function for a given robot, arg x is a robot instance"""
        return robot.y + np.random.normal(0, self.noise, robot.y.shape)

    def update_robot_f_2(self, robot, prediction):
        """update/interaction function"""
        x_full = robot.update(prediction)
        # x_full has dim = 2 * sdim, context and current, explauto hack
        return x_full[(robot.dim_s_proprio + robot.dim_s_extero):]
        
    def step(self):
        """one time step world update"""
        # print "self.time", self.time
        # Y = []
        for i,robotdict in enumerate(self.robots):
            # temporary helpers
            robot = robotdict["robot"]
            robin = robotdict["input"]
            # debug
            # print "robin.shape", robin.shape, robin
            
            # update (step) robot, returns y (motor vector, or proprio description)
            # FIXME: this is awkward, rather get/set x directly from outside
            y = robot.step(robin)
            # now action is out in the world
            
            # update robot's state by interaction with world
            robotdict["input"] = self.update_robot[i](robot, y) # FIXME
            # TODO: self.update_world(), maybe does something with the input
            # task: tasks and robots are synchronised arrays so we use common loop
            # evaluate task and use feedback as sensors for robot/brain
            # debug
            # print "robotdict[\"input\"].shape", robotdict["input"].shape, robotdict["input"]
            # print "robot.x.shape = %s, %s" % (robot.x.shape, robot.x)
            # print "robot.y.shape = %s, %s" % (robot.y.shape, robot.y)
            # log all robot module data for current timestep
            # logdata = np.atleast_2d(np.hstack((robot.x, robot.y))).T
            logdata = robot.get_logdata()
            # print "logdata.shape", logdata.shape
            log.log(robot.conf["name"], logdata)
            log.log3(robot.conf["name"], logdata)
            
        # update time
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
                    self.robots.append({"robot": item, "input": np.zeros((item.dim_s_proprio + item.dim_s_extero, 1))})
                    self.update_robot.append(self.update_robot_f_2)
                    log.init_log2_block(item.conf["name"], item.dim)
                    # columns = [getattr(item, a) for a in item.smstruct]
                    columns = [a for a in item.dimnames]
                    print "columns", columns
                    log.init_log3_block(item.conf["name"], item.dim, tbl_columns = columns, numsteps = self.numsteps)
        else:
            print self.__class__.__name__, "add(): requires list"
