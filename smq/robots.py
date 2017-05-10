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

import time
import numpy as np
from collections import OrderedDict

try:
    import rospy
    from tf.transformations import euler_from_quaternion, quaternion_from_euler
except Exception, e:
    print "import rospy failed", e

from smq.utils import get_items, set_attr_from_dict, set_attr_from_dict_ifs
from smp.environments import get_context_environment, get_context_environment_pointmass, get_context_environment_simplearm, get_context_environment_morse_copter

def get_sysdim_string_for_robot(system, dim, control = None):
    if system == "pointmass":
        if len(dim) == 1:
            if control == "vel":
                sysdim = "low_c1"
            else:
                sysdim = "low"
        elif len(dim) == 2:
            sysdim = "planar"
        elif len(dim) in range(3,10):
            sysdim = "mid"
        elif len(dim) >= 10:
            sysdim = "high"

    elif system == "simplearm":
        if len(dim) <= 3:
            sysdim = "low"
        elif len(dim) > 3 and len(dim) <= 7:
            sysdim = "mid"
        elif len(dim) > 7 and len(dim) <= 10:
            sysdim = "high"
            
    return sysdim

def make_args_from_(conf):
    """make args Namespace from config variables"""
    from argparse import Namespace
    # print "conf", conf
    args = Namespace()

    if conf["class"].__name__.startswith("PointmassRobot"):
        system = "pointmass"
    elif conf["class"].__name__.startswith("SimpleRandomRobot"):
        system = "pointmass"
    elif conf["class"].__name__.startswith("SimplearmRobot"):
        system = "simplearm"

    sysdim = get_sysdim_string_for_robot(system, conf["dim_s_motor"], conf["control"])
                
    setattr(args, "system", system)
    setattr(args, "sysdim", sysdim)
    setattr(args, "numsteps", conf["numsteps"])
    return args

# class Robot(object):
#     def __init__(self, conf):
#         self.conf = conf
#         # yeah, which dim: DoF sensorimotor, DoF locomotion, sensor dim, motor dim, ...
#         self.dim    = 0
#         self.dimnames = []
#         # self.dimcolumns = []
#         self.smdict       = OrderedDict()
#         self.smdict_index = OrderedDict()
#         # let's call these "dimension groups"
#         self.smstruct = ["dim_s_proprio", "dim_s_extero", "dim_s_intero", "dim_s_reward", "dim_s_pred", "dim_s_motor"]
#         self.smattrs  = ["dim", "dimnames", "smdict", "smstruct", "sm", "smattrs"]

#         # default copy conf items into member vars
#         set_attr_from_dict(self, conf) # check that this is OK
                
#         # sensorimotor space representation
#         for k in self.smstruct:
#             # smdict key
#             k_ = k.replace("dim_", "")
            
#             # dim of that part is length of fields array
#             dim_ = len(conf[k])
            
#             # set the class attribute
#             setattr(self, k, dim_)
            
#             # count overall dims
#             self.dim += dim_

#             # collect all variable names
#             self.smdict_index[k_] = {}
#             for i, dimname in enumerate(conf[k]):
#                 # this is local index for given dim group
#                 self.smdict_index[k_][dimname] = i
#                 # this is globally associated with self.sm
#                 self.dimnames.append(dimname)
                
#             self.smdict[k_] = np.zeros((dim_, 1))
#             # self.dimcolumns.append(conf[k])
#         self.smdict_concat = [None for i in range(self.dim)] # don't need this
#         self.sm = np.zeros((self.dim, 1)) # full sensorimotor vector, use dict?

#         # debug
#         # print "%s.__init__ full sm dim = %d, names = %s, %s" % (self.__class__.__name__, self.dim, self.dimnames, self.smdict)
#         print "%s.__init__ full\n       #dims = %d\n    dimnames = %s\nsmdict_index = %s\n" % \
#           (self.__class__.__name__, self.dim, self.dimnames, self.smdict_index)
                    
