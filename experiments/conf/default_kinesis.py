"""
Default experiment for clean smp

Should be self-contained requiring now external packages or processes.

Robot: Point mass
World: open planar (2D) space
 Task: go to a goal position and stay there
Brain: kinesis 
 Loss: mean squared error
"""

import time
from smq.worlds import RobotWorld
from smq.robots import SimpleRandomRobot, PointmassRobot
from smq.plot   import PlotTimeseries
from smq.tasks  import NullTask, SetpointTask, GoalTask
from smq.brains import NullBrain, KinesisBrain

# local variables for re-use
numsteps = 1000
motors   = 1

# using dict convention seemed to be the best over yaml and friends
conf = {
    # first level corresponds to experiment
    "numsteps": numsteps,
    "id": "default-%s" % (time.strftime("%Y%m%d-%H%M%S")),
    # these are arrays of dicts specifying components
    "robots": [
        {
            "class": PointmassRobot, # SimpleRandomRobot,
            "type": "explauto",
            "name": "pm",
            # dimensions of different subparts of sm vector
            # make that more compact / automatically inferred
            # actually: make that lists of names whose length is the dim
            "dim_s_proprio": ["acc"],
            "dim_s_extero": ["vel"],
            "dim_s_intero": ["vel_", "pos_", "vel_goal"],
            "dim_s_reward": ["dist_goal"],
            "dim_s_pred": ["\hat acc"],
            "dim_s_motor": ["m"] * motors,
            "numsteps": numsteps,
            "control": "force",
            "ros": False,
            "brains": [
                {
                    "class": KinesisBrain,
                    "name": "kinesisbrain",
                    "dim_s_motor": motors,
                    # tasks be of length either one or same as len(robots)
                    "tasks": [
                        {
                            "class": GoalTask,
                            "name": "goaltask",
                            "goalspace": "extero",
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
        }
    ],
    "loss": "mse",
    "analyses": [
        {
            "class": PlotTimeseries,
            "name": "plottimeseries",
        },
    ],
    }
