"""
Default experiment for clean smp

Should be self-contained requiring now external packages or processes.

Robot: Point mass
World: open linear (1D) space
 Task: go to a goal position and stay there
Brain: kinesis 
 Loss: mean squared error / goal distance
"""

import time, math
from smq.utils  import make_column_names_numbered, make_expr_id, make_robot_name
from smq.worlds import RobotWorld
from smq.robots import SimpleRandomRobot, PointmassRobot, SimplearmRobot
from smq.plot   import PlotTimeseries, PlotTimeseries2D, PlotTimeseriesND, PlotExplautoSimplearm
from smq.tasks  import NullTask, SetpointTask, GoalTask
from smq.brains import NullBrain, KinesisBrain

# local variables for re-use
numsteps = 1000
motors   = 3
name = "kinesis_3dof_simplearm"
expr_id = make_expr_id(name)

# using dict convention seemed to be the best over yaml and friends
conf = {
    # first level corresponds to experiment
    "numsteps": numsteps,
    "id": expr_id,
    # these are arrays of dicts specifying components
    "robots": [
        {
            "class": SimplearmRobot,
            "type": "explauto",
            "name": make_robot_name(expr_id, "sa", 0),
            # dimensions of different subparts of sm vector
            # make that more compact / automatically inferred
            # actually: make that lists of names whose length is the dim
            "dim_s_proprio": make_column_names_numbered("j_ang", motors),
            "dim_s_extero": make_column_names_numbered("ee_pos", 2),
            "dim_s_intero": make_column_names_numbered("j_ang_", motors) + make_column_names_numbered("ee_pos_", 2) + make_column_names_numbered("j_ang_goal", motors),
            "dim_s_reward": make_column_names_numbered("dist_goal", 1),
            "dim_s_pred": make_column_names_numbered("j_ang_pred", motors),
            "dim_s_motor": make_column_names_numbered("m", motors),
            "numsteps": numsteps,
            "control": "joint_angle", # 0th order
            "ros": False,
            "brains": [
                {
                    "class": KinesisBrain,
                    "name": "kinesisbrain",
                    "dim_s_motor": motors,
                    "variant": "binary_threshold", # "continuous_linear"
                    "binary_high_range": math.pi/3.0 * 0.01,
                    "binary_low_range": 0.001,
                    "binary_threshold": 0.1,
                    "continuous_gain": 0.5,
                    # tasks be of length either one or same as len(robots)
                    "tasks": [
                        {
                            "class": GoalTask,
                            "name": "goaltask",
                            "goalspace": "s_proprio",
                            "intero_index": 5, # FIXME: hm ..
                            "goaldim": motors,
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
            "class": PlotExplautoSimplearm,
            "name": "plotexplautosimplearm",
            "type": "pyplot",
            "method": "run",
        },
        {
            "class": PlotTimeseriesND,
            "name": "plottimeseries3d",
            "type": "seaborn", # "pyplot",
            "method": "run",
            "cols": ["j_ang%d" % i for i in range(motors)] + ["j_ang_pred%d" % i for i in range(motors)],
            "cols_goal_base": "j_ang_goal",
            "cols_goal": ["j_ang_goal%d" % i for i in range(motors)]
        },
    ],
    }
