"""
Default experiment for clean smp

Should be self-contained requiring now external packages or processes.

Robot: Point mass
World: open linear (1D) space
 Task: null task: task performance is always null no matter what
Brain: null brain: just output null
 Loss: 0
"""

import time
from smq.utils  import make_column_names_numbered
from smq.worlds import RobotWorld
from smq.robots import SimpleRandomRobot, PointmassRobot
from smq.plot   import PlotTimeseries
from smq.tasks  import NullTask, SetpointTask
from smq.brains import NullBrain

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
            "dim_s_intero": ["vel_", "pos_"],
            "dim_s_reward": ["dist_goal"],
            "dim_s_pred": ["acc_pred"],
            "dim_s_motor": ["m"] * motors,
            "numsteps": numsteps,
            "control": "force",
            "ros": False,
            "brains": [
                {
                    "class": NullBrain,
                    "name": "nullbrain",
                    "dim_s_motor": motors,
                    # tasks be of length either one or same as len(robots)
                    "tasks": [
                        {
                            "class": NullTask,
                            "name": "nulltask",
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
