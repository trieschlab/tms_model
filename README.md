# Ongoing brain rhythms shape I-wave properties in a computational model

The code associated with the article:

_Natalie Schaworonkow, Jochen Triesch_: Ongoing brain rhythms shape I-wave properties in a computational model. Brain Stimulation, 2018.
https://doi.org/10.1016/j.brs.2018.03.010

## Installation

The code was tested with Python 2.7 and NEURON 7.3. Parallel execution of simulations is implemented via mpi4py.

Clone the repository:

    git clone git@github.com:trieschlab/tms_model.git

Compile the NEURON mechanisms:

    cd tms_model/code
    nrnivmodl mechanisms/

## Execution
Test if the code works:

    python run_rusu.py -p params/rusu.py

This should generate an example plot in the working directory. The simulation including ongoing oscillations can be run with:

    python run_mu_rhythm.py -p params/high_power.py

(For the high oscillation power condition.)
All simulations are independent and can be run as separate cluster jobs.

## Contact

In case of questions, contact:
schaworonkow@fias.uni-frankfurt.de
