FROM ubuntu:22.04

# set a directory for the app
WORKDIR /usr/src/soid/

# copy
COPY . .

# install ubuntu dependencies
RUN DEBIAN_FRONTEND=noninteractive \
  apt-get update \
  && apt-get install -y build-essential \
                        wget \
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
                        libtool \
                        freeglut3-dev \
                        libgl1-mesa-glx \
                        ffmpeg \
                        libsm6 \
                        libxext6 \
                        npm \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# expose ports
# soid frontend
EXPOSE 3000
# soid backend
EXPOSE 5001

# Install miniconda
ENV CONDA_DIR /opt/conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
     /bin/bash ~/miniconda.sh -b -p /opt/conda

# Put conda in path so we can use conda activate
ENV PATH=$CONDA_DIR/bin:$PATH

# link to prebuilt libcxx
RUN mkdir /usr/src/soid/deps/build
RUN ln -s /usr/src/soid/deps/prebuilt/klee /usr/src/soid/deps/build/libc++

# link to prebuilt klee-uclibc
RUN ln -s /usr/src/soid/deps/prebuilt/klee-uclibc /usr/src/soid/deps/klee-uclibc

# link to prebuilt klee
RUN ln -s /usr/src/soid/deps/prebuilt/klee /usr/src/soid/deps/klee

# link to prebuilt llvm-project
RUN ln -s /usr/src/soid/deps/prebuilt/llvm-project /usr/src/soid/deps/llvm-project

# link to prebuilt klee-float
RUN ln -s /usr/src/soid/deps/prebuilt/klee-float /usr/src/soid/deps/klee-float

# install python dependencies
RUN pip install --no-cache-dir -r /usr/src/soid/requirements.txt

# install soid
RUN pip install .

# prep duckietown-soid
RUN mv /usr/src/soid/examples/gui/prep /usr/src/soid/examples/gui/duckietown-soid/prep
RUN mv /usr/src/soid/examples/gui/launch /usr/src/soid/examples/gui/duckietown-soid/launch
RUN /usr/src/soid/examples/gui/duckietown-soid/prep

# run duckietown-soid
#CMD /usr/src/soid/examples/gui/launch
