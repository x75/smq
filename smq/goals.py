"""smq goals"""

import numpy as np
from smq.core  import SMQModule
from smq.utils import set_attr_from_dict

################################################################################
# Basic goal class
class Goal(SMQModule):
    """Basic goal, contains a basic goal datum"""
    def __init__(self, conf):
        SMQModule.__init__(self, conf)
        set_attr_from_dict(self, conf["goald"])

        # step counter
        self.cnt = 0        
        # goal vector
        self.goal = np.zeros((self.goal_dims_num, 1))
        
        # some configuration defaults
        if not self.goald.has_key("mins"):
            self.goald["mins"] = -0.7
        if not self.goald.has_key("maxs"):
            self.goald["maxs"] = 0.7

    def step(self, smdict):
        self.sample()
        self.cnt += 1
        return smdict

class JointGoal(Goal):
    """Joint goal is a joint position goal"""
    def __init__(self, conf):
        Goal.__init__(self, conf)
        self.goal = self.sample()

    def sample(self):
        return np.random.uniform(self.goald["mins"], self.goald["maxs"], (self.goal_dims_num, 1))

class PosGoal(Goal):
    """Position goal, sample a goal position for in a given space"""
    def __init__(self, conf):
        Goal.__init__(self, conf)

        # self.goal = self.sample()
        
    def sample(self):
        # FIXME: configure limits
        if hasattr(self, "goaltype"):
            if self.goaltype == "stdr_sonar":
                ret = np.array([[1.0], [0.55], [0.45]])
            elif self.goaltype == "stdr_pos":
                ret = np.array([[1], [1]])
            # elif self.goaltype == "extero_cart":
            #     # print "%s.sample: self.brain = %s" % (self.__class__.__name__, dir(self.brain))

            #     # now cartesian angular motion is in s_pred, need to change that to proprio
            #     # FIXME: all hardcoded stuff
            #     cond = np.vstack((self.brain.smdict["s_extero"], self.brain.smdict["s_proprio"]))
            #     # print "cond", cond
            #     cond[:self.brain.dim_s_extero] = np.random.uniform(-1.0, 1.0, (1, self.brain.dim_s_extero)).T
            #     # np.random.uniform([0, -1], [1, 1], (1, 2)).T
            #     cond[2:] = np.nan
            #     if self.brain.e2p.fitted:
            #         ret1 = self.brain.e2p.predict(cond).T
            #     else:
            #         ret1 = np.random.uniform(self.goald["mins"], self.goald["maxs"], (self.goal_dims_num, 1))
            #     intero_pos_goal_idx = self.brain.get_sm_index("s_intero", "pos_goal", indexdim = 2)
            #     self.brain.smdict["s_intero"][intero_pos_goal_idx] = cond[:2]
            #     # intero_idx = self.brain.get_sm_index("s_intero", "j_ang_")
            #     # pred_idx = self.brain.get_sm_index("s_pred", "j_ang_vel_pred")
            #     # print "ret", ret, self.smdict["s_intero"][intero_idx]
            #     # print "pred_idx", pred_idx, ret.shape
            #     # self.smdict["s_intero"][intero_idx] = ret.reshape((self.dim_s_motor, 1))
            #     # self.smdict["s_pred"] = ret.reshape((self.dim_s_motor, 1)) #[pred_idx]
        
            #     # ret = np.random.uniform(self.goald["mins"], self.goald["maxs"], (self.goal_dims_num, 1))
            #     print "%s.sample: goal = %s/%s" % (self.__class__.__name__, ret1.shape, ret1)
            #     # ret = ret1.T
            #     ret = ret1
            #     print "%s.sample: goal = %s/%s" % (self.__class__.__name__, ret.shape, ret)
            else:
                ret = np.random.uniform(0.0, 1.0, (self.goal_dims_num, 1))
        else:
            ret = np.random.uniform(self.goald["mins"], self.goald["maxs"], (self.goal_dims_num, 1))
        return ret

class CntPosGoal(PosGoal):
    """Counting position goal, resample a the goal after fixed number of 'resample_interval'
    time steps"""
    def __init__(self, conf):
        PosGoal.__init__(self, conf)
        self.cnt = 0

        if not hasattr(self, "resample_interval"):
            self.resample_interval = 100

    def step(self, smdict):
        smdict = PosGoal.step(self, smdict)
        if self.cnt % self.resample_interval == 0:
            self.goal = self.sample()
        
        self.cnt += 1
        return smdict

class AvgErrorPosGoal(PosGoal):
    """Average error position goal, if the average error is below a theshold 'thresh'
    sample a new goal"""
    def __init__(self, conf):
        PosGoal.__init__(self, conf)
        self.avgerror = 0.0
        self.coeff = 0.05
        self.cnt = 0

    def sample(self):
        # compute the average error
        self.avgerror = self.avgerror * (1 - self.coeff) + self.brain.smdict["s_reward"] * self.coeff
        # log average error to sm space
        avgerridx = self.brain.get_sm_index("s_intero", "avgerrorposgoal_avgerror", indexdim = 1)
        self.brain.smdict["s_intero"][avgerridx] = self.avgerror
        # check if threshold exceeded
        if self.cnt == 0 or self.cnt > 100:
            if self.avgerror < self.thresh:
                self.goal = PosGoal.sample(self)
        # FIXME: shouldn't we be logging the goal here?
        print "self.goal = %s" % self.goal
        return self.goal

