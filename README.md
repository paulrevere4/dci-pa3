# Group Members

William Rory Kronmiller - RCS: kronmw

Paul Revere - RCS: reverp

# Running

To run this program, please install the following dependencies:

- The join-python library (we got this working by copying join.py into our python lib folders)
- The execnet Python library

These programs are designed to run on Python 3.3+ and are not compatible with
Python 2.7.

Once the dependencies are installed, it should be a matter of executing
`part_one.py` and `part_two.py`.

# Features/Bugs

Our program's output differs from the C program output. We have checked our
program for bugs, to the best of our abilities. The individual differences are
quite small, so the differences could possibly be a result of rounding error.

## Part One

Part One uses the join-python libary, which can be found here
<https://github.com/maandree/join-python>.

## Part Two

Part Two does not use the join python library, as that library does not support
distributed join calculus operations. Instead we use the execnet library, which
provides roughly equivalent functionality (asynchronous, distributed, channel-
based communications, spawning of parallel processes, checking of function arg-
uments against function prototypes, joining with processes). We have essentially
emulated the Join Calculus through execnet. The main difference is that the
child funcctions do not use return statements, but instead explicitly call
channel send functions.

Part Two can spawn processes on remote machines by setting up SSH sessions. The
remote connections can be set up by adding execnet gateways with SSH hostname
arguments in their constructors to the `gws` list in `__main__`. See line 103
for an example. To avoid making testers have to set up SSH public/private keys
or type their passwords in 20 times, the SSH gateway is commented out and the
remote executor is spawned as a new process on the local machine (see line
104).

Part Two is significantly slower than Part One, which seems to be a function of
the overhead of the execnet library versus the join-python library (which uses
threading instead of multiprocessing under the hood).

# Analysis of Distributed Computation versus Sequential

We expect that a distributed computation will have higher performance than a
sequential solution when we have a large number of machines that can communicate
with each other easily with little chance for faults. Computing clusters and
data centers both have environments similar to this. We also expect that the
distributed solution will be more efficient when the amount of data passed in
messages between machines can be kept to a minimum. In our example the only data
that is sent to the workers is in the form of three arrays that are the width of
the grid and one array of the same size is sent back. Finally, we expect higher
performance with distributed solutions on highly computational tasks, ones where
there is far more computation than communication for the workers. The task in
this assignment did not require much computation so in the end the cost of
communication was higher than the benefit of distribution.
