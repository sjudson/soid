### soid: smt-based oracles for investigating decisions

##### install

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
                       clang-9 \
                       llvm-9 \
                       llvm-9-dev \
                       llvm-9-tools \
                       m4 \
                       bison \
                       flex \
                       bc \
                       libboost-dev \
                       unzip \
                       
```
or on MacOS, with [Homebrew](https://brew.sh/) installed
```shell
$ brew install curl \
               git \
               cmake \
               python \
               unzip \
               gperftools \
               sqlite3 \
               doxygen \
               bash \
               z3 \
               llvm@9
```
After this completes, all that is left is to run the dependency install script from within the base folder of the `soid` repo:
```
$ ./install-deps
```
This will build `klee-uclibc`, `klee`, and `cvc5`, as well as setup a Python `virtualenv` with the necessary dependencies installed. It can take some time to run, but has very verbose output throughout the install process.

##### soid codebase overview

`soid` is composed of three main parts: the `soid` tool itself, `soidlib`, and `Symbolize`.

The first part, the `soid` tool itself, lives at `./soid/soid`. It is a Python program that takes as input (i) the location of the makefile for a source program written in c++ with suitable symbolic execution annotations, and (ii) a set of queries formulated as a python package. It then executes the queries on the source program, and provides a detailed print out of the result.

The second part, `soidlib`, refers to both a python library at `./soid/soidlib/soidlib.py` and c++ library at `./soid/soidlib/soidlib.h`. The python library supports writing queries, while the c++ library supports writing source programs amenable to analysis using soid (for the moment, it mostly just wraps `klee.h`).

The last part, `Symbolize` at `./soid/symbolize/Symbolize.cpp`, is a currently in-progress component to autogenerate the annotations necessary for symbolic executions without requiring a programmer to manually alter the source program so that it can be used with soid.

##### running soid

To run `soid`, first enable the virtual environment created by the install, by
```
$ source ./venv/bin/activate
```
Then invoke the `soid` tool, specifying the source program makefile `-m` and the directory containing the python module with the queries `-qs`, e.g.,:
```
$ ./soid/soid.py -vs -m ./examples/microwave/src/Makefile -qs ./examples/microwave/queries
```
will execute the microwave example.

##### options

Soid takes five options:

- `-m`, `--make`: the location of the source program makefile, defaults to `./Makefile`.
- `-qs`, `--queries`: the location of the queries formulated as a python package, defaults to `./`.
- `-vs`, `--variants`: passes a `SOID_QUERY=XXX` variable to the makefile to allow using source code variants for different queries.
- `-n`, `--enum`: number of candidates to enumerate for synthesis queries (not yet implemented).