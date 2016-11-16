"""Brains ...

like: NullBrain, KinesisBrain, TaxisBrain, LearningBrain, ...

"""

import numpy as np

from collections import OrderedDict

from smq.utils import get_items

class Brain(object):
    def __init__(self, conf):
        self.conf = conf
        self.dim_s_motor = self.conf["dim_s_motor"]


        # # FIXME: basically a copy of what's in robot
        # self.dim    = 0
        # self.dimnames = []
        # self.smdict = OrderedDict()
        
        # # more differentiated sm space description
        # for k in ["dim_s_proprio", "dim_s_extero", "dim_s_intero", "dim_s_reward", "dim_s_pred", "dim_s_motor"]:
        #     dim_ = len(conf[k])
        #     setattr(self, k, dim_)
        #     self.dim += dim_
        #     for dimname in conf[k]:
        #         self.dimnames.append(dimname)
        #     k_ = k.replace("dim_", "")
        #     self.smdict[k_] = np.zeros((dim_, 1))
        # self.smdict_concat = [None for i in range(self.dim)]
        
        # print "%s.__init__ full sm dim = %d, names = %s, %s" % (self.__class__.__name__, self.dim, self.dimnames, self.smdict)
        # self.sm = np.zeros((self.dim, 1)) # full sensorimotor vector, use dict?

        # copy sm structure from robot
        for attr in conf["smattrs"]:
            print attr, conf[attr]
            setattr(self, attr, conf[attr])
        for attr in conf["smdict"].keys():
            # print "dim_" + attr, conf["smdict"][attr].shape[0]
            setattr(self, "dim_" + attr, conf["smdict"][attr].shape[0])
        
        # tasks
        self.tasks = get_items(conf["tasks"])
        # assert one reward for each task?
        assert(len(self.tasks) == self.dim_s_reward)

    def step(self, x):
        # 1. get sensors
        if x is None: # catch initial state
            # self.x = np.random.uniform(-1.0, 1.0, (self.sdim, 1))
            self.smdict["s_proprio"] = np.random.uniform(-1.0, 1.0, (self.dim_s_proprio, 1))
            self.smdict["s_extero"]  = np.random.uniform(-1.0, 1.0, (self.dim_s_extero,  1))
        else:
            self.smdict["s_proprio"] = x["s_proprio"].copy() # HACK?
            self.smdict["s_extero"]  = x["s_extero"].copy() # HACK?

        for i,task in enumerate(self.tasks):
            # self.smdict["s_reward"][i,0] = task.eval(self.smdict)
            # HACK
            # self.smdict["s_intero"][2] = task.goal
            self.smdict = task.eval(self.smdict)
        return x
             
    def predict_proprio(self):
        """By definition proprio space is identical to motor space?"""
        # return self.x[:-self.dim_s_motor]
        print "self.smdict[\"s_pred\"]", self.smdict
        self.smdict["s_pred"] = np.zeros((1, self.dim_s_motor))
        return self.smdict["s_pred"]

class NullBrain(Brain):
    """Plain Brain already is NullBrain: always predicts zeros"""
    def __init__(self, conf):
        Brain.__init__(self, conf)

class KinesisBrain(Brain):
    """Realize simple non-plastic kinesis"""
    def __init__(self, conf):
        Brain.__init__(self, conf)

    def predict_proprio(self):
        """By definition proprio space is identical to motor space?"""
        # checking for the value of a reward is this brain's way of responding to the environment
        if self.smdict["s_reward"][0] > 0.02:
             self.smdict["s_pred"] = np.random.uniform(-1.5, 1.5, (1, self.dim_s_motor))
        else:
             self.smdict["s_pred"] = np.random.uniform(-0.01, 0.01, (1, self.dim_s_motor))
        err = self.smdict["s_reward"][0]
        # self.smdict["s_pred"] = np.random.uniform(-(np.sqrt(err)*2), np.sqrt(err)*2, (1, self.dim_s_motor))
        return self.smdict["s_pred"].T
        
        
# Identity, Random, MotorBabbling, ...
