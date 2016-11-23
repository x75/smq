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
from smq.robots import SimpleRandomRobot, PointmassRobot, PointmassRobot2, STDRCircularRobot
from smq.plot   import PlotTimeseries2, PlotTimeseries2D, PlotTimeseriesND
from smq.tasks  import NullTask, SetpointTask, GoalTask, GoalTask2, GoalTaskTaxis2
from smq.brains import NullBrain, KinesisBrain, KinesisBrain2, TaxisBrain2

# local variables for re-use
numsteps = 1000
dt = 0.1
motors   = 2
name = "kinesis_stdr_%dd" % (motors)
expr_id = make_expr_id(name)
ros = True

# using dict convention seemed to be the best over yaml and friends
conf = {
    # first level corresponds to experiment
    "numsteps": numsteps,
    "id": "%s_%s" % (name, time.strftime("%Y%m%d_%H%M%S")),
    "ros": ros,
    # these are arrays of dicts specifying components
    # robots, brains, interfaces need to match / correspond
    "ifs": [
        {
            # dimensions of different subparts of sm vector
            # make that more compact / automatically inferred
            # actually: make that lists of names whose length is the dim
            # from world
            "dim_s_proprio": make_column_names_numbered("vel_ang", 1),
            "dim_s_extero": make_column_names_numbered("vel_lin", 1) + make_column_names_numbered("pos", 2) + make_column_names_numbered("theta", 1) + make_column_names_numbered("sonar", 3),
            # internal
            "dim_s_intero": make_column_names_numbered("vel_ang_", 1) + \
        make_column_names_numbered("pos_error", 2) + \
        make_column_names_numbered("pos_goal", 2) + \
        make_column_names_numbered("sonar_error", 3) + \
        make_column_names_numbered("sonar_goal", 3), #+ \
#        make_column_names_numbered("thresh", motors),
            "dim_s_reward": make_column_names_numbered("dist_goal", 1),
            "dim_s_pred": make_column_names_numbered("twist_pred", motors),
            # to world
            "dim_s_motor": make_column_names_numbered("m", motors),
        },
    ],
    "robots": [
        {
            "class": STDRCircularRobot,
            "type": "explauto",
            "name": make_robot_name(expr_id, "stdr", 0),
            "numsteps": numsteps,
            "control": "Twist",
            "ros": True,
            "robot_config": "simulators/stdr/simple_robot.yaml",
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
            # "class": TaxisBrain2,
            "class": KinesisBrain2,
            "name": make_robot_name(expr_id, "kinesisbrain", 0),
            "dim_s_motor": motors,
            "variant": "binary_threshold", # "continuous_linear"
            "continuous_gain": 5.0,
            "binary_threshold": 0.5, #0.3,
            "binary_high_range": 3.0,
            "binary_low_range": 0.1,
            # tasks be of length either one or same as len(robots)
            "tasks": [
                {
                    # "class": GoalTaskTaxis2, 
                    "class": GoalTask2, 
                    "name": "goaltask2", # name
                    "goaltype": "stdr_pos", # "stdr_sonar"
                    "goal_dims_dict":   {"s_extero": make_column_names_numbered("pos", 2)}, # map goal components to items in sm interface
                    "intero_goal_idx":  make_column_names_numbered("pos_goal", 2),   # map goal components to items in s_intero
                    "intero_error_idx": make_column_names_numbered("pos_error", 2),  # map goal components to items in s_intero
                    # "goal_dims_dict":   {"s_extero": make_column_names_numbered("sonar", 3)}, # map goal components to items in sm interface
                    # "intero_goal_idx":  make_column_names_numbered("sonar_goal", 3),   # map goal components to items in s_intero
                    # "intero_error_idx": make_column_names_numbered("sonar_error", 3),  # map goal components to items in s_intero
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
            "class": PlotTimeseriesND, # PlotTimeseries2D,
            "name": "plottimeseries",
            "title": "%s" % (expr_id),
            "type": "seaborn", # "pyplot",
            "plotitems": ["brains"], # ["robots"],
            "cols": make_column_names_numbered("pos", 2) + make_column_names_numbered("twist_pred", 2) + make_column_names_numbered("sonar", 3),
            "cols_goal_base": "pos_goal"
            # "cols_goal_base": "sonar_goal"
        },
    ],
}
