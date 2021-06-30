#!/bin/bash
# LIBZMQ
git clone git://github.com/zeromq/libzmq.git
cd libzmq
mkdir build
cd build
cmake ..
sudo make -j4 install
# CPPZMQ
cd ..
cd ..
git clone https://github.com/zeromq/cppzmq.git
cd cppzmq
mkdir build
cd build
cmake ..
sudo make -j4 install
cd ..
cd ..
# Python zmq
. ./venv/bin/activate
python3 -m pip install zmq
