"""
Default experiment for clean smp

Should be self-contained requiring now external packages or processes.

Robot: Point mass
World: open linear (1D) space
 Task: go to a goal position and stay there
Brain: kinesis 
 Loss: mean squared error / goal distance
"""

import time
from smq.utils  import make_column_names_numbered, make_expr_id, make_robot_name
from smq.worlds import RobotWorld
from smq.robots import SimpleRandomRobot, PointmassRobot
from smq.plot   import PlotTimeseries
from smq.tasks  import NullTask, SetpointTask, GoalTask
from smq.brains import NullBrain, KinesisBrain

# local variables for re-use
numsteps = 1000
motors   = 1
name = "default_kinesis_1d"
expr_id = make_expr_id(name)

# using dict convention seemed to be the best over yaml and friends
conf = {
    # first level corresponds to experiment
    "numsteps": numsteps,
    "id": "%s-%s" % (name, time.strftime("%Y%m%d-%H%M%S")),
    # these are arrays of dicts specifying components
    "robots": [
        {
            "class": PointmassRobot, # SimpleRandomRobot,
            "type": "explauto",
            "name": make_robot_name(expr_id, "pm_kinematic", 0),
            # dimensions of different subparts of sm vector
            # make that more compact / automatically inferred
            # actually: make that lists of names whose length is the dim
            "dim_s_proprio": ["acc"],
            "dim_s_extero": ["vel"],
            "dim_s_intero": ["vel_", "pos_", "vel_goal"],
            "dim_s_reward": ["dist_goal"],
            "dim_s_pred": ["acc_pred"],
            "dim_s_motor": ["m"] * motors,
            "numsteps": numsteps,
            "control": "vel",
            "ros": False,
            "brains": [
                {
                    "class": KinesisBrain,
                    "name": "kinesisbrain",
                    "dim_s_motor": motors,
                    "variant": "binary_threshold", # "continuous_linear"
                    "continuous_gain": 1.5,
                    "binary_threshold": 0.2,
                    "binary_high_range": 1.0,
                    "binary_low_range": 0.01,
                    # tasks be of length either one or same as len(robots)
                    "tasks": [
                        {
                            "class": GoalTask,
                            "name": "goaltask",
                            "goalspace": "s_extero",
                            "loss": "mse",
                        }
                    ],
                },
            ],
        }
    ],
    "worlds": [
        {"class": RobotWorld,
         "dt": 0.1,
         "map": "open_planar_isotropic",
         "dim": 0,
         "numsteps": numsteps,
        }
    ],
    "loss": "mse",
    "analyses": [
        {
            "class": PlotTimeseries,
            "name": "plottimeseries",
            "type": "seaborn" # "pyplot"
        },
    ],
    }
