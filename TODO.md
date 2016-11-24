

# Items


## add brains

-   interest models, learning from kinesis / kinesis as explorer
-   im, imol, actinf, eh, iso, &#x2026;
-   hyperopt'ing
-   x taxis
-   x kinesis


## add robots

-   sphero
-   cartpole
-   x stdr
-   x arm
-   x check pointmass kinematic vs. dynamic control: doesn't evenmake
    sense for kinematic control?


## add worlds


### pointmass world

-   add force fields
-   add structure and obstacles
-   x increase dimensions 3, 10


## sm space

-   dimensions again: need to be able to access sm variables by name
    from anywhere (!!!)
-   partition order: make sure that the order of sm space partitions is
    consistent with respect to smdict keys etc
-   provide for an efficient way of integrating very high dimensional
    observations, like images without generating high dimensional
    column name arrays etc


### dimensions

what is system, what is robot, what are dimensions, do proper spec of

-   proprioceptive
-   exteroceptive
-   interoceptive
-   reward system: pain, pleasure, hunger, &#x2026;


## fix plotting

-   distinguish analyses and plots
-   x plotting proper from prototype
    -   x switch to pandas dataframes as structured arrays seem weird
    -   x fix hardcoded tablename
-   x dataframes also solve the column name problem
-   x make sure plot funcs are dealing with figures and axes, so there
    can be a final aggregation of different parts into a final figure
    that can also be saved to print format


## failsafe

-   make failsafe checks for configuration consistency


## integration / robots lib

-   ideally, i would like to have a library of systems which can be
    equipped with wrappers for: explauto, ROS, &#x2026; probably using
    decorators
-   x use explauto or not? <span class="underline">no</span>


## experiment specification

experiments.py

how to define experiment structure in conf that can capture different
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

-   x how to separate world, robot, task appropriately: current state
    (v2) seems ok


## logging

-   how logging and ros publishing is the same or not: ROS also
    involves inputs whereas logging is only one-way
-   logging/publishing decorators
-   profiling log function, compare log2 (direct hdf5) + log3 (via pandas)
-   x column names for tables


## tasks

the actually interesting bit

-   artificial organism with brain equation: bacterial random search,
    directional field, internal simulation, TSPwAC
-   motor babbling
-   goal babbling
-   &#x2026;


## efus

-   ultrastability
-   explorer (kinesis, interest models)
-   learner


## dynamic challenges

-   dynamic creation of new variables
-   dynamic length of run
-   dynamic structural changes


## neural networks

-   include tricks of the trade foo: input cleaning, square augmented &#x2026;
-   include deep learning foo


## testing

-   do unit testing


## submodules

which parts to do as submodules:

-   noiselib: uniform, gaussian, binomial, pareto, &#x2026;
-   learnlib: rls, force, eh, iso, &#x2026;
-   losslib: mse, mae, pi, ais, &#x2026;
-   analylib: plot timeseries, plot histograms, plot hexbin, plot
    dimstack, scattermatrix, &#x2026;


## Filesystem

Separate the core component lib from the actual experiments,
specification, and logging data.

Put that into smp<sub>experiments</sub>.