#         ################################################################################
#         # brain only one
        
#         # brain prepare config by copying robot attributes to brain config
#         for attr in self.smattrs:
#             # print attr, getattr(self, attr)
#             self.conf["brains"][0][attr] = getattr(self, attr)
            
#         # brain instantiate
#         self.brains = get_items(self.conf["brains"])
        
#         # brain shouldn't we just pass a robot self reference down into the brain?
#         for brain in self.brains:
#             brain.robot = self
            
#         assert(len(self.brains) == 1) # not ready for that yet

#         if self.conf["type"] == "explauto":
#             # print "expl"
#             args = make_args_from_(self.conf)
#             self.env = get_context_environment(args)
#             # print "dir(self.env)", dir(self.env)
#             # print "env_cls", env_cls
#             # print "env_conf", env_conf
#             # reset environment
#             self.env.reset()
#             # print "self.env", self.env
        
#         # communication / logging
#         # ROS
#         if self.conf["ros"] is True:
#             import rospy
#             # rospy.init_node("%s" % self.conf["name"])

#     def get_sm_index(self, dimgroup, base):
#         # FIXME: make the goal dim configurable etc on this level
#         return [self.smdict_index[dimgroup]["%s%d" % (base, k)] for k in range(self.dim_s_motor)]
    
#     def step(self, x):
#         """execute one time-step of the robot brain with
#         new sensor data as input and producing a prediction"""
#         pass

#     def update(self, prediction):
#         """execute one time-step of the world with robot proprio predictions as input
#         and producing new world and sensory state"""
#         pass
    
# class SimpleRandomRobot(Robot):
#     def __init__(self, conf):
#         self.conf = conf
#         print "%s.__init__ self.conf = %s" % (self.__class__.__name__, self.conf)
#         # print "PointmassRobot.conf", conf
#         # make args from conf needing numsteps, system, sysdim
#         Robot.__init__(self, self.conf)
#         # ROS
#         if self.conf["ros"] is True:
#             import rospy
#             # rospy.init_node("%s" % self.conf["name"])
#         self.x = np.zeros((self.dim_s_proprio, 1))
#         self.y = np.zeros((self.dim_s_motor, 1))
        
#         if self.conf["type"] == "explauto":
#             # print "expl"
#             args = make_args_from_(self.conf)
#             self.env = get_context_environment(args)
#             # print "env_cls", env_cls
#             # print "env_conf", env_conf
#             # reset environment
#             self.env.reset()
#             print "%s.__init__ self.env = %s" %(self.__class__.__name__,  self.env)
        
#     def step(self, x):
#         """step the robot: input is vector of new information $x$ from the world"""
#         print "%s.step x = %s" % (self.__class__.__name__, x)
#         if x is None: # catch initial state
#             self.x = np.random.uniform(-1.0, 1.0, (self.dim_s_proprio, 1))
#         # print "x", x
#         # 1. s = get sensors
#         s = x.copy()
#         # 2. m = ask brain(s)
#         m = s + (np.random.binomial(3, 0.05) * 0.01 * (np.random.binomial(1, 0.5) * 2 -1))
#         # 3. w = ask_world(m)
#         # return self.x.reshape(self.mdim,)
#         self.y = m.reshape(self.dim_s_motor,)
#         return self.y
    
# class PointmassRobot(Robot):
#     def __init__(self, conf):
#         self.conf = conf
#         # print "PointmassRobot.conf", self.conf
#         # print "PointmassRobot.conf", conf
#         # make args from conf needing numsteps, system, sysdim
#         Robot.__init__(self, self.conf)
        
#         # robot i/o data, FIXME: pack it all into dictionary
#         # self.x = np.zeros((self.sdim, 1))
#         # self.y = np.zeros((self.mdim, 1))
        
