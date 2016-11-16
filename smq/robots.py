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

from smq.utils import get_items

#######################################################################
# copied from smp.environments, methods for constructing explauto based
# environments
def get_context_environment(args):
    from explauto.environment.context_environment import ContextEnvironment
    
    if args.system == "pointmass":
        env_cls, env_conf = get_context_environment_pointmass(args)
    elif args.system == "simplearm":
        env_cls, env_conf = get_context_environment_simplearm(args)
    elif args.system == "morse_copter":
        env_cls, env_conf = get_context_environment_morse_copter(args)

    # print ("env_conf", env_conf)
    try:
        s_ndims = env_conf["s_ndims"]
    except KeyError, e:
        s_ndims = len(env_conf["s_mins"])
    context_mode = dict(mode='mcs',
                    reset_iterations = args.numsteps, # 100, # 
                    context_n_dims = s_ndims,
                    context_sensory_bounds=[env_conf["s_mins"],
                                            env_conf["s_maxs"]])

    environment = ContextEnvironment(env_cls, env_conf, context_mode)
    return environment
    
def get_context_environment_pointmass(args):
    from explauto.environment import environments
    from explauto.environment.pointmass import PointmassEnvironment
    
    env_cls = PointmassEnvironment
    
    if args.sysdim == "low":
        env_conf_str = "low_dim_acc_vel"
        # env_conf_str = "low_dim_full"
    elif args.sysdim == "planar":
        env_conf_str = "planar_dim_acc_vel"
    elif args.sysdim == "mid":
        env_conf_str = "mid_dim_acc_vel"
    elif args.sysdim == "high":
        env_conf_str = "high_dim_acc_vel"
    env_conf = environments['pointmass'][1][env_conf_str]
    return env_cls, env_conf

def get_context_environment_simplearm(args):
    from explauto.environment import environments
    
    env_cls = SimpleDynamicArmEnvironment
    
    if args.sysdim == "low":
        env_conf_str = "low_dimensional"
        # env_conf_str = "low_dim_full"
    elif args.sysdim == "mid":
        env_conf_str = "mid_dimensional"
    elif args.sysdim == "high":
        env_conf_str = "high_dimensional"
        
    env_conf = environments['simple_arm'][1][env_conf_str]
    # print("env_cls, env_conf", env_cls, env_conf)
    return env_cls, env_conf

def get_context_environment_morse_copter(args):
    from explauto.environment import environments
    from explauto.environment.morse import CopterMorseEnvironment
    env_cls = CopterMorseEnvironment
    env_conf = environments['morse'][1]['copter_attitude']
    return env_cls, env_conf    

def make_args_from_(conf):
    """make args Namespace from config variables"""
    from argparse import Namespace
    args = Namespace()

    if conf["class"].__name__.startswith("PointmassRobot"):
        system = "pointmass"
    elif conf["class"].__name__.startswith("SimpleRandomRobot"):
        system = "pointmass"
        
    if len(conf["dim_s_motor"]) == 1:
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
        self.smdict = OrderedDict()
        self.smstruct = ["dim_s_proprio", "dim_s_extero", "dim_s_intero", "dim_s_reward", "dim_s_pred", "dim_s_motor"]
        self.smattrs  = ["dim", "dimnames", "smdict", "smstruct", "sm", "smattrs"]
        
        # more differentiated sm space description
        for k in self.smstruct:
            # dim of that part is length of fields array
            dim_ = len(conf[k])
            # set the class attribute
            setattr(self, k, dim_)
            # count overall dims
            self.dim += dim_
            
            for dimname in conf[k]:
                self.dimnames.append(dimname)
            k_ = k.replace("dim_", "")
            self.smdict[k_] = np.zeros((dim_, 1))
            # add raw field names
            # self.dimcolumns.append(conf[k])
        self.smdict_concat = [None for i in range(self.dim)]
        
        print "%s.__init__ full sm dim = %d, names = %s, %s" % (self.__class__.__name__, self.dim, self.dimnames, self.smdict)
        self.sm = np.zeros((self.dim, 1)) # full sensorimotor vector, use dict?

        # brains, only one
        for attr in self.smattrs:
            # print attr, getattr(self, attr)
            self.conf["brains"][0][attr] = getattr(self, attr)
        # print self.conf["brains"]
        self.brains = get_items(self.conf["brains"])
        assert(len(self.brains) == 1) # not ready for that yet
                
    def step(self):
        """execute one time-step, this refers to updating robot brain with
        new sensor data and producing a prediction"""
        pass

    def update(self, prediction):
        """update the robot/system by 'executing' the prediction"""
        pass

class SimpleRandomRobot(Robot):
    def __init__(self, conf):
        self.conf = conf
        print "PointmassRobot.conf", self.conf
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
            print "self.env", self.env
        
    def step(self, x):
        """step the robot: input is vector of new information $x$ from the world"""
        print "PointmassRobot.step x", x
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
        print "PointmassRobot.conf", self.conf
        # print "PointmassRobot.conf", conf
        # make args from conf needing numsteps, system, sysdim
        Robot.__init__(self, self.conf)
        # ROS
        if self.conf["ros"] is True:
            import rospy
            rospy.init_node("%s" % self.conf["name"])
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
            print "self.env", self.env

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
        # print "logdata", logdata
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
            # print "prediction",prediction
            # a_ = np.random.uniform(-0.1, 0.1, (1, self.dim_s_motor))
        
        # print "s_pred 3", self.smdict["s_pred"]
        m_ = self.env.compute_motor_command(prediction).T # transpose to comply with smdict
        # print "m_", m_.shape, m_, "s_pred", self.smdict["s_pred"]
        self.smdict["s_pred"] = m_
        self.smdict["s_motor"] = m_.reshape((self.dim_s_motor, 1))
        print "%s.step m = %s" % (self.__class__.__name__, self.smdict["s_motor"])
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
