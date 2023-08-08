### soid: smt-based oracles for investigating decisions

##### docker command

The easiest way to get setup with soid is to use Docker. You'll need to install both the [Docker Engine](https://docs.docker.com/engine/install/) and the [Docker Compose plugin](https://docs.docker.com/compose/install/). You can then just download `docker-compose.yml` (no need to clone the whole repository) and run the appropriate `docker compose run ...` command below. If the download fails, you might be having [authentication problems](https://docs.gitlab.com/ee/user/packages/container_registry/authenticate_with_container_registry.html).

To run the GUI, do:
```shell
$ docker compose run soid-gui
```
After initialization, the GUI is available from the host at `localhost:3000`. If the GUI complains about not having access to a display, you might need to install xvfb on the host machine, and do
```shell
$ Xvfb :0 -screen 0 1024x768x24 -ac +extension GLX +render -noreset &> xvfb.log &
$ export DISPLAY=:0
$ docker compose run soid-gui
```
instead. You can also spin up the hardcoded broadside crash scenario from the paper with
```shell
$ docker compose run soid-gui-crash
```
as well.


To work directly with soid, or to modify the GUI, you first need to spin the image up, and then get a shell.
```shell
$ docker compose run soid
```
Once in the container there is a minimal development environment, so to edit files you may need to do, e.g.:
```shell
$ apt-get update && apt-get emacs-nox
```
to get Emacs, or equivalently for Vim or otherwise. If you want to launch the GUI from inside the image, just run
```shell
$ ./usr/src/soid/examples/gui/duckietown-soid/launch
```
for the normal scenario or
```shell
$ ./usr/src/soid/examples/gui/duckietown-soid/launch -c
```
for the crash.

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
This will a) setup a Python `virtualenv` with the necessary dependencies installed, b) build `klee-uclibc` and `klee` for non-floating point analysis, and c) build `llvm3.4`, another version of `klee-uclibc`, and `klee-float` for floating point analysis. It can take some time to run, but has very verbose output throughout the install process.

Additionally, it takes two options. First, `llvm3.4` can have issues finding a gcc install on the host machine, so it may be necessary to specify an exact path. For example, you may need to do something like
```
$ ./install-deps -g /usr/lib/gcc/x86_64-linux-gnu/10
```
or alternatively `--gcc-path` to get everything to build successfully. Also, you can run
```
$ ./install-deps -c
```
or alternatively `--with-cvc5` to also get a build of cvc5, for some synthesis functionality as yet not yet fully implemented into `soid`.

##### running soid from the command line

To run `soid`, first enable the virtual environment created by the install, by
```
$ source ./deps/venv/bin/activate
```
Then invoke the `soid` tool using the cli interface, specifying the source program makefile `-m` and the directory containing the python module with the queries `-qs`, e.g.,:
```
$ ./scripts/soidcli -m ./examples/car/defensive/Makefile -qs ./examples/car/queries
```
will execute the car example.

##### options

Soid current takes four options:

- `-m`, `--make`: the location of the source program makefile, defaults to `./Makefile`.
- `-p`, `--path`: an alias for `-m` for symbolic execution engines that do not use makefiles.
- `-qs`, `--queries`: the location of the queries formulated as a python package, defaults to `./`.
- `-se`, `--symbexec`: symbolic execution engine, only 'klee' (the default) is supported.