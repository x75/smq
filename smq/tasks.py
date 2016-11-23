
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
        self.goal = np.random.uniform(-0.7, 0.7, (self.conf["goaldim"], 1))

    def eval(self, x):
        """evaluate task over x, x being an smdict at time t, requires local memory"""
        # print '%s.eval x["%s"].shape = %s, goal.shape = %s' % (self.__class__.__name__, self.goalspace, x[self.goalspace].shape, self.goal.shape)
        print '%s.eval x["%s"] = %s, goal = %s' % (self.__class__.__name__, self.goalspace, x[self.goalspace], self.goal)
        loss = np.sum(np.square(x[self.goalspace] - self.goal))
        # loss = np.sum(np.abs(x["s_extero"] - self.goal))
        # print "loss", loss
        x["s_reward"][0,0] = loss
        # print '%s.eval x["s_intero"] = %s' % (self.__class__.__name__, x["s_intero"])
        # x["s_intero"][2] = self.goal # FIXME: hard-coded index?
        x["s_intero"][self.intero_index:] = self.goal # FIXME: hard-coded index?
        # print "Task eval", x
        return x
    
class GoalTaskTaxis(Task):
    def __init__(self, conf):
        Task.__init__(self, conf)

    def synthesize_goal(self):
        # FIXME: general dimension, goal choice, interest model ...
        self.goal = np.random.uniform(-0.7, 0.7, (self.conf["goaldim"], 1))
        goal_sm_idx = self.brain.robot.get_sm_index("s_intero", "vel_goal")
        self.brain.robot.smdict["s_intero"][goal_sm_idx] = self.goal

    def eval(self, x):
        if not hasattr(self, "goal"):
            self.synthesize_goal()
        self.eval = self.eval2 # HACK?
        return self.eval(x)

    def eval2(self, x):
        """evaluate task over x, x being an smdict at time t, requires local memory"""
        # print '%s.eval x["s_extero"].shape = %s, goal.shape = %s' % (self.__class__.__name__, x["s_extero"].shape, self.goal.shape)
        # print '%s.eval x["s_extero"].shape = %s, goal.shape = %s' % (self.__class__.__name__, x["s_extero"].shape, self.goal.shape)
        error_sm_idx = self.brain.robot.get_sm_index("s_intero", "vel_error")
        # print '%s.%s error_sm_idx = %s' % (self.__class__.__name__, self.eval2.__name__, error_sm_idx)
        
        error = x["s_extero"] - self.goal
        self.brain.robot.smdict["s_intero"][error_sm_idx] = error
        # print "%s.eval: error = %s" % (self.__class__.__name__, error)
        # loss = np.sum(np.square(x["s_extero"] - self.goal))
        # loss = np.sum(np.abs(x["s_extero"] - self.goal))
        # print "loss", loss
        loss = np.sum(np.abs(error))
        x["s_reward"][0,0] = loss
        # print '%s.eval x["s_intero"] = %s' % (self.__class__.__name__, x["s_intero"])
        # x["s_intero"][2] = self.goal # FIXME: hard-coded index?
        # x["s_intero"][goal] = self.goal # FIXME: hard-coded index?
        # print "Task eval", x
        return x

################################################################################
# 
class Task2(object):
    """Base task, always minimum"""
    def __init__(self, conf):
        self.conf = conf
        set_attr_from_dict(self, self.conf)

    def eval(self, x, i):
        """evaluate task over x, x being an smdict at time t, requires local memory"""
        x["s_reward"][0,0] = 0
        return x

