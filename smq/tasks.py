
import numpy as np

class Task(object):
    """Base task, always minimum"""
    def __init__(self, conf):
        self.conf = conf

    def eval(self, x):
        """evaluate task over x, x being an smdict at time t, requires local memory"""
        x["s_reward"][0,0] = 0
        return x
            
class NullTask(Task):
    def __init__(self, conf):
        Task.__init__(self, conf)
            
class SetpointTask(Task):
    def __init__(self, conf):
        Task.__init__(self, conf)

class GoalTask(Task):
    def __init__(self, conf):
        Task.__init__(self, conf)
        # FIXME: general dimension, goal choice, interest model ...
        self.goal = np.random.uniform(-0.4, 0.4, (1, 1))

    def eval(self, x):
        """evaluate task over x, x being an smdict at time t, requires local memory"""
        loss = np.square(x["s_extero"] - self.goal)
        # print "loss", loss
        x["s_reward"][0,0] = loss
        x["s_intero"][2] = self.goal # FIXME: hard-coded index?
        print "Task eval", x
        return x
    
