"""
smq/smq/experiment.py: library components for the experiment shell

(c) 2016 Oswald Berthold
"""

import argparse

# from robots import ...
# available robots: pointmass, simple arm, two-wheeled differential, ...

try:
    import rospy
except Exception, e:
    print "import rospy failed", e


from smq.utils  import get_items, get_items2
from smq.worlds import RobotWorld2
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

def set_config_defaults(conf):
    """Try and set some reasonable defaults in case of inconsistent configurations"""
    # robots
    for robot in conf["robots"]:
        # brains
        for brain in robot["brains"]:
            # brain items
            print brain["class"]
            # kinesis brain
            if brain["class"].__name__ == "KinesisBrain": # FIXME
                brain_items = {
                    "variant": "default",
                    "continuous_gain": 1.5,
                    "binary_threshold": 0.005,
                    "binary_high_range": 1.5,
                    "binary_low_range": 0.01
                    }
            # taxis brain
            elif brain["class"].__name__.startswith("TaxisBrain"): # FIXME
                brain_items = {
                    "gain": 1.0
                    }
            else:
                brain_items = {}

            # copy from default dict to real dict
            for k,v in brain_items.items():
                if not brain.has_key(k):
                    brain[k] = v
            
            # tasks
            for task in brain["tasks"]:
                if not task.has_key("goaldim"):
                    task["goaldim"] = 1
                if not task.has_key("intero_index"):
                    task["intero_index"] = 1
    
    for analysis in conf["analyses"]:
        # print analysis
        if not analysis.has_key("type"):
            analysis["type"] = "seaborn"
    return conf

def set_config_defaults2(conf):
    """Try and set some reasonable defaults in case of inconsistent configurations"""
    # brains
    for brain in conf["brains"]:
        # kinesis brain
        if brain["class"].__name__ == "KinesisBrain": # FIXME
            brain_items = {
                "variant": "default",
                "continuous_gain": 1.5,
                "binary_threshold": 0.005,
                "binary_high_range": 1.5,
                "binary_low_range": 0.01
                }
        # taxis brain
        elif brain["class"].__name__.startswith("TaxisBrain"): # FIXME
            brain_items = {
                "gain": 1.0
            }
        else:
            brain_items = {}

        # copy from default dict to real dict
        for k,v in brain_items.items():
            if not brain.has_key(k):
                brain[k] = v
        
        # tasks
        for task in brain["tasks"]:
            if not task.has_key("goaldim"):
                task["goaldim"] = 1
            if not task.has_key("intero_index"):
                task["intero_index"] = 1
    # robots
    for robot in conf["robots"]:
        pass
            
    for analysis in conf["analyses"]:
        # print analysis
        if not analysis.has_key("type"):
            analysis["type"] = "seaborn"
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
        self.conf = set_config_defaults(self.conf)
        
        # precendence: conf, args overrides that
        self.numsteps = self.conf["numsteps"]

        if args.numsteps is not None:
            self.numsteps = args.numsteps
            
        # print "self.conf", self.conf
        self.brains = []
        # self.loss = []
        # self.task = []
        self.robots = []
        self.worlds = [] # index 0 convention, we will have _one_ world for a beginning
        self.analyses = []

        # initialize global logging
        log.init_log2(self.conf)
        log.init_log3(self.conf)
        
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
        self.conf["worlds"][0]["numsteps"] = self.numsteps
        self.worlds = get_items(self.conf["worlds"])
        self.worlds[0].add(self.robots)
        # append robot to world
        # append analyses
        self.analyses = get_items(self.conf["analyses"])
        # finito
                
    def run(self):
        """experiment run method: a set of nested loops capturing optimization over different
        time scales, agents, parameters, ..."""
        
        for i in xrange(self.numsteps):
            print "# % 10d " % (i) + "#" * 80
            # 1. get sensors
            # 2. do brain
            # 3. do motors
            # 4. do world
            self.worlds[0].step()
            # 5. log
            # 6. repeat

            # TODO: realtime mode: delay next iteration for realtime plotting and visualization
        # store logs, FIXME incrementally
        for k,v in log.log_lognodes.items():
            print "k", k, "v", type(v)
            log.log_store[k] = v

        # run analyses
        self.analyse()


    def analyse(self):
        # print "%s.analyse(): implement me" % (self.__class__.__name__)
        if len(self.robots) < 1:
            return
        
        for a in self.analyses:
            a.run(self.robots)


################################################################################
#
class Experiment2(object):
    def __init__(self, args):
        self.configfile = args.conf
        self.conf = get_config_raw(self.configfile)
        self.conf = set_config_defaults2(self.conf)
        
        # precendence: conf, args overrides that
        self.numsteps = self.conf["numsteps"]

        if args.numsteps is not None:
            self.numsteps = args.numsteps
            
        self.brains = []
        self.robots = []
        self.worlds = [] # index 0 convention, we will have _one_ world for a beginning
        self.analyses = []

        # initialize global logging
        log.init_log3(self.conf)

        # ROS
        if not self.conf.has_key("ros"): self.conf["ros"] = False
        if self.conf["ros"]:
            rospy.init_node(self.conf["id"])
                
        # initialize parts from config
        self.prepare()

        # experiment signature
        # self.conf["signature"] = make_expr_sig(self.conf)
        
    def prepare(self):
        """prepare the experiment: construct everything we need from the config"""
        
        # get brains
        self.brains = get_items2(self.conf, "brains")

        # get robot bodies
        self.robots = get_items2(self.conf, "robots")

        # check for zombies
        assert(len(self.brains) == len(self.robots))

        # # add interfaces
        # for i in range(len(self.brains)):
        #     self.brains
        
        # get world
        self.conf["worlds"][0]["numsteps"] = self.numsteps
        self.worlds = get_items(self.conf["worlds"])
        self.worlds[0].add(self.brains)
        self.worlds[0].add(self.robots)

        # print self.worlds[0]
        
        # get analyses
        self.analyses = get_items(self.conf["analyses"])
        
        # finito
                
    def run(self):
        """experiment run method: a set of nested loops capturing optimization over different
        time scales, agents, parameters, ..."""
        
        for i in xrange(self.numsteps):
            # mark
            print "# % 10d " % (i) + "#" * 80
            # handle ROS
            if self.conf["ros"]:
                if rospy.is_shutdown():
                    break
                
            # do world
            self.worlds[0].step()

            # TODO: realtime mode: delay next iteration for realtime plotting and visualization
            
        # store logs, FIXME incrementally
        for k,v in log.log_lognodes.items():
            print "k", k, "v", type(v)
            log.log_store[k] = v

        # run analyses
        self.analyse()

    def analyse(self):
        # print "%s.analyse(): implement me" % (self.__class__.__name__)
        if len(self.robots) < 1:
            return
        
        for a in self.analyses:
            if hasattr(a, "plotitems"):
                for plotitem in getattr(a, "plotitems"):
                    print "plotitem", plotitem
                    a.run(getattr(self, plotitem))
            else:
                a.run(self.robots)
