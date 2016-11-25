"""smq core classes"""

from smq.utils import set_attr_from_dict, set_attr_from_dict_ifs

class SMQModule(object):
    """Core SMQ module, take a configuration dictionary and copy that into members"""
    def __init__(self, conf):
        self.conf = conf
        # default conf to attr copy action
        set_attr_from_dict(self, self.conf)

class IFSMQModule(SMQModule):
    """SMQ module with an interface spec"""
    def __init__(self, conf, ifs_conf):
        SMQModule.__init__(self, conf)

        # configure structure of sensorimotor space
        set_attr_from_dict_ifs(self, ifs_conf)
