"""
smq/smq/experiment.py: library components for the experiment shell

(c) 2016 Oswald Berthold
"""

import argparse

def get_args():
    import argparse
    # define defaults
    default_conf     = "conf/default.py"
    default_numsteps = 10
    # create parser
    parser = argparse.ArgumentParser()
    # add required arguments
    parser.add_argument("-c", "--conf",     type=str, default=default_conf,     help="Configuration file [%s]" % default_conf)
    parser.add_argument("-n", "--numsteps", type=int, default=default_numsteps, help="Number of outer loop steps [%d]" % default_numsteps)
    # parse arguments
    args = parser.parse_args()
    # return arguments
    return args

class Experiment(object):
    def __init__(self, args):
        self.conf = args.conf
        self.numsteps = args.numsteps

    def run(self):
        # FIXME: how to define experiment structure in conf for different scenarios like:
        # single run single model single task
        # single run multiple models single task
        # optimization run single model single task
        # ...
        # IDEA: use a generic type "loop" which has a "step" method and a "stack" member
        #       stacks are ordered dicts/lists of "loops"
        for i in xrange(self.numsteps):
            print "i = %d" % i
