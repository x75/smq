
import numpy as np

from smq.utils import set_attr_from_dict

class Task(object):
    """Base task, always minimum"""
    def __init__(self, conf):
        self.conf = conf
        set_attr_from_dict(self, conf)

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
        self.goal = np.random.uniform(-0.4, 0.4, (self.conf["goaldim"], 1))

    def eval(self, x):
        """evaluate task over x, x being an smdict at time t, requires local memory"""
        # print '%s.eval x["s_extero"].shape = %s, goal.shape = %s' % (self.__class__.__name__, x["s_extero"].shape, self.goal.shape)
        # print '%s.eval x["s_extero"].shape = %s, goal.shape = %s' % (self.__class__.__name__, x["s_extero"].shape, self.goal.shape)
        loss = np.sum(np.square(x["s_extero"] - self.goal))
        # loss = np.sum(np.abs(x["s_extero"] - self.goal))
        # print "loss", loss
        x["s_reward"][0,0] = loss
        # print '%s.eval x["s_intero"] = %s' % (self.__class__.__name__, x["s_intero"])
        # x["s_intero"][2] = self.goal # FIXME: hard-coded index?
        x["s_intero"][self.intero_index:] = self.goal # FIXME: hard-coded index?
        # print "Task eval", x
        return x
    
