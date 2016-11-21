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
from smq.plot   import PlotTimeseries, PlotTimeseries2D, PlotTimeseriesND
from smq.tasks  import NullTask, SetpointTask, GoalTask
from smq.brains import NullBrain, KinesisBrain

# local variables for re-use
numsteps = 1000
motors   = 2
name = "default_kinesis_2d"
expr_id = make_expr_id(name)

# using dict convention seemed to be the best over yaml and friends
conf = {
    # first level corresponds to experiment
    "numsteps": numsteps,
    "id": expr_id,
    # these are arrays of dicts specifying components
    "robots": [
        {
            "class": PointmassRobot, # SimpleRandomRobot,
            "type": "explauto",
            "name": make_robot_name(expr_id, "pm", 0),
            # dimensions of different subparts of sm vector
            # make that more compact / automatically inferred
            # actually: make that lists of names whose length is the dim
            "dim_s_proprio": make_column_names_numbered("acc", motors),
            "dim_s_extero": make_column_names_numbered("vel", motors),
            "dim_s_intero": make_column_names_numbered("vel_", motors) + make_column_names_numbered("pos_", motors) + make_column_names_numbered("vel_goal", motors),
            "dim_s_reward": make_column_names_numbered("dist_goal", 1),
            "dim_s_pred": make_column_names_numbered("acc_pred", motors),
            "dim_s_motor": make_column_names_numbered("m", motors),
            "numsteps": numsteps,
            "control": "force",
            "ros": False,
            "brains": [
                {
                    "class": KinesisBrain,
                    "name": "kinesisbrain",
                    "dim_s_motor": motors,
                    "variant": "continuous_linear", # "binary_threshold"
                    # tasks be of length either one or same as len(robots)
                    "tasks": [
                        {
                            "class": GoalTask,
                            "name": "goaltask",
                            "goalspace": "s_extero",
                            "intero_index": 4,
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
            "class": PlotTimeseries2D,
            "name": "plottimeseries2d",
            "type": "seaborn", # "pyplot",
            "method": "run"
        },
        {
            "class": PlotTimeseriesND,
            "name": "plottimeseriesnd",
            "type": "seaborn", # "pyplot",
            "method": "run"
        },
    ],
    }
