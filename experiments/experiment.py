"""
Experiment shell to use to run any experiment in smq

(c) 2016 Oswald Berthold

Requiring
 - configuration: a config file which is itself a python file which is loaded
   and evaluated and fully specifies the experiment

Providing
 - fixed set of experiment components
 - hooks to be able to insert custom arbitrary python code
 - command line arguments interacting with config
 - execution and job management
 - logging
 
"""

from smq.experiments import get_args
from smq.experiments import Experiment

def main(args):
    # print "args", args
    expr = Experiment(args)

    expr.run()
    
if __name__ == "__main__":
    main(get_args())
