"""smq goals"""

import numpy as np
from smq.core  import SMQModule
from smq.utils import set_attr_from_dict

class Goal(SMQModule):
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
    def __init__(self, conf):
        Goal.__init__(self, conf)
        self.goal = self.sample()

    def sample(self):
        return np.random.uniform(self.goald["mins"], self.goald["maxs"], (self.goal_dims_num, 1))

class PosGoal(Goal):
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
            elif self.goaltype == "extero_cart":
                # print "%s.sample: self.brain = %s" % (self.__class__.__name__, dir(self.brain))

                # now cartesian angular motion is in s_pred, need to change that to proprio
                # FIXME: all hardcoded stuff
                cond = np.vstack((self.brain.smdict["s_extero"], self.brain.smdict["s_proprio"]))
                # print "cond", cond
                cond[:self.brain.dim_s_extero] = np.random.uniform(-1.0, 1.0, (1, self.brain.dim_s_extero)).T
                # np.random.uniform([0, -1], [1, 1], (1, 2)).T
                cond[2:] = np.nan
                if self.brain.e2p.fitted:
                    ret1 = self.brain.e2p.predict(cond).T
                else:
                    ret1 = np.random.uniform(self.goald["mins"], self.goald["maxs"], (self.goal_dims_num, 1))
                intero_pos_goal_idx = self.brain.get_sm_index("s_intero", "pos_goal", indexdim = 2)
                self.brain.smdict["s_intero"][intero_pos_goal_idx] = cond[:2]
                # intero_idx = self.brain.get_sm_index("s_intero", "j_ang_")
                # pred_idx = self.brain.get_sm_index("s_pred", "j_ang_vel_pred")
                # print "ret", ret, self.smdict["s_intero"][intero_idx]
                # print "pred_idx", pred_idx, ret.shape
                # self.smdict["s_intero"][intero_idx] = ret.reshape((self.dim_s_motor, 1))
                # self.smdict["s_pred"] = ret.reshape((self.dim_s_motor, 1)) #[pred_idx]
        
                # ret = np.random.uniform(self.goald["mins"], self.goald["maxs"], (self.goal_dims_num, 1))
                print "%s.sample: goal = %s/%s" % (self.__class__.__name__, ret1.shape, ret1)
                # ret = ret1.T
                ret = ret1
                print "%s.sample: goal = %s/%s" % (self.__class__.__name__, ret.shape, ret)
            else:
                ret = np.random.uniform(0.0, 1.0, (self.goal_dims_num, 1))
        else:
            ret = np.random.uniform(self.goald["mins"], self.goald["maxs"], (self.goal_dims_num, 1))
        return ret

class CntPosGoal(PosGoal):
    def __init__(self, conf):
        PosGoal.__init__(self, conf)
        self.cnt = 0

    def step(self, smdict):
        smdict = PosGoal.step(self, smdict)
        if self.cnt % 100 == 0:
            self.goal = self.sample()
        
        self.cnt += 1
        return smdict

class AvgErrorPosGoal(PosGoal):
    def __init__(self, conf):
        PosGoal.__init__(self, conf)
        self.avgerror = 0.0
        self.coeff = 0.05
        self.cnt = 0

    # def step(self, smdict):
    #     smdict = PosGoal.step(self, smdict)

    #     return smdict

    def sample(self):
        self.avgerror = self.avgerror * (1 - self.coeff) + self.brain.smdict["s_reward"] * self.coeff
        if self.cnt == 0 or self.cnt > 100:
            if self.avgerror < self.thresh:
                self.goal = PosGoal.sample(self)
        print "self.goal = %s" % self.goal
        return self.goal