class GoalTask2(Task2):
    def __init__(self, conf):
        Task2.__init__(self, conf)

        self.goal_dims_num = 0
        self.goal_dims = {}

        # numerical indices into s_intero for goal and error
        self.intero_goal_idx_num =  []
        self.intero_error_idx_num = []
        
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

        # print self.intero_goal_idx_num, self.intero_error_idx_num
              
        # print "self.goal_dims", self.goal_dims
        self.goal = np.random.uniform(-0.7, 0.7, (self.goal_dims_num, 1))
        self.error = np.zeros_like(self.goal)
        
    def eval(self, x, i):
        """evaluate task over x, x being an smdict at time t, requires local memory"""
        # print '%s.eval x["%s"] = %s, goal = %s' % (self.__class__.__name__, self.goal_dims, x[self.goalspace], self.goal)
        # print "x", x
        goal_comparison = np.vstack([x[k][self.goal_dims[k]] for k in self.goal_dims.keys()])
        # print "goal_comparison", goal_comparison
        assert(goal_comparison.shape == self.goal.shape)
        self.error = goal_comparison - self.goal
        loss = np.sum(np.square(self.error))
        
        x["s_intero"][self.intero_goal_idx_num] = self.goal # FIXME: hard-coded index?
        x["s_intero"][self.intero_error_idx_num] = self.error # FIXME: hard-coded index?
        x["s_reward"][i,0] = loss

        return x
    
class GoalTaskTaxis2(Task2):
    def __init__(self, conf):
        Task2.__init__(self, conf)

        self.goal_dims_num = 0
        self.goal_dims = {}

        # numerical indices into s_intero for goal and error
        self.intero_goal_idx_num =  []
        self.intero_error_idx_num = []
        
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

        # print self.intero_goal_idx_num, self.intero_error_idx_num
              
        # print "self.goal_dims", self.goal_dims
        # self.goal = np.random.uniform(-0.7, 0.7, (self.goal_dims_num, 1))
        self.synthesize_goal()
        self.error = np.zeros_like(self.goal)
        
    def synthesize_goal(self):
        # FIXME: general dimension, goal choice, interest model ...
        # FIXME: goal itself must be structured like smdict
        self.goal = np.random.uniform(-0.7, 0.7, (self.goal_dims_num, 1))
        # print self.goal_dims
        
        # goal_sm_idx = self.brain.get_sm_index("s_intero", "vel_goal")
        # self.brain.smdict["s_intero"][goal_sm_idx] = self.goal
        
        for k,v in self.goal_dims.items():
            self.brain.smdict[k][v] = self.goal

    def eval(self, x, i):
        """evaluate task over x, x being an smdict at time t, requires local memory"""
        # print '%s.eval x["s_extero"].shape = %s, goal.shape = %s' % (self.__class__.__name__, x["s_extero"].shape, self.goal.shape)
        # print '%s.eval x["s_extero"].shape = %s, goal.shape = %s' % (self.__class__.__name__, x["s_extero"].shape, self.goal.shape)
        # error_sm_idx = self.brain.get_sm_index("s_intero", "vel_error")
        # print '%s.%s error_sm_idx = %s' % (self.__class__.__name__, self.eval2.__name__, error_sm_idx)

        goal_comparison = np.vstack([x[k][self.goal_dims[k]] for k in self.goal_dims.keys()])
        assert(goal_comparison.shape == self.goal.shape)
        self.error = goal_comparison - self.goal
        
        # error = x["s_extero"] - self.goal
        # print "%s.eval: error = %s" % (self.__class__.__name__, error)
        # loss = np.sum(np.square(x["s_extero"] - self.goal))
        # loss = np.sum(np.abs(x["s_extero"] - self.goal))
        # print "loss", loss
        # loss = np.sum(np.square(self.error))
        loss = np.sum(np.abs(self.error))
        
        # x["s_reward"][0,0] = loss
        x["s_intero"][self.intero_goal_idx_num] = self.goal # FIXME: hard-coded index?
        x["s_intero"][self.intero_error_idx_num] = self.error # FIXME: hard-coded index?
        # self.brain.smdict["s_intero"][error_sm_idx] = self.error
        x["s_reward"][i,0] = loss
        
        # print '%s.eval x["s_intero"] = %s' % (self.__class__.__name__, x["s_intero"])
        # x["s_intero"][2] = self.goal # FIXME: hard-coded index?
        # x["s_intero"][goal] = self.goal # FIXME: hard-coded index?
        # print "Task eval", x
        return x
    
