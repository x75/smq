"""Robots for use in smq experiments

A robot contains a body, defined set of internal states, given brain, ...

(c) 2016 Oswald Berthold
"""

# Implementations:
#  # these are limited to 1D/2D
#  - smp.ode_inert_system.InertParticle, 
#  - smp.ode_inert_system.InertParticle2D
#  - smp.ode_inert_system.InertParticleND
#
#  # these are incomplete / defunct
#  - smpsim.point_mass_experiment
#
#  # imol.robots.robots.Pointmass,...
#  - 
#
#  # probably the best, disentangle from explauto
#  - explauto.environments.pointmass

# TODO: pm, sa, random, sphero, morse, nao, ...

import numpy as np
from collections import OrderedDict

from smq.utils import get_items, set_attr_from_dict
from smp.environments import get_context_environment, get_context_environment_pointmass, get_context_environment_simplearm, get_context_environment_morse_copter

def make_args_from_(conf):
    """make args Namespace from config variables"""
    from argparse import Namespace
    args = Namespace()

    if conf["class"].__name__.startswith("PointmassRobot"):
        system = "pointmass"
    elif conf["class"].__name__.startswith("SimpleRandomRobot"):
        system = "pointmass"
    elif conf["class"].__name__.startswith("SimplearmRobot"):
        system = "simplearm"
        
    if len(conf["dim_s_motor"]) == 1:
        if conf["control"] == "vel":
            sysdim = "low_c1"
        else:
            sysdim = "low"
    elif len(conf["dim_s_motor"]) == 2:
        sysdim = "planar"
    elif len(conf["dim_s_motor"]) in range(3,10):
        sysdim = "mid"
    elif len(conf["dim_s_motor"]) >= 10:
        sysdim = "high"
    
    setattr(args, "system", system)
    setattr(args, "sysdim", sysdim)
    setattr(args, "numsteps", conf["numsteps"])
    return args

class Robot(object):
    def __init__(self, conf):
        self.conf = conf
        # yeah, which dim: DoF sensorimotor, DoF locomotion, sensor dim, motor dim, ...
        self.dim    = 0
        self.dimnames = []
        # self.dimcolumns = []
        self.smdict       = OrderedDict()
        self.smdict_index = OrderedDict()
        # let's call these "dimension groups"
        self.smstruct = ["dim_s_proprio", "dim_s_extero", "dim_s_intero", "dim_s_reward", "dim_s_pred", "dim_s_motor"]
        self.smattrs  = ["dim", "dimnames", "smdict", "smstruct", "sm", "smattrs"]

        # default copy conf items into member vars
        set_attr_from_dict(self, conf) # check that this is OK
                
        # sensorimotor space representation
        for k in self.smstruct:
            # smdict key
            k_ = k.replace("dim_", "")
            
            # dim of that part is length of fields array
            dim_ = len(conf[k])
            
            # set the class attribute
            setattr(self, k, dim_)
            
            # count overall dims
            self.dim += dim_

            # collect all variable names
            self.smdict_index[k_] = {}
            for i, dimname in enumerate(conf[k]):
                # this is local index for given dim group
                self.smdict_index[k_][dimname] = i
                # this is globally associated with self.sm
                self.dimnames.append(dimname)
                
            self.smdict[k_] = np.zeros((dim_, 1))
            # self.dimcolumns.append(conf[k])
        self.smdict_concat = [None for i in range(self.dim)] # don't need this
        self.sm = np.zeros((self.dim, 1)) # full sensorimotor vector, use dict?

        # debug
        # print "%s.__init__ full sm dim = %d, names = %s, %s" % (self.__class__.__name__, self.dim, self.dimnames, self.smdict)
        print "%s.__init__ full\n       #dims = %d\n    dimnames = %s\nsmdict_index = %s\n" % \
          (self.__class__.__name__, self.dim, self.dimnames, self.smdict_index)
                    
        ################################################################################
        # brain only one
        
        # brain prepare config by copying robot attributes to brain config
        for attr in self.smattrs:
            # print attr, getattr(self, attr)
            self.conf["brains"][0][attr] = getattr(self, attr)
            
        # brain instantiate
        self.brains = get_items(self.conf["brains"])
        
        # brain shouldn't we just pass a robot self reference down into the brain?
        for brain in self.brains:
            brain.robot = self
            
        assert(len(self.brains) == 1) # not ready for that yet

        if self.conf["type"] == "explauto":
            # print "expl"
            args = make_args_from_(self.conf)
            self.env = get_context_environment(args)
            # print "dir(self.env)", dir(self.env)
            # print "env_cls", env_cls
            # print "env_conf", env_conf
            # reset environment
            self.env.reset()
            # print "self.env", self.env
        
        # communication / logging
        # ROS
        if self.conf["ros"] is True:
            import rospy
            rospy.init_node("%s" % self.conf["name"])

    def get_sm_index(self, dimgroup, base):
        # FIXME: make the goal dim configurable etc on this level
        return [self.smdict_index[dimgroup]["%s%d" % (base, k)] for k in range(self.dim_s_motor)]
    
    def step(self, x):
        """execute one time-step, this refers to updating robot brain with
        new sensor data and producing a prediction"""
        pass

    def update(self, prediction):
        """update the robot/system by 'executing' the prediction"""
        pass
    
