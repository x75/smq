# smq/experiments

This is the place where experiments are specified, the plan being so:

* common experiment.py script
* this loads a config which describes the experiment
    * agents[i]
        * task (loss-spec on sm-space; composite, hierarchical)
        * brain (learner/controller; composite, hierarchical)
    * environment (agents[], world)
