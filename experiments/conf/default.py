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
from smq.robots import Pointmass

# using dict convention seemed to be the best over yaml and friends
conf = {
    "robots": [
        {"class": Pointmass,
         "dim": 1,
         "control": "kinematic"
        }
    ],
    "worlds": [
        {"class": RobotWorld,
         "dt": 0.1,
         "map": "open_planar_isotropic"
        }
    ],
    "task": "setpoint",
    "brain": "kinesis",
    "loss": "mse"
    }
