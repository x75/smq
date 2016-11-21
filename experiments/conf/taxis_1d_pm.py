"""
Default experiment for clean smp

Should be self-contained requiring now external packages or processes.

Robot: Point mass
World: open linear (1D) space
 Task: go to a goal position and stay there
Brain: taxis 
 Loss: mean squared error / goal distance
"""

import time
from smq.utils  import make_column_names_numbered, make_expr_id, make_robot_name
from smq.worlds import RobotWorld
from smq.robots import SimpleRandomRobot, PointmassRobot
from smq.plot   import PlotTimeseries
from smq.tasks  import NullTask, SetpointTask, GoalTask, GoalTaskTaxis
from smq.brains import NullBrain, TaxisBrain

# local variables for re-use
numsteps = 1000
motors   = 1
name = "taxis_1d"
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
            "name": make_robot_name(expr_id, "pm", 0),
            # dimensions of different subparts of sm vector
            # make that more compact / automatically inferred
            # actually: make that lists of names whose length is the dim
            "dim_s_proprio": make_column_names_numbered("acc", motors),
            "dim_s_extero": make_column_names_numbered("vel", motors),
            "dim_s_intero": make_column_names_numbered("vel_", motors) + make_column_names_numbered("pos_", motors) + make_column_names_numbered("vel_goal", motors) + make_column_names_numbered("vel_error", motors),
            "dim_s_reward": make_column_names_numbered("dist_goal", 1),
            "dim_s_pred": make_column_names_numbered("acc_pred", motors),
            "dim_s_motor": make_column_names_numbered("m", motors),
            # above is not enough, need either full dict / access variable by column name
            #                   OR dict mapping variable name to numerical index (HACK?)
            
            "numsteps": numsteps,
            "control": "force",
            "ros": False,
            "brains": [
                {
                    "class": TaxisBrain,
                    "name": "taxisbrain",
                    "dim_s_motor": motors,
                    "variant": "binary_threshold", # "continuous_linear"
                    "continuous_gain": 1.5,
                    "binary_threshold": 0.2,
                    "binary_high_range": 1.0,
                    "binary_low_range": 0.01,
                    # tasks be of length either one or same as len(robots)
                    "tasks": [
                        {
                            "class": GoalTaskTaxis,
                            "name": "goaltasktaxis",
                            "goalspace": "s_extero",
                            "goaldim": motors,
                            "goalinteroindex": 2,
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