class SimpleRandomRobot(Robot):
    def __init__(self, conf):
        self.conf = conf
        print "%s.__init__ self.conf = %s" % (self.__class__.__name__, self.conf)
        # print "PointmassRobot.conf", conf
        # make args from conf needing numsteps, system, sysdim
        Robot.__init__(self, self.conf)
        # ROS
        if self.conf["ros"] is True:
            import rospy
            rospy.init_node("%s" % self.conf["name"])
        self.x = np.zeros((self.dim_s_proprio, 1))
        self.y = np.zeros((self.dim_s_motor, 1))
        
        if self.conf["type"] == "explauto":
            # print "expl"
            args = make_args_from_(self.conf)
            self.env = get_context_environment(args)
            # print "env_cls", env_cls
            # print "env_conf", env_conf
            # reset environment
            self.env.reset()
            print "%s.__init__ self.env = %s" %(self.__class__.__name__,  self.env)
        
    def step(self, x):
        """step the robot: input is vector of new information $x$ from the world"""
        print "%s.step x = %s" % (self.__class__.__name__, x)
        if x is None: # catch initial state
            self.x = np.random.uniform(-1.0, 1.0, (self.dim_s_proprio, 1))
        # print "x", x
        # 1. s = get sensors
        s = x.copy()
        # 2. m = ask brain(s)
        m = s + (np.random.binomial(3, 0.05) * 0.01 * (np.random.binomial(1, 0.5) * 2 -1))
        # 3. w = ask_world(m)
        # return self.x.reshape(self.mdim,)
        self.y = m.reshape(self.dim_s_motor,)
        return self.y
    
