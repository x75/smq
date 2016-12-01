"""smq errors"""

import numpy as np
from smq.core  import SMQModule
from smq.utils import ct_pol2car, ct_car2pol

class Error(SMQModule):
    def __init__(self, conf):
        SMQModule.__init__(self, conf)
        self.error = np.zeros((self.goal_dims_num, 1))

    def step(self, state, goal):
        print "goal = %s" % (goal)
        self.error = state - goal

class DifferenceError(Error):
    def __init__(self, conf):
        Error.__init__(self, conf)

class AngularError(Error):
    def __init__(self, conf):
        Error.__init__(self, conf)

    def step(self, state, goal):
        pass
