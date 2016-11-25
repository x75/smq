"""smq goals"""

import numpy as np
from smq.core import SMQModule

class Goal(SMQModule):
    def __init__(self, conf):
        SMQModule.__init__(self, conf)
        self.goal = np.zeros((self.goal_dims_num, 1))

class JointGoal(Goal):
    def __init__(self, conf):
        Goal.__init__(self, conf)
        # FIXME: configure limits
        self.goal = np.random.uniform(-0.7, 0.7, (self.goal_dims_num, 1))

class PosGoal(Goal):
    def __init__(self, conf):
        Goal.__init__(self, conf)
        # FIXME: configure limits
        if hasattr(self, "goaltype"):
            if self.goaltype == "stdr_sonar":
                self.goal = np.array([[1.0], [0.55], [0.45]])
            elif self.goaltype == "stdr_pos":
                self.goal = np.array([[1], [1]])
            else:
                self.goal = np.random.uniform(0.0, 1.0, (self.goal_dims_num, 1))
        else:
            self.goal = np.random.uniform(-0.7, 0.7, (self.goal_dims_num, 1))
       
