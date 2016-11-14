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
    "robots": [
        {"class": PointmassRobot,
         "type": "explauto",
         "dim": 1,
         "numsteps": numsteps,
         "control": "kinematic"
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
    "loss": "mse"
    }
