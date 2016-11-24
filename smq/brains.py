"""smq Brains

like: NullBrain, KinesisBrain, TaxisBrain, LearningBrain, ...

"""

import numpy as np

from collections import OrderedDict

from smq.utils import get_items, set_attr_from_dict, ct_pol2car, ct_car2pol, set_attr_from_dict_ifs

from smq.motivation import default_conf_motivations

################################################################################
# Brain's are things that can be fed with numbers (data) and which respond with
# predictions about future values of sensorimotor space. Those predictions corresponding
# to motor lines will then be interpreted by the motor units as "commands"
# v2 style is a the current rewrite
class Brain2(object):
    """Brain2 basic Brain"""
    def __init__(self, conf, ifs_conf):
        self.conf = conf
        # self.dim_s_motor = self.conf["dim_s_motor"]

        # default conf to attr copy action
        set_attr_from_dict(self, self.conf)

        # configure structure of sensorimotor space
        set_attr_from_dict_ifs(self, ifs_conf)
                            
        # configure tasks
        self.tasks = get_items(conf["tasks"])
        for task in self.tasks:
            # task.brain = self
            task.prepare(self)

        # configure motivation
        if not conf.has_key("motivations"):
            conf["motivations"] = default_conf_motivations
        self.motivations = get_items(conf["motivations"])
        
        # assert one reward for each task?
        assert(len(self.tasks) == self.dim_s_reward)

    def get_sm_index(self, dimgroup, base):
        return [self.smdict_index[dimgroup]["%s%d" % (base, k)] for k in range(self.dim_s_motor)]
        
    def get_logdata(self):
        """collect all internal variables, stack them into one vector and
        return that"""
        logdata = np.atleast_2d(np.vstack([self.smdict[k] for k in self.smdict.keys()]))
        # print "%s.get_logdata, logdata.shape = %s, self.dim = %d" % (self.__class__.__name__, logdata.shape, self.dim)
        # logdata = np.atleast_2d(np.hstack((self.x, self.y))).T
        return logdata
    
    def step(self, x):
        """ingest new sensory measurements into state"""
        # # old numpy array style
        # assert(type(x) == np.ndarray)
        # assert(x.shape == (self.dim_s_proprio + self.dim_s_extero, 1))

        # new smdict style
        assert(type(x) == dict)
        assert(x["s_proprio"].shape == (self.dim_s_proprio, 1))
        assert(x["s_extero"].shape  == (self.dim_s_extero, 1))

        # copy raw numpy array into smdict
        
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
            self.smdict = task.eval(self.smdict, i)
        
        prediction = self.predict_proprio()
        print "prediction", prediction.shape
        assert(prediction.shape == (self.dim_s_motor, 1))
        self.smdict["s_motor"] = prediction
        return prediction
             
    def predict_proprio(self):
        """produce new predictions based on state, by definition proprio space is identical to motor space?"""
        # return self.x[:-self.dim_s_motor]
        # print "self.smdict[\"s_pred\"]", self.smdict
        # self.smdict["s_pred"] = np.zeros((1, self.dim_s_motor))
        return np.zeros((self.dim_s_motor, 1))

class NullBrain2(Brain2):
    """Plain Brain already is NullBrain: always predicts zeros"""
    def __init__(self, conf, ifs_conf):
        Brain2.__init__(self, conf, ifs_conf)

class KinesisBrain2(Brain2):
    """Realize simple non-plastic kinesis"""
    def __init__(self, conf, ifs_conf):
        Brain2.__init__(self, conf, ifs_conf)

    def predict_proprio(self):
        """By definition proprio space is identical to motor space?"""
        # checking for the value of a reward is this brain's way of responding to the environment
        gain = self.continuous_gain
        
        for i, task in enumerate(self.tasks):
            err = self.smdict["s_reward"][i]
        
            if self.variant == "binary_threshold":
                if err > self.binary_threshold: # FIXME: hardcoded index
                    # self.smdict["s_intero"][self.smdict_index["s_intero"]["thresh0"]] = 1
                    self.smdict["s_pred"] = np.random.uniform(-self.binary_high_range, self.binary_high_range, (self.dim_s_motor, 1))
                else:
                    # self.smdict["s_intero"][self.smdict_index["s_intero"]["thresh0"]] = 0
                    self.smdict["s_pred"] = np.random.uniform(-self.binary_low_range,  self.binary_low_range,  (self.dim_s_motor, 1))
            else: # default case
                self.smdict["s_pred"] = np.random.uniform(-(np.sqrt(err)*gain), np.sqrt(err)*gain, (self.dim_s_motor, 1))
                # self.smdict["s_pred"] = np.random.uniform(-(np.power(err, 1/2.0)*gain), np.power(err, 1/2.0)*gain, (1, self.dim_s_motor))

        # FIXME: currently last task wins. reset s_pred to zero, accumulate
        # predictions respecting previously computed values
        return self.smdict["s_pred"]

class TaxisBrain2(Brain2):
    def __init__(self, conf, ifs_conf):
        Brain2.__init__(self, conf, ifs_conf)

    def predict_proprio(self):
        error_cart_level = 0.1
        gain = self.gain

        for i, task in enumerate(self.tasks):        
            # cartesian error
            # error_cart = self.smdict["s_intero"][self.get_sm_index("s_intero", "vel_error")]
            error_cart = self.smdict["s_intero"][task.intero_error_idx_num]

            # add noise to error
            error_cart += np.random.normal(0, error_cart_level, error_cart.shape)

            # prediction based on cartesian error, accounting for both angular
            # and absolute value error components
            # pred = error_cart * -gain + np.random.normal(0.01, 0.01, error_cart.shape)

            # debug
            # print "%s.predict_proprio: error_cart = %s, pred = %s" % (self.__class__.__name__, error_cart, pred)
        
            # prediction based on directional error only, with a fixed absolute
            # value component

            if self.dim_s_motor > 1:
                # transform cartesian to polar
                error_pol = ct_car2pol(error_cart)
        
                print "error_cart", error_cart, "error_pol", error_pol
            
                # prepare argument
                arrarg  = error_pol[1:].reshape(error_cart.shape[0]-1, )
                # arrarg += np.random.normal(0.0, 0.1, arrarg.shape)
    
                # print "error_arg", arrarg
            
                # transform back to cartesian
                pred = -ct_pol2car(gain, arrarg).reshape(error_cart.shape)
            else:
                pred = -np.sign(error_cart) * gain

            # print "%s.predict_proprio: error_pol = %s, pred = %s" % (self.__class__.__name__, error_pol, pred)
        
            # # FIXME: control indexing shape
            # pred_idx = self.robot.get_sm_index("s_pred", "acc_pred")
            # # pred_idx = map(list, zip(*pred_idx))        
            # print "%s.predict_proprio: pred_idx = %s" % (self.__class__.__name__, pred_idx)
            # self.smdict["s_pred"][pred_idx] = pred
            # return self.smdict["s_pred"].T
        
        self.smdict["s_pred"] = pred
        # make sure shape is (1, dim)
        return self.smdict["s_pred"]
