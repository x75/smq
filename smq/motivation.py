"""smq Motivation modules

in explauto framework  these are called interest models

these modules essentially implement exploration strategies which depend on
 - the past states
 - the current state
 - the state of the model
 """

default_conf_motivations = {
    "class": Motivation2
}

class Motivation2(object):
    def __init__(self, conf, ifs_conf):
        self.conf = conf
        set_attr_from_dict(self, self.conf)

        # tentative list of attributes
        # - goal (current goal)
        # - certainty / confidence
        
    def sample(self):
        """sample from the motivation: yield an exploratory move"""
        return 0

    def fit(self, x):
        """fit the motivation module to a data item"""
        return