################################################################################
# Exteroceptive goal class: sample a goal in exteroceptive space and translate that
# via a learned map into proprio space
class ExteroPosGoal(PosGoal):
    """Basic class for an exteroceptive goal. The primary goal exists in exteroceptive space,
    and needs to be mapped into proprioceptive space via the e2p map. Then we pursue the derived
    goal in proprioceptive space
      set proprio base goal dims and parameters
      set extero       goal dims and parameters
      sample: sample a new random (?) extero goal and ask the e2p map to convert that into a proprio goal
      pimp with avgerror for both proprio and extero
      questions:
       - one class or composition of several goals?
       - pack away functions for sampling extero goals based on current state"""
    def __init__(self, conf):
        PosGoal.__init__(self, conf)
        # check if brain is compatible with this goal type
        if not hasattr(self.brain, "e2p"):
            print "%s.__init__: wrong brain, does not seem to have an e2p module, exiting" % (self.__class__.__name__)
            raise AttributeError
        self.goal_ext = np.random.uniform(-1.0, 1.0, (1, self.brain.dim_s_extero)).T


    def sample(self):
        # now cartesian angular motion is in s_pred, need to change that to proprio
        # FIXME: all hardcoded stuff
        cond = np.vstack((self.brain.smdict["s_extero"], self.brain.smdict["s_proprio"]))
        # print "cond", cond
        self.goal_ext = np.random.uniform(-1.0, 1.0, (1, self.brain.dim_s_extero)).T
        cond[:self.brain.dim_s_extero] = self.goal_ext
        # np.random.uniform([0, -1], [1, 1], (1, 2)).T
        cond[2:] = np.nan
        if self.brain.e2p.fitted:
            print "%s.sample: brain.e2p fitted" % (self.__class__.__name__)
            ret = self.brain.e2p.predict(cond).T
        else:
            print "%s.sample: brain.e2p unfitted" % (self.__class__.__name__)
            ret = np.random.uniform(self.goald["mins"], self.goald["maxs"], (self.goal_dims_num, 1))
        intero_pos_goal_idx = self.brain.get_sm_index("s_intero", "pos_goal", indexdim = 2)
        self.brain.smdict["s_intero"][intero_pos_goal_idx] = cond[:2]
        # intero_idx = self.brain.get_sm_index("s_intero", "j_ang_")
        # pred_idx = self.brain.get_sm_index("s_pred", "j_ang_vel_pred")
        # print "ret", ret, self.smdict["s_intero"][intero_idx]
        # print "pred_idx", pred_idx, ret.shape
        # self.smdict["s_intero"][intero_idx] = ret.reshape((self.dim_s_motor, 1))
        # self.smdict["s_pred"] = ret.reshape((self.dim_s_motor, 1)) #[pred_idx]
        
        # ret = np.random.uniform(self.goald["mins"], self.goald["maxs"], (self.goal_dims_num, 1))
        print "%s.sample: goal = %s/%s" % (self.__class__.__name__, ret.shape, ret)
        self.goal = ret
        return self.goal
        # return ret

class AvgErrorExteroPosGoal(ExteroPosGoal):
    """Average error position goal, if the average error is below a theshold 'thresh'
    sample a new goal"""
    def __init__(self, conf):
        ExteroPosGoal.__init__(self, conf)
        self.avgerror_prop = 0.0 # force resample
        self.avgerror_ext  = 0.0 # 
        self.avgerror_prop_ = 0.0 # t - 1
        self.avgerror_ext_  = 0.0 #
        # difference
        # avg difference
        # FIXME: generic function to compute: error, avg error, error derivative, avg error derivative, then replace error with some signal
        self.coeff = 0.05
        self.cnt = 0
        # FIXME: rather use average change in error

    def sample(self):
        # compute the average error
        self.avgerror_prop = self.avgerror_prop * (1 - self.coeff) + self.brain.smdict["s_reward"] * self.coeff
        # log average error to sm space
        avgerrpropidx = self.brain.get_sm_index("s_intero", "avgerrorposgoal_avgerror", indexdim = 1)
        self.brain.smdict["s_intero"][avgerrpropidx] = self.avgerror_prop

        exterr = np.sum(np.square((self.brain.smdict["s_extero"] - self.goal_ext)))
        self.avgerror_ext  = self.avgerror_prop * (1 - self.coeff) + exterr * self.coeff
        
        # check if threshold exceeded
        if self.cnt == 0 or self.cnt > 100:
            if self.avgerror_prop < self.thresh or self.avgerror_ext < self.thresh:
                self.goal = ExteroPosGoal.sample(self)
        # FIXME: shouldn't we be logging the goal here?
        print "self.goal = %s" % self.goal
        return self.goal