#         if self.conf["type"] == "explauto":
#             # print "expl"
#             args = make_args_from_(self.conf)
#             self.env = get_context_environment(args)
#             # print "dir(self.env)", dir(self.env)
#             # print "env_cls", env_cls
#             # print "env_conf", env_conf
#             # reset environment
#             self.env.reset()
#             # print "self.env", self.env

#     def get_logdata_columns(self):
#         """collect all internal variables and their names and return ordered
#         list of names corresponding to order in sm vector"""
#         return self.dimnames
        
#     def get_logdata(self):
#         """collect all internal variables, stack them into one vector and
#         return that"""
#         # logdata = np.atleast_2d(np.hstack((self.x, self.y))).T
#         # acc, vel, pos, dist_goal, acc_pred, acc_motor

#         # for k in self.smdict.keys():
#         #     print "self.smdict[%s]" % (k), self.smdict[k].shape
        
#         logdata = np.atleast_2d(np.vstack([self.smdict[k] for k in self.smdict.keys()]))
#         print "%s.get_logdata, logdata.shape = %s, self.dim = %d" % (self.__class__.__name__, logdata.shape, self.dim)
#         # logdata = np.atleast_2d(np.hstack((self.x, self.y))).T
#         return logdata
            
#     def step(self, x):
#         """step the robot:
#         input is vector of new information $x$ from the world

#         essentially: step the robot brain
#         """
#         # debug
#         print "%s.step x = %s" % (self.__class__.__name__, x.shape)
        
#         # 1. get sensors
#         if x is None: # catch initial state
#             # self.x = np.random.uniform(-1.0, 1.0, (self.sdim, 1))
#             self.smdict["s_proprio"] = np.random.uniform(-1.0, 1.0, (self.dim_s_proprio, 1))
#             self.smdict["s_extero"]  = np.random.uniform(-1.0, 1.0, (self.dim_s_extero,  1))
#         else:
#             self.smdict["s_proprio"] = x[self.dim_s_extero:].copy() # HACK?
#             self.smdict["s_extero"]  = x[:self.dim_s_extero].copy() # HACK?
            
#         # print "s_pred 1", self.smdict["s_pred"]
#         # 2. m = ask brain to fill in things, no brain yet but hey
#         for brain in self.brains:
#             # print "brain",i
#             self.smdict = brain.step(self.smdict)
#             # print "s_pred 2", self.smdict["s_pred"]
#             prediction = brain.predict_proprio()
#             print "%s.step prediction.shape = %s" %(self.__class__.__name__,  prediction.shape)
#             # a_ = np.random.uniform(-0.1, 0.1, (1, self.dim_s_motor))
        
#         # print "s_pred 3", self.smdict["s_pred"]
        
#         # m_ retains input shape?
#         # m_ = self.env.compute_motor_command(np.squeeze(prediction, axis=0)).T # transpose to comply with smdict
#         # print "m_.shape", m_.shape
        
#         m_ = self.env.compute_motor_command(prediction).T # transpose to comply with smdict
#         print "m_.shape", m_.shape
#         # print "m_", m_.shape, m_, "s_pred", self.smdict["s_pred"]
#         self.smdict["s_pred"] = m_
#         self.smdict["s_motor"] = m_.reshape((self.dim_s_motor, 1))
#         # print "%s.step m = %s" % (self.__class__.__name__, self.smdict["s_motor"])
#         # m = s + (np.random.binomial(3, 0.05) * 0.01 * (np.random.binomial(1, 0.5) * 2 -1))
#         # 3. w = ask_world(m)
#         # return self.x.reshape(self.mdim,)
#         # self.y = self.smdict["s_motor"].reshape(self.dim_s_motor,)
#         # print "dimcomaprison smdict[\"s_motor\"] vs. y", self.smdict["s_motor"].shape, self.y.shape
#         # return brain answer
#         return np.squeeze(self.smdict["s_motor"], axis=1)

