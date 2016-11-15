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
        env_conf_str = "low_dim_vel"
        # env_conf_str = "low_dim_full"
    elif args.sysdim == "mid":
        env_conf_str = "mid_dim_vel"
    elif args.sysdim == "high":
        env_conf_str = "high_dim_vel"
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
        
    if conf["mdim"] == 1:
        sysdim = "low"
    elif conf["mdim"] == 3:
        sysdim = "mid"
    elif conf["mdim"] == 10:
        sysdim = "high"
    
    setattr(args, "system", system)
    setattr(args, "sysdim", sysdim)
    setattr(args, "numsteps", conf["numsteps"])
    return args

class Robot(object):
    def __init__(self, conf):
        self.conf = conf
        # yeah, which dim: DoF sensorimotor, DoF locomotion, sensor dim, motor dim, ...
        self.sdim   = self.conf["sdim"]
        self.mdim   = self.conf["mdim"]

    def step(self):
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
        self.x = np.zeros((self.sdim, 1))
        self.y = np.zeros((self.mdim, 1))
        
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
            self.x = np.random.uniform(-1.0, 1.0, (self.sdim, 1))
        # print "x", x
        # 1. s = get sensors
        s = x.copy()
        # 2. m = ask brain(s)
        m = s + (np.random.binomial(3, 0.05) * 0.01 * (np.random.binomial(1, 0.5) * 2 -1))
        # 3. w = ask_world(m)
        # return self.x.reshape(self.mdim,)
        self.y = m.reshape(self.mdim,)
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
        self.x = np.zeros((self.sdim, 1))
        self.y = np.zeros((self.mdim, 1))
        
        if self.conf["type"] == "explauto":
            # print "expl"
            args = make_args_from_(self.conf)
            self.env = get_context_environment(args)
            print "dir(self.env)", dir(self.env)
            # print "env_cls", env_cls
            # print "env_conf", env_conf
            # reset environment
            self.env.reset()
            print "self.env", self.env
        
    def step(self, x):
        """step the robot: input is vector of new information $x$ from the world"""
        print "PointmassRobot.step x", x
        if x is None: # catch initial state
            self.x = np.random.uniform(-1.0, 1.0, (self.sdim, 1))
        # print "x", x
        # 1. s = get sensors
        s = x.copy()
        # 2. m = ask brain(s)
        m = self.env.compute_motor_command(np.random.uniform(-0.1, 0.1, (self.mdim, 1)))
        print "m", m
        # m = s + (np.random.binomial(3, 0.05) * 0.01 * (np.random.binomial(1, 0.5) * 2 -1))
        # 3. w = ask_world(m)
        # return self.x.reshape(self.mdim,)
        self.y = m.reshape(self.mdim,)
        return self.y
