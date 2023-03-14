#! /bin/bash

export SOID_PATH="/usr/src/soid"

eval "$(conda shell.bash hook)"
conda activate duckietown
export PYTHONPATH="${PYTHONPATH}:/usr/src/soid/examples/gui/duckietown-soid/learning"
export PYTHONPATH="${PYTHONPATH}:/usr/src/soid/examples/gui/duckietown-soid/src"
conda develop /usr/src/soid/examples/gui/duckietown-soid

python ./run_tests.py