#     def update(self, prediction):
#         """let the body and forces induced by the robot's predictions interact with the world and yield effect"""
#         x_ = np.atleast_2d(self.env.compute_sensori_effect(prediction)).T
#         # self.x = self.env.update(prediction)
#         # x_ = self.env.update(prediction, reset=False)
#         print "update: x_", x_.shape
#         return x_


# ################################################################################
# # simple arm / explauto
# class SimplearmRobot(Robot):
#     def __init__(self, conf):
#         self.conf = conf
#         Robot.__init__(self, self.conf)

#     def get_logdata(self):
#         logdata = np.atleast_2d(np.vstack([self.smdict[k] for k in self.smdict.keys()]))
#         print "%s.get_logdata, logdata.shape = %s, self.dim = %d" % (self.__class__.__name__, logdata.shape, self.dim)
#         # logdata = np.atleast_2d(np.hstack((self.x, self.y))).T
#         return logdata
        
#     def step(self, x):
#         """step the robot:
#         input is vector of new information $x$ from the world

#         essentially: step the robot brain
#         """
#         # debug
#         print "%s.step x.shape = %s" % (self.__class__.__name__, x.shape)
        
#         # 1. get sensors
#         if x is None: # catch initial state
#             # self.x = np.random.uniform(-1.0, 1.0, (self.sdim, 1))
#             self.smdict["s_proprio"] = np.random.uniform(-1.0, 1.0, (self.dim_s_proprio, 1))
#             self.smdict["s_extero"]  = np.random.uniform(-1.0, 1.0, (self.dim_s_extero,  1))
#         else:
#             self.smdict["s_proprio"] = x[self.dim_s_extero:].copy() # HACK?
#             self.smdict["s_extero"]  = x[:self.dim_s_extero].copy() # HACK?
            
#         # print "s_pred 1", self.smdict["s_pred"]
#         # 2. m = ask brain to fill in things, no brain yet but hey
#         for brain in self.brains:
#             # print "brain",i
#             self.smdict = brain.step(self.smdict)
#             # print "s_pred 2", self.smdict["s_pred"]
#             prediction = brain.predict_proprio()
#             print "%s.step prediction.shape = %s, %s" %(self.__class__.__name__,  prediction.shape, prediction)
#             # a_ = np.random.uniform(-0.1, 0.1, (1, self.dim_s_motor))
            
#         m_ = self.env.env.compute_motor_command(prediction.reshape(self.dim_s_motor,)).reshape((self.dim_s_motor, 1)) # transpose to comply with smdict
#         print "m_.shape", m_.shape, m_.T == prediction
#         # print "m_", m_.shape, m_, "s_pred", self.smdict["s_pred"]
#         self.smdict["s_proprio"] = m_
#         self.smdict["s_pred"] = m_
#         self.smdict["s_motor"] = m_.reshape((self.dim_s_motor, 1))
        
#         return np.squeeze(self.smdict["s_motor"], axis=1)

#     def update(self, prediction):
#         dim_sum = self.dim_s_extero + self.dim_s_proprio
#         # for simple_arm, this computes only exteroceptive sensory feedback
#         x_extero = np.atleast_2d(self.env.compute_sensori_effect(prediction)).T
#         # so we have to squeeze in the proprio stuff
#         x_ = np.zeros((dim_sum * 2, 1))
#         x_[:self.dim_s_extero] = x_extero[:self.dim_s_extero]
#         x_[self.dim_s_extero:self.dim_s_extero+self.dim_s_proprio] = self.smdict["s_proprio"]
#         x_[dim_sum:dim_sum+self.dim_s_extero] = x_extero[self.dim_s_extero:]
#         x_[dim_sum+self.dim_s_extero:] = self.smdict["s_proprio"]
#         # self.x = self.env.update(prediction)
#         # x_ = self.env.update(prediction, reset=False)
#         print "%s.update: x_.shape = %s, wanted = %s, x_ = %s" % (self.__class__.__name__, x_.shape, ((dim_sum) * 2, 1), x_)
#         assert(x_.shape == ((self.dim_s_extero + self.dim_s_proprio) * 2, 1))
#         return x_

