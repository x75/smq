
import numpy as np

# from smq.utils import set_attr_from_dict
from smq.core  import SMQModule

################################################################################
# v2 style
class Task2(SMQModule):
    """Base task, always minimum"""
    def __init__(self, conf, ref):
        SMQModule.__init__(self, conf)

        # goal specification
        self.goal_dims_num = 0
        self.goal_dims = {}

        # numerical indices into s_intero for goal and error
        self.intero_goal_idx_num =  []
        self.intero_error_idx_num = []

        # compute more member values from configuration dict
        self.prepare(ref)

        # compute submodule members
        self.goal       = conf["goal"](self.conf)
        self.error      = conf["error"](self.conf)
        self.measure    = conf["measure"](self.conf)
        self.motivation = conf["motivation"](self.conf)

    def eval(self, x, i):
        """evaluate task over x, x being an smdict at time t, requires local memory"""
        # collect variables that we want to compare to the goal
        goal_comparison = np.vstack([x[k][self.goal_dims[k]] for k in self.goal_dims.keys()])
        
        # make sure there are compatible
        assert(goal_comparison.shape == self.goal.goal.shape)

        # compute the error
        self.error.step(goal_comparison, self.goal.goal)

        # compute the distance
        self.measure.step(self.error.error)

        # assign new values intero variables
        x["s_intero"][self.intero_goal_idx_num] = self.goal.goal # FIXME: hard-coded index?
        x["s_intero"][self.intero_error_idx_num] = self.error.error # FIXME: hard-coded index?
        x["s_reward"][i,0] = self.measure.measure

        # and return the dict
        return x

    def prepare(self, brain):
        # keep reference to brain
        self.brain = brain
        # some index magic for goal reference variables
        for k,v in self.goal_dims_dict.items():
            self.goal_dims[k] = []
            for gdim in v:
                # print v, self.brain.smdict_index[k]
                self.goal_dims[k].append(self.brain.smdict_index[k][gdim])
                self.goal_dims_num += 1

        # index magic for goal and error variables
        for item in self.intero_goal_idx:
            # print item
            self.intero_goal_idx_num.append(self.brain.smdict_index["s_intero"][item])
        for item in self.intero_error_idx:
            # print item
            self.intero_error_idx_num.append(self.brain.smdict_index["s_intero"][item])

        for item in ["brain", "goal_dims_num", "goal_dims", "intero_goal_idx_num", "intero_error_idx_num", "goaltype"]:
            if hasattr(self, item):
                self.conf[item] = getattr(self, item)

# FIXME: these two don't seem to do anything special, remove
class GoalTask2(Task2):
    def __init__(self, conf, ref):
        Task2.__init__(self, conf, ref)

    def prepare(self, brain):
        Task2.prepare(self, brain)
                            
class GoalTaskTaxis2(Task2):
    def __init__(self, conf, ref):
        Task2.__init__(self, conf, ref)
        
    def prepare(self, brain):
        Task2.prepare(self, brain)
    