class PointmassRobot(Robot):
    def __init__(self, conf):
        self.conf = conf
        # print "PointmassRobot.conf", self.conf
        # print "PointmassRobot.conf", conf
        # make args from conf needing numsteps, system, sysdim
        Robot.__init__(self, self.conf)
        
        # robot i/o data, FIXME: pack it all into dictionary
        # self.x = np.zeros((self.sdim, 1))
        # self.y = np.zeros((self.mdim, 1))
        
        if self.conf["type"] == "explauto":
            # print "expl"
            args = make_args_from_(self.conf)
            self.env = get_context_environment(args)
            # print "dir(self.env)", dir(self.env)
            # print "env_cls", env_cls
            # print "env_conf", env_conf
            # reset environment
            self.env.reset()
            # print "self.env", self.env

    def get_logdata_columns(self):
        """collect all internal variables and their names and return ordered
        list of names corresponding to order in sm vector"""
        return self.dimnames
        
    def get_logdata(self):
        """collect all internal variables, stack them into one vector and
        return that"""
        # logdata = np.atleast_2d(np.hstack((self.x, self.y))).T
        # acc, vel, pos, dist_goal, acc_pred, acc_motor

        # for k in self.smdict.keys():
        #     print "self.smdict[%s]" % (k), self.smdict[k].shape
        
        logdata = np.atleast_2d(np.vstack([self.smdict[k] for k in self.smdict.keys()]))
        print "%s.get_logdata, logdata.shape = %s, self.dim = %d" % (self.__class__.__name__, logdata.shape, self.dim)
        # logdata = np.atleast_2d(np.hstack((self.x, self.y))).T
        return logdata
            
    def step(self, x):
        """step the robot:
        input is vector of new information $x$ from the world

        essentially: step the robot brain
        """
        # debug
        print "%s.step x = %s" % (self.__class__.__name__, x.shape)
        
        # 1. get sensors
        if x is None: # catch initial state
            # self.x = np.random.uniform(-1.0, 1.0, (self.sdim, 1))
            self.smdict["s_proprio"] = np.random.uniform(-1.0, 1.0, (self.dim_s_proprio, 1))
            self.smdict["s_extero"]  = np.random.uniform(-1.0, 1.0, (self.dim_s_extero,  1))
        else:
            self.smdict["s_proprio"] = x[self.dim_s_extero:].copy() # HACK?
            self.smdict["s_extero"]  = x[:self.dim_s_extero].copy() # HACK?
            
        # print "s_pred 1", self.smdict["s_pred"]
        # 2. m = ask brain to fill in things, no brain yet but hey
        for brain in self.brains:
            # print "brain",i
            self.smdict = brain.step(self.smdict)
            # print "s_pred 2", self.smdict["s_pred"]
            prediction = brain.predict_proprio()
            print "%s.step prediction.shape = %s" %(self.__class__.__name__,  prediction.shape)
            # a_ = np.random.uniform(-0.1, 0.1, (1, self.dim_s_motor))
        
        # print "s_pred 3", self.smdict["s_pred"]
        
        # m_ retains input shape?
        # m_ = self.env.compute_motor_command(np.squeeze(prediction, axis=0)).T # transpose to comply with smdict
        # print "m_.shape", m_.shape
        
        m_ = self.env.compute_motor_command(prediction).T # transpose to comply with smdict
        print "m_.shape", m_.shape
        # print "m_", m_.shape, m_, "s_pred", self.smdict["s_pred"]
        self.smdict["s_pred"] = m_
        self.smdict["s_motor"] = m_.reshape((self.dim_s_motor, 1))
        # print "%s.step m = %s" % (self.__class__.__name__, self.smdict["s_motor"])
        # m = s + (np.random.binomial(3, 0.05) * 0.01 * (np.random.binomial(1, 0.5) * 2 -1))
        # 3. w = ask_world(m)
        # return self.x.reshape(self.mdim,)
        # self.y = self.smdict["s_motor"].reshape(self.dim_s_motor,)
        # print "dimcomaprison smdict[\"s_motor\"] vs. y", self.smdict["s_motor"].shape, self.y.shape
        # return brain answer
        return np.squeeze(self.smdict["s_motor"], axis=1)

    def update(self, prediction):
        """let the body and forces induced by the robot's predictions interact with the world and yield effect"""
        x_ = np.atleast_2d(self.env.compute_sensori_effect(prediction)).T
        # self.x = self.env.update(prediction)
        # x_ = self.env.update(prediction, reset=False)
        # print "update: x_", x_.shape
        return x_


################################################################################
# simple arm / explauto
class SimplearmRobot(Robot):
    def __init__(self, conf):
        self.conf = conf
        Robot.__init__(self, self.conf)

    def get_logdata(self):
        pass
        
    def step(self, x):
        """step the robot:
        input is vector of new information $x$ from the world

        essentially: step the robot brain
        """
        # debug
        print "%s.step x.shape = %s" % (self.__class__.__name__, x.shape)
        
        # 1. get sensors
        if x is None: # catch initial state
            # self.x = np.random.uniform(-1.0, 1.0, (self.sdim, 1))
            self.smdict["s_proprio"] = np.random.uniform(-1.0, 1.0, (self.dim_s_proprio, 1))
            self.smdict["s_extero"]  = np.random.uniform(-1.0, 1.0, (self.dim_s_extero,  1))
        else:
            self.smdict["s_proprio"] = x[self.dim_s_extero:].copy() # HACK?
            self.smdict["s_extero"]  = x[:self.dim_s_extero].copy() # HACK?
            
        # print "s_pred 1", self.smdict["s_pred"]
        # 2. m = ask brain to fill in things, no brain yet but hey
        for brain in self.brains:
            # print "brain",i
            self.smdict = brain.step(self.smdict)
            # print "s_pred 2", self.smdict["s_pred"]
            prediction = brain.predict_proprio()
            print "%s.step prediction.shape = %s" %(self.__class__.__name__,  prediction.shape)
            # a_ = np.random.uniform(-0.1, 0.1, (1, self.dim_s_motor))
            
        m_ = self.env.compute_motor_command(prediction).T # transpose to comply with smdict
        print "m_.shape", m_.shape
        # print "m_", m_.shape, m_, "s_pred", self.smdict["s_pred"]
        self.smdict["s_pred"] = m_
        self.smdict["s_motor"] = m_.reshape((self.dim_s_motor, 1))
        
        return np.squeeze(self.smdict["s_motor"], axis=1)
        

    def update(self, prediction):
        pass