################################################################################
# v2 style
class Robot2(object):
    def __init__(self, conf, ifs_conf):
        self.conf = conf
        set_attr_from_dict(self, conf) # check that this is OK

        set_attr_from_dict_ifs(self, ifs_conf)
        
        # ROS
        if self.ros:
            # rospy.init_node(self.name)
            self.subs = {}
            self.pubs = {}
            
    def get_sm_index(self, dimgroup, base, numk = None):
        if numk is None:
            numk = self.dim_s_motor
        # FIXME: make the goal dim configurable etc on this level
        return [self.smdict_index[dimgroup]["%s%d" % (base, k)] for k in range(numk)]

    def get_sm_index_single(self, dimgroup, base, numk):
        if numk is None:
            numk = 0
        # FIXME: make the goal dim configurable etc on this level
        return [self.smdict_index[dimgroup]["%s%d" % (base, k)] for k in [numk]]
    
    def get_logdata(self):
        """collect all internal variables, stack them into one vector and
        return that"""
        logdata = np.atleast_2d(np.vstack([self.smdict[k] for k in self.smdict.keys()]))
        print "%s.get_logdata, logdata.shape = %s, self.dim = %d" % (self.__class__.__name__, logdata.shape, self.dim)
        # logdata = np.atleast_2d(np.hstack((self.x, self.y))).T
        return logdata
    
    def step(self, world, x):
        """update the robot body respecting effects of the world"""
        print "%s.step world = %s, x = %s" % (self.__class__.__name__, world, x)
        return {"s_proprio": np.zeros((self.dim_s_proprio, 1)), "s_extero": np.zeros((self.dim_s_extero, 1))}

class NullRobot2(Robot2):
    def __init__(self, conf, ifs_conf):
        Robot2.__init__(self, conf, ifs_conf)
    
class PointmassRobot2(Robot2):
    """point mass model: this seems to be the same as in
explauto/environments/pointmass.py
"""
    def __init__(self, conf, ifs_conf):
        Robot2.__init__(self, conf, ifs_conf)

        # state is (pos, vel, acc).T
        # self.state_dim
        self.x0 = np.zeros((self.statedim, 1))
        self.x  = self.x0.copy()
        self.cnt = 0

    def reset(self):
        self.x = self.x0.copy()
        
    def step(self, world, x):
        """update the robot, pointmass"""
        print "%s.step world = %s, x = %s" % (self.__class__.__name__, world, x)
        self.apply_force(x)
        return {"s_proprio": self.compute_sensors_proprio(),
                "s_extero": self.compute_sensors_extero()}
        
    def bound_motor(self, m):
        return np.clip(m, self.force_min, self.force_max)

    def apply_force(self, u):
        """control pointmass with force command (2nd order)"""
        # print "u", u
        # FIXME: insert motor transfer function
        a = (u/self.mass).reshape((self.dim_s_motor, 1))
        # a += np.random.normal(0.05, 0.01, a.shape)

        # # world modification
        # if np.any(self.x[:self.dim_s_motor] > 0):
        #     a += np.random.normal(0.05, 0.01, a.shape)
        # else:
        #     a += np.random.normal(-0.1, 0.01, a.shape)
            
        # print("a.shape", a.shape)
        # print "a", a, self.x[self.conf.s_ndims/2:]
        v = self.x[self.dim_s_motor:self.dim_s_motor*2] * (1 - self.friction) + a * self.dt
        
        # self.a_ = a.copy()
        
        
        # # world modification
        # v += np.sin(self.cnt * 0.01) * 0.05
        
        # print "v", v
        p = self.x[:self.dim_s_motor] + v * self.dt

        # collect temporary state description into joint state vector
        self.x[:self.dim_s_motor] = p.copy()
        self.x[self.dim_s_motor:self.dim_s_motor*2] = v.copy()
        self.x[self.dim_s_motor*2:] = a.copy()

        # apply noise
        self.x += self.sysnoise * np.random.randn(self.x.shape[0], self.x.shape[1])

        # print "self.x[2,0]", self.x[2,0]

        # self.scale()
        # self.pub()                
        self.cnt += 1
        
        # return x
        # self.x = x # pointmasslib.simulate(self.x, [u], self.dt)

    def compute_sensors_proprio(self):
        return self.x[self.dim_s_motor*2:]
    
    def compute_sensors_extero(self):
        return self.x[self.dim_s_motor:self.dim_s_motor*2]
    
    def compute_sensors(self):
        """compute the proprio and extero sensor values from state"""
        return 

    
    
