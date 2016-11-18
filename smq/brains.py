"""Brains ...

like: NullBrain, KinesisBrain, TaxisBrain, LearningBrain, ...

"""

import numpy as np

from collections import OrderedDict

from smq.utils import get_items, set_attr_from_dict, ct_pol2car, ct_car2pol


class Brain(object):
    def __init__(self, conf):
        self.conf = conf
        self.dim_s_motor = self.conf["dim_s_motor"]

        # default conf to attr copy action
        set_attr_from_dict(self, self.conf)
        
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
        for attr in self.conf["smattrs"]:
            # print attr, self.conf[attr]
            setattr(self, attr, self.conf[attr])
        for attr in self.conf["smdict"].keys():
            # print "dim_" + attr, conf["smdict"][attr].shape[0]
            setattr(self, "dim_" + attr, conf["smdict"][attr].shape[0])
        
        # tasks
        self.tasks = get_items(conf["tasks"])
        for task in self.tasks:
            task.brain = self
        
        # assert one reward for each task?
        assert(len(self.tasks) == self.dim_s_reward)

    def step(self, x):
        # 1. get sensors
        if x is None: # catch initial state
            # self.x = np.random.uniform(-1.0, 1.0, (self.sdim, 1))
            self.smdict["s_proprio"] = np.random.uniform(-1.0, 1.0, (self.dim_s_proprio, 1))
            self.smdict["s_extero"]  = np.random.uniform(-1.0, 1.0, (self.dim_s_extero,  1))
            self.smdict["s_intero"]  = np.random.uniform(-1.0, 1.0, (self.dim_s_intero,  1))
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
        err = self.smdict["s_reward"][0]
        gain = self.continuous_gain
        
        if self.variant == "binary_threshold":
            if err > self.binary_threshold: # FIXME: hardcoded index
                self.smdict["s_pred"] = np.random.uniform(-self.binary_high_range, self.binary_high_range, (1, self.dim_s_motor))
            else:
                self.smdict["s_pred"] = np.random.uniform(-self.binary_low_range,  self.binary_low_range,  (1, self.dim_s_motor))
        else: # default case
            self.smdict["s_pred"] = np.random.uniform(-(np.sqrt(err)*gain), np.sqrt(err)*gain, (1, self.dim_s_motor))
            # self.smdict["s_pred"] = np.random.uniform(-(np.power(err, 1/2.0)*gain), np.power(err, 1/2.0)*gain, (1, self.dim_s_motor))
            
        return self.smdict["s_pred"]
        
class TaxisBrain(Brain):
    def __init__(self, conf):
        Brain.__init__(self, conf)

    def predict_proprio(self):
        error_cart_level = 0.1
        gain = 0.5
        # cartesian error, FIXME: more general with respect to the variable keys
        error_cart = self.smdict["s_intero"][self.robot.get_sm_index("s_intero", "vel_error")]

        # add noise to error
        # error_cart += np.random.normal(0, error_cart_level, error_cart.shape)

        # prediction based on cartesian error, accounting for both angular
        # and absolute value error components
        # pred = error_cart * -gain + np.random.normal(0.01, 0.01, error_cart.shape)

        # debug
        # print "%s.predict_proprio: error_cart = %s, pred = %s" % (self.__class__.__name__, error_cart, pred)
        

        # prediction based on directional error only, with a fixed absolute
        # value component
        # 
        # transform cartesian to polar
        error_pol = ct_car2pol(error_cart)
        # prepare argument
        arrarg  = error_pol[1:].reshape(error_cart.shape[0]-1, )
        arrarg += np.random.normal(0.0, 0.1, arrarg.shape)
        # transform back to cartesian
        pred = -ct_pol2car(0.05, arrarg).reshape(error_cart.shape)

        # print "%s.predict_proprio: error_pol = %s, pred = %s" % (self.__class__.__name__, error_pol, pred)
        
        # # FIXME: control indexing shape
        # pred_idx = self.robot.get_sm_index("s_pred", "acc_pred")
        # # pred_idx = map(list, zip(*pred_idx))        
        # print "%s.predict_proprio: pred_idx = %s" % (self.__class__.__name__, pred_idx)
        # self.smdict["s_pred"][pred_idx] = pred
        # return self.smdict["s_pred"].T
        
        self.smdict["s_pred"] = pred.T
        # make sure shape is (1, dim)
        return self.smdict["s_pred"]
                    
# Identity, Random, MotorBabbling, ...
