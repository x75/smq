"""smq Motivation modules

in explauto framework  these are called interest models

these modules essentially implement exploration strategies which depend on
 - the past states
 - the current state
 - the state of the model
 """

import numpy as np

from smq.utils import set_attr_from_dict, set_attr_from_dict_ifs

# Motivation base class
# uniform state-agnostic, gaussian, pareto, 1/f, interest modulated
class Motivation2(object):
    def __init__(self, conf, ifs_conf):
        self.conf = conf
        set_attr_from_dict(self, self.conf)

        set_attr_from_dict_ifs(self, ifs_conf)
        # tentative list of attributes
        # - goal (current goal)
        # - certainty / confidence

        # self.goal = np.zeros((self.goal_dims_num, 1))
        self.goal = np.zeros((self.dim_s_motor, 1))
        # print "%s.__init__: dir(self) = %s" % (self.__class__.__name__,  dir(self))
        
        
    def sample(self):
        """sample from the motivation: yield an exploratory move"""
        return self.goal

    def fit(self, x):
        """fit the motivation module to a data item"""
        return

default_conf_motivations = [
    {
        "class": Motivation2
    }
]
