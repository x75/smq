

# Items


## tasks

the actually interesting bit, grow package by stepping through the tasks

-   x jumping goal: x by counting, x by average error
-   learn an e2p model, e.g. taxis with distinct goal- and
    proprio-spaces
    -   clean up actinf/hebbsom and gmm's, ready to load with fit and
        predict
    -   integrate these
-   actinf, imol, im proprio?
-   use kinesis as explorer and learn a model
-   artificial organism with brain equation: bacterial random search,
    directional field, internal simulation, TSPwAC, reservoir fillup/consumption
-   motor babbling
-   goal babbling


## high-level design qu's

-   default configuration generator, also use it to repair/update old configs
-   revert to blocks paradigm, all blocks of same basic type
    -   globally share config among all blocks
    -   use one shared type "Block", init from config all the same
    -   use one shared smdict to globally ferry information
    -   every block lists the subscriptions and publishers it wants/creates
    -   the config dict is mapped onto comp graph without structural change
        (smpblocks)?
    -   hierarchical: "goal" is just another prediction in the motor
        command sense, such as proprio layer makes a prediction at proprio
        level, the lowest one, next level makes a prediction at one level
        up which becomes the goal for proprio, etc
-   test multiple robots, tasks, &#x2026;
-   x how to separate world, robot, task appropriately: current state
    (v2) seems ok


## add brains

-   interest models, learning from kinesis / kinesis as explorer
-   im, imol, actinf, eh, iso, &#x2026;
-   hyperopt'ing
-   x taxis
-   x kinesis


## add robots

-   logfile reading robot
-   sphero
-   cartpole
-   x stdr
-   x arm
-   x check pointmass kinematic vs. dynamic control: doesn't even make
    sense for kinematic control?


## add worlds

-   add force fields (pm, sa)
-   add structure and obstacles (pm, sa)
-   add exteroception (pm)
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

-   how to define experiment structure in conf that can capture different example scenarios like:
    -   single episode learning
    -   multi episode learning (value func prop)
    -   multi episode optimization (hpo, cma, evo, &#x2026;)
    -   infinite episode, &#x2026;
    -   single episode, single model, single task
    -   single run multiple models single task
    -   optimization run single model single task
-   IDEA: use a generic type "loop" which has a "step" method and a "stack" member, stacks being ordered dicts/lists of "loops"

-   hierarchy
    -   0th order innate hardwared controller (Darwinian) changes motor output according to rule
    -   1st order learning model (Skinnerian) changes controller parameters in order to
        change the change in motor output
    -   2nd order learning wraps around that again and changes the 1st
        order learners parameter to better change the 0th order parameters
        to change the motor output
    -   it should be possible to apply the same learning principles on all
        those levels (kinesis, taxis, online model learner with
        exploration, actinf, evo, hyperopt)?


## logging

-   how logging and ros publishing is the same or not: ROS also
    involves inputs whereas logging is only one-way
-   logging/publishing decorators
-   profiling log function, compare log2 (direct hdf5) + log3 (via pandas)
-   x column names for tables


## efus

-   ultrastability
-   explorer (kinesis, interest models)
-   learner


## dynamic challenges

-   dynamic creation of new variables
-   dynamic length of run
-   dynamic structural changes
-   make block types which get their step function body from the configuration


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