def forward(angles, lengths):
    """ Link object as defined by the standard DH representation.

    :param list angles: angles of each joint

    :param list lengths: length of each segment

    :returns: a tuple (x, y) of the end-effector position

    .. warning:: angles and lengths should be the same size.
    """
    x, y = joint_positions(angles, lengths)
    return x[-1], y[-1]

def joint_positions(angles, lengths, unit='rad'):
    """ Link object as defined by the standard DH representation.

    :param list angles: angles of each joint

    :param list lengths: length of each segment

    :returns: x positions of each joint, y positions of each joints, except the first one wich is fixed at (0, 0)

    .. warning:: angles and lengths should be the same size.
    """
    if len(angles) != len(lengths):
        raise ValueError('angles and lengths must be the same size!')

    if unit == 'rad':
        a = np.array(angles)
    elif unit == 'std':
        a = np.pi * np.array(angles)
    else:
        raise NotImplementedError
     
    a = np.cumsum(a)
    return np.cumsum(np.cos(a)*lengths), np.cumsum(np.sin(a)*lengths)
    
class SimpleArmRobot(Robot2):
    def __init__(self, conf, ifs_conf):
        Robot2.__init__(self, conf, ifs_conf)
        
        # self.length_ratio = length_ratio
        # self.noise = noise

        self.factor = 1.0

        self.lengths = self.compute_lengths(self.dim_s_motor, self.length_ratio)

        self.m = np.zeros((self.dim_s_motor, 1))

    def compute_lengths(self, n_dofs, ratio):
        l = np.ones(n_dofs)
        for i in range(1, n_dofs):
            l[i] = l[i-1] / ratio
        return l / sum(l)

    def compute_motor_command(self, m):
        m *= self.factor
        return np.clip(m, self.m_mins, self.m_maxs)

    def step(self, world, x):
        """update the robot, pointmass"""
        print "%s.step world = %s, x = %s" % (self.__class__.__name__, world, x)
        # print "x", x.shape
        self.m = self.compute_motor_command(self.m + x)# .reshape((self.dim_s_motor, 1))
        
        # print "m", m
        # self.apply_force(x)
        return {"s_proprio": self.m, # self.compute_sensors_proprio(),
                "s_extero": self.compute_sensors_extero()}

    def compute_sensors_extero(self):
        hand_pos = np.array(forward(self.m, self.lengths)).reshape((self.dim_s_extero, 1))
        hand_pos += self.sysnoise * np.random.randn(*hand_pos.shape)
        # print "hand_pos", hand_pos.shape
        return hand_pos
                
