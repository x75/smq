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
from smq.worlds import RobotWorld2
from smq.robots import SimpleRandomRobot, PointmassRobot, PointmassRobot2
from smq.plot   import PlotTimeseries2, PlotTimeseriesND
from smq.tasks  import NullTask, SetpointTask, GoalTask, GoalTask2
from smq.brains import NullBrain, KinesisBrain, KinesisBrain2

# local variables for re-use
numsteps = 1000
dt = 0.1
motors   = 3
name = "kinesis_pm_%dd" % (motors)
expr_id = make_expr_id(name)

# using dict convention seemed to be the best over yaml and friends
conf = {
    # first level corresponds to experiment
    "numsteps": numsteps,
    "id": "%s_%s" % (name, time.strftime("%Y%m%d_%H%M%S")),
    # these are arrays of dicts specifying components
    # robots, brains, interfaces need to match / correspond
    "ifs": [
        {
            # dimensions of different subparts of sm vector
            # make that more compact / automatically inferred
            # actually: make that lists of names whose length is the dim
            # from world
            "dim_s_proprio": make_column_names_numbered("acc", motors),
            "dim_s_extero": make_column_names_numbered("vel", motors),
            # internal
            "dim_s_intero": make_column_names_numbered("vel_", motors) + \
        make_column_names_numbered("pos_", motors) + \
        make_column_names_numbered("vel_error", motors) + \
        make_column_names_numbered("vel_goal", motors), #+ \
#        make_column_names_numbered("thresh", motors),
            "dim_s_reward": make_column_names_numbered("dist_goal", 1),
            "dim_s_pred": make_column_names_numbered("acc_pred", motors),
            # to world
            "dim_s_motor": make_column_names_numbered("m", motors),
        },
    ],
    "robots": [
        {
            "class": PointmassRobot2, # SimpleRandomRobot,
            "type": "explauto",
            "name": make_robot_name(expr_id, "pm", 0),
            "numsteps": numsteps,
            "control": "force",
            "ros": False,
            "statedim": motors * 3,
            "dt": dt,
            "mass": 1.0,
            "force_max":  1.0,
            "force_min": -1.0,
            "friction": 0.01,
            "sysnoise": 1e-3,
        }
    ],
    "brains": [
        {
            "class": KinesisBrain2,
            "name": make_robot_name(expr_id, "kinesisbrain", 0),
            "dim_s_motor": motors,
            "variant": "binary_threshold", # "continuous_linear"
            "continuous_gain": 1.5,
            "binary_threshold": 0.05,
            "binary_high_range": 1.0,
            "binary_low_range": 0.01,
            # tasks be of length either one or same as len(robots)
            "tasks": [
                {
                    "class": GoalTask2,  # class
                    "name": "goaltask2", # name
                    "goal_dims_dict":   {"s_extero": make_column_names_numbered("vel", motors)}, # map goal components to items in sm interface
                    "intero_goal_idx":  make_column_names_numbered("vel_goal", motors),   # map goal components to items in s_intero
                    "intero_error_idx": make_column_names_numbered("vel_error", motors),  # map goal components to items in s_intero
                    # "loss": "mse",
                }
            ],
        },
    ],
    "worlds": [
        {
            "class": RobotWorld2,
            "dt": dt,
            "map": "open_planar_isotropic",
            "dim": 0,
            "numsteps": numsteps,
        }
    ],
    "loss": "mse",
    "analyses": [
        {
            "class": PlotTimeseriesND,
            "name": "plottimeseries",
            "title": "%s" % (expr_id),
            "type": "seaborn", # "pyplot",
            "plotitems": ["brains"],
        },
    ],
}
