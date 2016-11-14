"""
Default experiment for clean smp

Should be self-contained requiring now external packages or processes.

Robot: Point mass
World: open planar (2D) space
 Task: go to a goal position and stay there
Brain: kinesis 
 Loss: mean squared error
"""

from smq.worlds import RobotWorld
from smq.robots import PointmassRobot

# local variables for re-use
numsteps = 1000

# using dict convention seemed to be the best over yaml and friends
conf = {
    # first level corresponds to experiment
    "numsteps": numsteps,
    # these are arrays of dicts specifying components
    "robots": [
        {"class": PointmassRobot,
         "type": "explauto",
         "name": "pm",
         "sdim": 1, # sensor dim
         "mdim": 1, # motor  dim
         "numsteps": numsteps,
         "control": "kinematic",
         "ros": False,
        }
    ],
    "worlds": [
        {"class": RobotWorld,
         "dt": 0.1,
         "map": "open_planar_isotropic",
         "dim": 0,
        }
    ],
    "task": "setpoint",
    "brain": "kinesis",
    "loss": "mse",
    "analyses": [
        "plot_timeseries",
        ],
    }
