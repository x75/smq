"""
smq/smq/experiment.py: library components for the experiment shell

(c) 2016 Oswald Berthold
"""

import argparse

# from robots import ...
# available robots: pointmass, simple arm, two-wheeled differential, ...

from smq.utils  import get_items
from smq.worlds import RobotWorld
import smq.logging as log

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

def make_expr_sig(args =  None):
    """create experiment signature string from args and timestamp"""
    import time
    # print ("make_expr_sig", args)
    # infile = args.infile.replace("/", "_").replace(".wav", "")
    # expr_sig = "MN%s_MS%d_IF%s_IS%d_NE%d_EL%d_TS%s" % (args.mode, args.modelsize, infile, args.samplelen, args.numepochs, args.embedding_length, time.strftime("%Y%m%d-%H%M%S"))
    expr_sig = time.strftime("%Y%m%d-%H%M%S")
    return expr_sig

class Experiment(object):
    def __init__(self, args):
        self.configfile = args.conf
        self.conf = get_config_raw(self.configfile)
        # precendence: conf, args overrides that
        self.numsteps = self.conf["numsteps"]

        if args.numsteps is not None:
            self.numsteps = args.numsteps
            
        # print "self.conf", self.conf
        self.brains = []
        self.loss = []
        self.task = []
        self.robots = []
        self.worlds = [] # index 0 convention, we will have _one_ world for a beginning
        self.analyses = []

        # initialize global logging
        log.init_log2(self.conf)
        
        # initialize parts from config
        self.prepare()

        # experiment signature
        # self.conf["signature"] = make_expr_sig(self.conf)
        
    def prepare(self):
        """prepare the experiment: construct everything we need from the config"""
        # get brain
        # self.brains = get_items(self.conf["brains"])
        # get task
        # self.tasks  = get_items(self.conf["tasks"])
        # print "self.tasks", self.tasks
        # get loss
        # append loss to task
        # get robot
        self.robots = get_items(self.conf["robots"])
        # append task to robot
        # get world
        print "self.conf[\"worlds\"][0]", self.conf["worlds"][0]
        self.worlds = get_items(self.conf["worlds"])
        self.worlds[0].add(self.robots)
        # append robot to world
        # append analyses
        self.analyses = get_items(self.conf["analyses"])
        # finito
                
    def run(self):
        # FIXME: how to define experiment structure in conf for different scenarios like:
        # single run single model single task
        # single run multiple models single task
        # optimization run single model single task
        # ...
        # IDEA: use a generic type "loop" which has a "step" method and a "stack" member
        #       stacks are ordered dicts/lists of "loops"
        #       examples: single episode learning, multi episode learning (value func prop),
        #                 multi episode optimization (hpo, cma, evo, ...)
        #                 infinite episode, ...
        for i in xrange(self.numsteps):
            print "#" * 80
            print "Experiment.run iter = %d" % i
            # 1. get sensors
            # 2. do brain
            # 3. do motors
            # 4. do world
            self.worlds[0].step()
            # 5. log
            # 6. repeat

        self.analyse()


    def analyse(self):
        # print "%s.analyse(): implement me" % (self.__class__.__name__)
        for a in self.analyses:
            a.run()
