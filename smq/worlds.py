"""Worlds for use in smq experiments

A world contains robots and an additional set of forces, objects, processes, agents, and so on.

"""
import time
import numpy as np

import smq.logging as log

from robots import Robot2
from brains import Brain2

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

    def update_robot_f(self, robot, prediction):
        """update function for a given robot, arg x is a robot instance"""
        return robot.y + np.random.normal(0, self.noise, robot.y.shape)

    def update_robot(self, robot, prediction):
        """update function for a given robot, arg x is a robot instance"""
        # return robot.y + np.random.normal(0, self.noise, robot.y.shape)
        return robot.update(prediction)

    def update_robot_explauto(self, robot, prediction):
        """update/interaction function, if explauto context_environment strip context info"""
        x_full = robot.update(prediction)
        print "%s.update_robot_f_2 x_full.shape = %s" % (self.__class__.__name__, x_full.shape)
        
        # x_full has dim = 2 * sdim, context and current, explauto hack
        return x_full[(robot.dim_s_proprio + robot.dim_s_extero):]
        
    def step(self):
        """one time step world update"""
        # print "self.time", self.time
        # Y = []
        for i,robotdict in enumerate(self.robots):
            print "robotdict", robotdict
            # temporary helpers
            robot = robotdict["robot"] # get the smq.robots.Robot instance
            robin = robotdict["input"] # get the associated input item
            # debug
            # print "robin.shape", robin.shape, robin
            
            # update (step) robot, returns y (motor vector, or proprio description) which
            # is passed through the environment and only reinserted into the robot in the
            # update function
            # argument is the entire sensory input for the robot including proprio, extero, which is
            # a problem with the self-contained robot/environments of explauto
            y = robot.step(robin)
            # now action is out in the world
            
            # update robot's state by interaction with world
            robin = self.update_robot[i](robot, y) # FIXME
            # TODO: self.update_world(), maybe does something with the input
            # task: tasks and robots are synchronised arrays so we use common loop
            # evaluate task and use feedback as sensors for robot/brain
            
            # debug
            # print "%s.step robotdict[\"input\"].shape = %s, %s" % (self.__class__.__name__, robotdict["input"].shape, robotdict["input"])
            # print "robot.x.shape = %s, %s" % (robot.x.shape, robot.x)
            # print "robot.y.shape = %s, %s" % (robot.y.shape, robot.y)
            
            # log all robot module data for current timestep
            logdata = robot.get_logdata()
            # print "logdata.shape", logdata.shape

            # now = time.time()
            log.log(robot.conf["name"], logdata)
            # print "%s.step log2 took %f s" % (self.__class__.__name__, time.time() - now)

            # now = time.time()
            log.log3(robot.conf["name"], logdata)
            # print "%s.step log3 took %f s" % (self.__class__.__name__, time.time() - now)

            # update persistent storage
            robotdict["input"] = robin
            
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
                    print "%s.add'ing a robot %s" % (self.__class__.__name__, item)
                    # intialize robot's input vector, possible FIXME to specify fully general input description in robot config
                    self.robots.append({"robot": item, "input": np.zeros((item.dim_s_proprio + item.dim_s_extero, 1))})
                    if item.type == "explauto":
                        self.update_robot.append(self.update_robot_explauto)
                    else:
                        self.update_robot.append(self.update_robot)
                    log.init_log2_block(item.conf["name"], item.dim)
                    # columns = [getattr(item, a) for a in item.smstruct]
                    columns = [a for a in item.dimnames]
                    # print "%s.add: columns %s" % (self.__class__.__name__, columns)
                    log.init_log3_block(item.conf["name"], item.dim, tbl_columns = columns, numsteps = self.numsteps)
        else:
            print self.__class__.__name__, "add(): requires list"

################################################################################
#
class RobotWorld2(RobotWorld):
    def __init__(self, conf):
        RobotWorld.__init__(self, conf)
        self.brains = []

    def step(self):
        for i in range(len(self.brains)):
            brain = self.brains[i]
            robot = self.robots[i]
            # debug
            # print "%s.step self.brains[%d] = %s" % (self.__class__.__name__, i, brain)
            # print "%s.step self.robots[%d] = %s" % (self.__class__.__name__, i, robot)
            # robot = robotdict["robot"]   # get the smq.robots.Robot instance
            # robin = robotdict["sensors"] # get the associated sensors item
            y = brain["brain"].step(robot["sensors"])
            robot["sensors"] = robot["robot"].step(self, y) # self.update_robot[i](robot, y) # FIXME
            
            # log all brain and robot module data for current timestep
            for k,v in {"brain": brain, "robot": robot}.items():
                logdata = v[k].get_logdata()
                # print "logdata.shape", logdata.shape
                # now = time.time()
                log.log3(v[k].conf["name"], logdata)
                # print "%s.step log3 took %f s" % (self.__class__.__name__, time.time() - now)
            
        self.time += self.dt

    def add(self, items):
        if items.__class__ == list:
            # print "it's a list"
            for i, item in enumerate(items):
                # print "item #%d" % i
                if isinstance(item, Robot2):
                    print "%s.add'ing a robot %s" % (self.__class__.__name__, item)
                    # self.robots.append({"robot": item, "sensors": np.zeros((item.dim_s_proprio + item.dim_s_extero, 1))})
                    self.robots.append({"robot": item,
                                        "sensors": {"s_proprio": np.zeros((item.dim_s_proprio, 1)),
                                                    "s_extero" : np.zeros((item.dim_s_extero, 1))}})
                    columns = [a for a in item.dimnames]
                    log.init_log3_block(item.conf["name"], item.dim, tbl_columns = columns, numsteps = self.numsteps)
                elif isinstance(item, Brain2):
                    print "%s.add'ing a brain %s" % (self.__class__.__name__, item)
                    self.brains.append({"brain": item, "motors": np.zeros((item.dim_s_motor, 1))})
                    columns = [a for a in item.dimnames]
                    log.init_log3_block(item.conf["name"], item.dim, tbl_columns = columns, numsteps = self.numsteps)
        else:
            print self.__class__.__name__, "add(): requires list"

