"""smq Motivation modules

in explauto framework  these are called interest models

these modules essentially implement exploration strategies which depend on
 - the past states
 - the current state
 - the state of the model
 """

import numpy as np

from smq.core  import SMQModule
from smq.utils import set_attr_from_dict, set_attr_from_dict_ifs, ct_car2pol, ct_pol2car

# Motivation base class
# uniform state-agnostic, gaussian, pareto, 1/f, interest modulated
class Motivation(SMQModule):
    def __init__(self, conf):
        SMQModule.__init__(self, conf)
        # tentative list of attributes
        # - goal (current goal)
        # - certainty / confidence

        self.goal = np.zeros((self.goal_dims_num, 1))
        self.suggestion = np.zeros((self.brain.dim_s_motor, 1))
        # print "%s.__init__: dir(self) = %s" % (self.__class__.__name__,  dir(self))

    def step(self, smdict): 
        smdict["s_pred"] = self.suggestion
        return smdict
        
    def sample(self):
        """sample from the motivation: yield an exploratory move"""
        return self.goal

    def fit(self, x):
        """fit the motivation module to a data item"""
        return

class UniformRandomMotivation(Motivation):
    def __init__(self, conf):
        Motivation.__init__(self, conf)

    def step(self, smdict, i):
        gain = self.brain.continuous_gain
        err = smdict["s_reward"][i]
        
        if self.brain.variant == "binary_threshold":
            if err > self.brain.binary_threshold: # FIXME: hardcoded index
                # self.smdict["s_intero"][self.smdict_index["s_intero"]["thresh0"]] = 1
                smdict["s_pred"] = np.random.uniform(-self.brain.binary_high_range, self.brain.binary_high_range, (self.brain.dim_s_motor, 1))
            else:
                # self.smdict["s_intero"][self.smdict_index["s_intero"]["thresh0"]] = 0
                smdict["s_pred"] = np.random.uniform(-self.brain.binary_low_range,  self.brain.binary_low_range,  (self.brain.dim_s_motor, 1))
        else: # default case
            smdict["s_pred"] = np.random.uniform(-(np.sqrt(err)*gain), np.sqrt(err)*gain, (self.brain.dim_s_motor, 1))
            # self.smdict["s_pred"] = np.random.uniform(-(np.power(err, 1/2.0)*gain), np.power(err, 1/2.0)*gain, (1, self.dim_s_motor))
                
        # smdict["s_pred"] = np.random.uniform(-self.brain.binary_high_range, self.brain.binary_high_range, (self.brain.dim_s_motor, 1))
        return smdict


class AngularPursuitMotivation(Motivation):
    def __init__(self, conf):
        Motivation.__init__(self, conf)
        
    def step(self, smdict, i):
        error_cart_level = 0.1
        gain = self.brain.gain

        # cartesian error as computed earlier
        error_cart = smdict["s_intero"][self.intero_error_idx_num]

        # add noise to error
        error_cart += np.random.normal(0, error_cart_level, (self.brain.dim_s_motor, 1))

        # prediction based on cartesian error, accounting for both angular
        # and absolute value error components
        # pred = error_cart * -gain + np.random.normal(0.01, 0.01, error_cart.shape)
        
        # prediction based on directional error only, with a fixed absolute
        # value component

        if self.brain.dim_s_motor > 1:
            # transform cartesian to polar
            error_pol = ct_car2pol(error_cart)
            
            # print "error_cart", error_cart, "error_pol", error_pol
            
            # prepare argument
            arrarg  = error_pol[1:].reshape(error_cart.shape[0]-1, )
            
            # transform back to cartesian
            pred = -ct_pol2car(gain, arrarg).reshape((self.brain.dim_s_motor, 1))
        else:
            pred = -np.sign(error_cart) * gain

        smdict["s_pred"] = pred
        return smdict
        
default_conf_motivations = [
    {
        "class": Motivation
    }
]
