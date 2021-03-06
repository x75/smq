"""smq Brains

like: NullBrain, KinesisBrain, TaxisBrain, LearningBrain, ...

"""

import numpy as np

from collections import OrderedDict

from smq.utils import get_items, get_items2, get_items_with_ref, ct_pol2car, ct_car2pol

from smq.core import IFSMQModule
from smq.motivations import default_conf_motivations

from actinf_models import ActInfGMM, ActInfHebbianSOM

################################################################################
# Brain's are things that can be fed with numbers (data) and which respond with
# predictions about future values of sensorimotor space. Those predictions corresponding
# to motor lines will then be interpreted by the motor units as "commands"
# v2 style is a the current rewrite
class Brain2(IFSMQModule):
    """Brain2 basic Brain"""
    def __init__(self, conf, ifs_conf):
        IFSMQModule.__init__(self, conf, ifs_conf)
                            
        # configure tasks
        self.tasks = get_items_with_ref(conf["tasks"], self)
        print "%s.__init__: self.tasks = %s"  % (self.__class__.__name__, self.tasks)
        # for task in self.tasks:
        #     # task.brain = self
        #     task.prepare(self)

        # # configure motivation
        # if not conf.has_key("motivations"):
        #     conf["motivations"] = default_conf_motivations
        #     # conf["task"] = self.tasks[
        # # copy interfaces config
        # conf["ifs"] = [ifs_conf]
        # self.motivations = get_items_with_ref(conf["tasks"], self)
        # print "self.motivations", self.motivations
        
        # assert one reward for each task?
        assert(len(self.tasks) == self.dim_s_reward)

    def get_sm_index(self, dimgroup, base, indexdim = None):
        if indexdim is None:
            indexdim = self.dim_s_motor
        return [self.smdict_index[dimgroup]["%s%d" % (base, k)] for k in range(indexdim)]
        
    def get_sm_index_single(self, dimgroup, name):
        return [self.smdict_index[dimgroup]["%s" % (name)]]
    
    def get_logdata(self):
        """collect all internal variables, stack them into one vector and
        return that"""
        logdata = np.atleast_2d(np.vstack([self.smdict[k] for k in self.smdict.keys()]))
        # print "%s.get_logdata, logdata.shape = %s, self.dim = %d" % (self.__class__.__name__, logdata.shape, self.dim)
        # logdata = np.atleast_2d(np.hstack((self.x, self.y))).T
        return logdata

    def step_check_input(self, x):
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

    # FIXME: use decorators for this checking stuff
    def step(self, x):
        """ingest new sensory measurements into state"""
        # # old numpy array style
        # assert(type(x) == np.ndarray)
        # assert(x.shape == (self.dim_s_proprio + self.dim_s_extero, 1))

        self.step_check_input(x)

        for i,task in enumerate(self.tasks):
            # self.smdict["s_reward"][i,0] = task.eval(self.smdict)
            # HACK
            # self.smdict["s_intero"][2] = task.goal
            self.smdict = task.eval(self.smdict, i)
        
        prediction = self.predict_proprio()
        # print "prediction", prediction.shape
        assert(prediction.shape == (self.dim_s_motor, 1))
        # self.smdict["s_motor"] = prediction
        return prediction

    # predict proprioceptive state             
    def predict_proprio(self):
        """produce new predictions based on state
        
        by definition proprio space is identical to motor space

        task should already provide a prediction for itself,
        brain combines potentially multiple predictions"""
        
        for i, task in enumerate(self.tasks):
            self.smdict = task.motivation.step(self.smdict, i)
        return self.smdict["s_pred"]

class NullBrain2(Brain2):
    """Plain Brain already is NullBrain: always predicts zeros"""
    def __init__(self, conf, ifs_conf):
        Brain2.__init__(self, conf, ifs_conf)

