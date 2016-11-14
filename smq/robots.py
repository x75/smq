"""Robots for use in smq experiments

A robot contains a body, defined set of internal states, given brain, ...

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

    if conf["class"].__name__.startswith("Pointmass"):
        system = "pointmass"
        
    if conf["dim"] == 1:
        sysdim = "low"
    elif conf["dim"] == 3:
        sysdim = "mid"
    elif conf["dim"] == 10:
        sysdim = "high"
    
    setattr(args, "system", system)
    setattr(args, "sysdim", sysdim)
    setattr(args, "numsteps", conf["numsteps"])
    return args

class Robot(object):
    def __init__(self, conf):
        self.conf = conf

    def step(self):
        pass

class PointmassRobot(Robot):
    def __init__(self, conf):
        self.conf = conf
        print "PointmassRobot.conf", self.conf
        # print "PointmassRobot.conf", conf
        # make args from conf needing numsteps, system, sysdim
        Robot.__init__(self, self.conf)
        
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
            x = np.random.uniform(-1.0, 1.0, (self.conf["dim"], 1))
        # 1. s = get sensors
        # 2. m = ask brain(s)
        # 3. w = ask_world(m)
        return x.reshape(self.conf["dim"],)
        
