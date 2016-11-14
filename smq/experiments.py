"""
smq/smq/experiment.py: library components for the experiment shell

(c) 2016 Oswald Berthold
"""

import argparse

# from robots import ...
# available robots: pointmass, simple arm, two-wheeled differential, ...

from smq.worlds import RobotWorld
from smq.logging import Logger

################################################################################
# from im/im_quadrotor_controller
def get_args():
    import argparse
    # define defaults
    default_conf     = "conf/default.py"
    default_numsteps = None # 10
    # create parser
    parser = argparse.ArgumentParser()
    # add required arguments
    parser.add_argument("-c", "--conf",     type=str, default=default_conf,     help="Configuration file [%s]" % default_conf)
    parser.add_argument("-n", "--numsteps", type=int, default=default_numsteps, help="Number of outer loop steps [%s]" % default_numsteps)
    # parse arguments
    args = parser.parse_args()
    # return arguments
    return args

################################################################################
# from im/im_experiment.py
def get_config_raw(conf):
    # open and read config file containing a dictionary spec
    s = open(conf, "r").read()

    # parse config into variable, easy
    # conf = eval(s)

    # proper version with more powerS!
    code = compile(s, "<string>", "exec")
    global_vars = {}
    local_vars  = {}
    exec(code, global_vars, local_vars)

    conf = local_vars["conf"]

    # print "conf", conf

    return conf

def get_robots(robot_confs):
    # print "robot_confs", robot_confs
    robots = []
    for i, robot_conf in enumerate(robot_confs):
        # print "i, robot_conf", i, robot_conf["class"]
        robots.append(robot_conf["class"](robot_conf))
    return robots
        
def get_worlds(world_conf):
    # print "world_conf", world_conf
    worlds = []
    for i in range(1):
        # print "i", type(i), i, world_conf
        worlds.append(world_conf[i]["class"](world_conf[i]))
    return worlds

class Experiment(object):
    def __init__(self, args):
        self.configfile = args.conf
        self.conf = get_config_raw(self.configfile)
        # precendence: conf, args overrides that
        self.numsteps = self.conf["numsteps"]

        if args.numsteps is not None:
            self.numsteps = args.numsteps
            
        # print "self.conf", self.conf
        self.loss = []
        self.task = []
        self.robots = []
        self.worlds = [] # index 0 convention, we will have _one_ world for a beginning
        self.analyses = []
        self.prepare()

    def prepare(self):
        """prepare the experiment: construct everything we need from the config"""
        # get task
        # get loss
        # append loss to task
        # get robot
        self.robots = get_robots(self.conf["robots"])
        # append task to robot
        # get world
        print "self.conf[\"worlds\"][0]", self.conf["worlds"][0]
        self.worlds = get_worlds(self.conf["worlds"])
        self.worlds[0].add(self.robots)
        # append robot to world
        # finito
                
    def run(self):
        # FIXME: how to define experiment structure in conf for different scenarios like:
        # single run single model single task
        # single run multiple models single task
        # optimization run single model single task
        # ...
        # IDEA: use a generic type "loop" which has a "step" method and a "stack" member
        #       stacks are ordered dicts/lists of "loops"
        for i in xrange(self.numsteps):
            print "#" * 80
            print "Experiment.run iter = %d" % i
            # 1. get sensors
            # 2. do brain
            # 3. do motors
            # 4. do world
            self.worlds[0].step()
            # 5. repeat

        self.analyse()


    def analyse(self):
        print "%s.analyse(): implement me" % (self.__class__.__name__)
        # for a in self.analyses:
        #     a.run()
            
