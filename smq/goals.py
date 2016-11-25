"""smq goals"""

import numpy as np
from smq.core  import SMQModule
from smq.utils import set_attr_from_dict

class Goal(SMQModule):
    def __init__(self, conf):
        SMQModule.__init__(self, conf)
        set_attr_from_dict(self, conf["goald"])
        
        # goal vector
        self.goal = np.zeros((self.goal_dims_num, 1))
        
        # some configuration defaults
        if not self.goald.has_key("mins"):
            self.goald["mins"] = -0.7
        if not self.goald.has_key("maxs"):
            self.goald["maxs"] = 0.7

    def step(self, smdict):
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

        self.goal = self.sample()

    def sample(self):
        # FIXME: configure limits
        if hasattr(self, "goaltype"):
            if self.goaltype == "stdr_sonar":
                ret = np.array([[1.0], [0.55], [0.45]])
            elif self.goaltype == "stdr_pos":
                ret = np.array([[1], [1]])
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

    def step(self, smdict):
        smdict = PosGoal.step(self, smdict)

        self.avgerror = self.avgerror * (1 - self.coeff) + smdict["s_reward"] * self.coeff
        if self.cnt > 100:
            if self.avgerror < self.thresh:
                self.goal = self.sample()
        else:
            self.cnt += 1
        
        return smdict