# FIXME these also have collapsed into one Brain, remove
class KinesisBrain2(Brain2):
    """Realize simple non-plastic kinesis"""
    def __init__(self, conf, ifs_conf):
        Brain2.__init__(self, conf, ifs_conf)

    # def predict_proprio(self):
    #     """By definition proprio space is identical to motor space?"""
    #     # checking for the value of a reward is this brain's way of responding to the environment
              
    #     for i, task in enumerate(self.tasks):
    #         self.smdict = task.motivation.step(self.smdict, i)
            
    #     # FIXME: currently last task wins. reset s_pred to zero, accumulate
    #     # predictions respecting previously computed values
    #     return self.smdict["s_pred"]

class TaxisBrain2(Brain2):
    def __init__(self, conf, ifs_conf):
        Brain2.__init__(self, conf, ifs_conf)

    # def predict_proprio(self):
    #     for i, task in enumerate(self.tasks):
    #         self.smdict = task.motivation.step(self.smdict, i)

    #         # print "%s.predict_proprio: error_pol = %s, pred = %s" % (self.__class__.__name__, error_pol, pred)
        
    #         # # FIXME: control indexing shape
    #         # pred_idx = self.robot.get_sm_index("s_pred", "acc_pred")
    #         # # pred_idx = map(list, zip(*pred_idx))        
    #         # print "%s.predict_proprio: pred_idx = %s" % (self.__class__.__name__, pred_idx)
    #         # self.smdict["s_pred"][pred_idx] = pred
    #         # return self.smdict["s_pred"].T
        
    #     # self.smdict["s_pred"] = pred
    #     # make sure shape is (1, dim)
    #     return self.smdict["s_pred"]

class E2PBrain2(Brain2):
    def __init__(self, conf, ifs_conf):
        Brain2.__init__(self, conf, ifs_conf)

        e2p_dim = self.dim_s_proprio + self.dim_s_extero
        self.e2p = ActInfGMM(e2p_dim)
        # self.e2p = ActInfHebbianSOM(self.dim_s_extero, self.dim_s_proprio)

    def step(self, x):
        """ingest new sensory measurements into state"""
        self.step_check_input(x)

        # FIXME: do the batch fit asynchronously in a separate thread
        self.e2p.fit(self.smdict["s_extero"].T, self.smdict["s_proprio"].T)

        # print "s_pred.shape", self.smdict["s_pred"].shape
        
        for i,task in enumerate(self.tasks):
            self.smdict = task.eval(self.smdict, i)
                    
        print "s_pred.shape", self.smdict["s_pred"].shape
        prediction = self.predict_proprio()
        print "s_pred.shape", self.smdict["s_pred"].shape
        print "prediction.shape", prediction.shape
        
        assert(prediction.shape == (self.dim_s_motor, 1))
        return prediction
    
    # predict proprioceptive state             
    def predict_proprio(self):
        """produce new predictions based on state
        
        by definition proprio space is identical to motor space

        task should already provide a prediction for itself,
        brain combines potentially multiple predictions"""
        
        for i, task in enumerate(self.tasks):
            self.smdict = task.motivation.step(self.smdict, i)

        # # now cartesian angular motion is in s_pred, need to change that to proprio
        # cond = np.vstack((self.smdict["s_extero"], self.smdict["s_proprio"]))
        # cond[2:] = np.nan
        # ret = self.e2p.predict(cond)
        # intero_idx = self.get_sm_index("s_intero", "j_ang_")
        # pred_idx = self.get_sm_index("s_pred", "j_ang_vel_pred")
        # # print "ret", ret, self.smdict["s_intero"][intero_idx]
        # print "pred_idx", pred_idx, ret.shape
        # self.smdict["s_intero"][intero_idx] = ret.reshape((self.dim_s_motor, 1))
        # self.smdict["s_pred"] = ret.reshape((self.dim_s_motor, 1)) #[pred_idx]
            
        return self.smdict["s_pred"]
    
