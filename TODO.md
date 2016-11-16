

# Items


## fix plotting

-   plotting proper from prototype: switch to pandas dataframes as structured arrays seem weird
-   dataframes also solve the column name problem


## add worlds


### pointmass world

-   increase dimensions 3, 10
-   add force fields
-   add structure and obstacles


## add robots

-   check pointmass kinematic vs. dynamic control
-   arm
-   stdr
-   sphero
-   cartpole


## add brains

-   x kinesis
-   taxis
-   learning from kinesis
-   im, imol, actinf, eh, iso, &#x2026;
-   hyperopt'ing


## sm space partition order

make sure that the order of sm space partitions is consistent with
respect to smdict keys etc


## failsafe

make failsafe checks for configuration consistency


## integration / robots lib

use explauto or not?

ideally, i would like to have a library of systems which can be equipped
with wrappers for: explauto, ROS, &#x2026; probably using decorators


## experiment specification

experiments.py

FIXME: how to define experiment structure in conf for different
example scenarios like:

-   single episode learning
-   multi episode learning (value func prop)
-   multi episode optimization (hpo, cma, evo, &#x2026;)
-   infinite episode, &#x2026;
-   single episode, single model, single task
-   single run multiple models single task
-   optimization run single model single task

IDEA: use a generic type "loop" which has a "step" method and a
"stack" member, stacks being ordered dicts/lists of "loops"


## high-level design qu's

how to separate world, robot, task appropriately


## logging

-   how logging and ros publishing is the same or not: ROS also
    involves inputs whereas logging is only one-way
-   logging/publishing decorators
-   column names for tables


## tasks


## efus

-   ultrastability
-   explorer
-   learner


## dynamic challenges

-   dynamic creation of new variables
-   dynamic length of run
-   dynamic structural changes


## neural networks

-   include tricks of the trade foo: input cleaning, square augmented &#x2026;
-   include deep learning foo


## testing

do unit testing


## submodules

which parts to do as submodules:

-   noiselib: uniform, gaussian, binomial, pareto, &#x2026;
-   learnlib: rls, force, eh, iso, &#x2026;
-   losslib: mse, mae, pi, ais, &#x2026;
-   analylib: plot timeseries, plot histograms, plot hexbin, plot
    dimstack, scattermatrix, &#x2026;


## dimensions

what is system, what is robot, what are dimensions, do proper spec of

-   proprioceptive
-   exteroceptive
-   interoceptive
-   reward system: pain, pleasure, hunger, &#x2026;


## Filesystem

Separate the core component lib from the actual experiments,
specification, and logging data.

Put that into smp<sub>experiments</sub>.

