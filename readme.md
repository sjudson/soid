### soid: smt-based oracles for investigating decisions

##### docker command

To run the GUI, do:
```shell
$ sudo docker compose run soid-gui
```
After initialization, the GUI is available from the host at `localhost:3000`.

To work directly with soid, or to modify the GUI, you first need to spin the image up, and then get a shell.
```shell
$ sudo docker compose run soid
```
Once in the container there is a minimal development environment, so to edit files you may need to do, e.g.:
```shell
# apt-get update && apt-get emacs-nox
```
to get Emacs, or equivalently for Vim or otherwise. If you want to launch the GUI from inside the image, just run
```shell
# ./usr/src/soid/examples/gui/duckietown-soid/launch
```

##### source install

First you'll need to clone the repository with submodules:
```shell
$ git clone --recurse-submodules -j8 git@gitlab.com:rose-yale/soid.git
```

Then, run on debian/ubuntu:
```shell
$ sudo apt-get install build-essential \
                       curl \
                       libcap-dev \
                       git \
                       cmake \
                       libncurses5-dev \
                       python2-minimal \
                       unzip \
                       libtcmalloc-minimal4 \
                       libgoogle-perftools-dev \
                       libsqlite3-dev \
                       doxygen \
                       python3 \
                       python3-pip \
                       python3-dev \
                       virtualenv \
                       gcc-multilib \
                       g++-multilib \
                       z3 \
                       clang-11 \
                       llvm-11 \
                       llvm-11-dev \
                       llvm-11-tools \
                       m4 \
                       bison \
                       flex \
                       bc \
                       libboost-dev \
                       unzip \

```
After this completes, all that is left is to run the dependency install script from within the `deps` folder of the `soid` repo:
```
$ ./install-deps
```
This will build `klee-uclibc`, `klee`, and `cvc5`, as well as setup a Python `virtualenv` with the necessary dependencies installed. It can take some time to run, but has very verbose output throughout the install process.

##### soid codebase overview

`soid` is composed of three main parts: the `soid` tool itself, `soidlib`, and `Symbolize`.

The first part, the `soid` tool itself, lives at `./soid/soid`. It is a Python program that takes as input (i) the location of the makefile for a source program written in c++ with suitable symbolic execution annotations, and (ii) a set of queries formulated as a python package. It then executes the queries on the source program, and provides a detailed print out of the result.

The second part, `soidlib`, refers to both a python library at `./soid/soidlib/soidlib.py` and c++ library at `./soid/soidlib/soidlib.h`. The python library supports writing queries, while the c++ library supports writing source programs amenable to analysis using soid (for the moment, it mostly just wraps `klee.h`).

The last part, `Symbolize` at `./soid/symbolize/Symbolize.cpp`, is a currently in-progress component to autogenerate the annotations necessary for symbolic executions without requiring a programmer to manually alter the source program so that it can be used with soid/klee.

##### running soid

To run `soid`, first enable the virtual environment created by the install, by
```
$ source ./venv/bin/activate
```
Then invoke the `soid` tool, specifying the source program makefile `-m` and the directory containing the python module with the queries `-qs`, e.g.,:
```
$ ./soid/soid.py -vs -m ./examples/car/defensive/Makefile -qs ./examples/car/queries
```
will execute the microwave example.

##### options

Soid current takes two options:

- `-m`, `--make`: the location of the source program makefile, defaults to `./Makefile`.
- `-qs`, `--queries`: the location of the queries formulated as a python package, defaults to `./`.