class STDRCircularRobot(Robot2):
    def __init__(self, conf, ifs_conf):
        Robot2.__init__(self, conf, ifs_conf)

        if not self.ros:
            import sys
            print "ROS not configured but this robot (%s) requires ROS, exiting" % (self.__class__.__name__)
            sys.exit(1)
        # timing
        self.rate = rospy.Rate(1/self.dt)
            
        # pub / sub
        from nav_msgs.msg      import Odometry
        from geometry_msgs.msg import Twist
        from sensor_msgs.msg   import Range

        # actuator / motors
        self.twist = Twist()
        self.twist.linear.x = 0
        self.twist.linear.y = 0
        self.twist.linear.z = 0
        self.twist.angular.x = 0
        self.twist.angular.y = 0
        self.twist.angular.z = 0

        # odometry
        self.odom = Odometry()
        self.sonars = []
        self.outdict = {"s_proprio": np.zeros((self.dim_s_proprio, 1)),
                "s_extero": np.zeros((self.dim_s_extero, 1))}
                
        self.subs["odom"]    = rospy.Subscriber("/robot0/odom", Odometry, self.cb_odom)
        for i in range(3):
            self.sonars.append(Range())
            self.subs["sonar%d" % i]    = rospy.Subscriber("/robot0/sonar_%d" % i, Range, self.cb_range)
        self.pubs["cmd_vel"] = rospy.Publisher("/robot0/cmd_vel", Twist, queue_size = 2)

        # initialize / reset
        from stdr_msgs.srv import MoveRobot
        from geometry_msgs.msg import Pose2D
        self.srv_replace = rospy.ServiceProxy("robot0/replace", MoveRobot)
        default_pose = Pose2D()
        default_pose.x = 2.0
        default_pose.y = 2.0
        ret = self.srv_replace(default_pose)
        # print "ret", ret

    def step(self, world, x):
        if rospy.is_shutdown(): return
        self.twist.linear.x = x[0,0]  # np.random.uniform(0, 1)
        self.twist.angular.z = x[1,0] * 1.0 # np.random.uniform(-1, 1)
        self.pubs["cmd_vel"].publish(self.twist)
        # time.sleep(self.dt * 0.9)
        self.rate.sleep()

        
        # self.outdict["s_proprio"][0,0] = x[1,0]
        
        # idx = self.get_sm_index("s_extero", "vel_lin", 1)
        # self.outdict["s_extero"][idx] = x[0,0]
        
        # idx = self.get_sm_index("s_extero", "pos", 2)
        # self.outdict["s_extero"][idx] = np.array([[self.odom.pose.pose.position.x], [self.odom.pose.pose.position.y]])
        
        # idx = self.get_sm_index("s_extero", "pos", 2)
        # self.outdict["s_extero"][idx] = np.array([[self.odom.pose.pose.position.x], [self.odom.pose.pose.position.y]])

        self.outdict["s_proprio"] = self.smdict["s_proprio"]
        self.outdict["s_extero"] = self.smdict["s_extero"]
        
        return self.outdict
        
    def cb_odom(self, msg):
        # print "%s.cb_odom" % (self.__class__.__name__), type(msg)
        self.odom = msg
        
        self.smdict["s_proprio"][self.get_sm_index("s_proprio", "vel_ang", 1)] = self.odom.twist.twist.angular.z
        self.smdict["s_extero"][self.get_sm_index("s_extero", "vel_lin", 1)] = self.odom.twist.twist.linear.x
        self.smdict["s_extero"][self.get_sm_index("s_extero", "pos", 2)] = np.array([[self.odom.pose.pose.position.x], [self.odom.pose.pose.position.y]])
        
        euler_angles = np.array(euler_from_quaternion([
            msg.pose.pose.orientation.x,
            msg.pose.pose.orientation.y,
            msg.pose.pose.orientation.z,
            msg.pose.pose.orientation.w
            ]))
        
        self.smdict["s_extero"][self.get_sm_index("s_extero", "theta", 1)] = euler_angles[2]
        
    def cb_range(self, msg):
        # print "%s.cb_range" % (self.__class__.__name__), type(msg)
        # print "id", msg.header.frame_id
        sonar_idx = int(msg.header.frame_id.split("_")[-1])
        # print sonar_idx
        # self.get_sm_index("s_extero", "sonar", 1)
        if np.isinf(msg.range ):
            srange = 0
        else:
            srange = msg.range
        self.smdict["s_extero"][self.get_sm_index_single("s_extero", "sonar", sonar_idx)] = srange
        self.sonars[sonar_idx] = msg
