"""smq measures"""

import numpy as np
from smq.core import SMQModule

class Measure(SMQModule):
    def __init__(self, conf):
        SMQModule.__init__(self, conf)
        self.measure = np.zeros((self.goal_dims_num, 1))

    def step(self, error):
        self.measure = np.sum(np.square(error))

class MSEMeasure(Measure):
    """Mean squared error measure"""
    def __init__(self, conf):
        Measure.__init__(self, conf)
