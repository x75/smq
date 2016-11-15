

# Items


## Filesystem

Separate the core component lib from the actual experiments,
specification, and logging data.


## dimensions

what is system, what is robot, what are dimensions, do proper spec of

-   proprioceptive
-   exteroceptive
-   interoceptive
-   reward system: pain, pleasure, hunger, &#x2026;


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

how logging and ros publishing is the same or not?


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

