#!/bin/bash
cd ..
# PANGOLIN
git clone https://github.com/stevenlovegrove/Pangolin.git
cd Pangolin
mkdir build
cd build
cmake ..
cmake --build .
cd ..
cd ..
# OPENCV
. ./build_opencv.sh
# EIGEN
git clone https://gitlab.com/libeigen/eigen.git
cd eigen
mkdir build
cd build
cmake ..
make -j4
sudo make install
#sudo ln -s /usr/include/eigen3/Eigen /usr/local/include/Eigen
cd ..
cd ..
# ORB_SLAM
git clone https://github.com/raulmur/ORB_SLAM2.git
mv orb_module ORB_SLAM2/orb_module
. .setup_files/build_osmap.sh # BUILD OSMAP MODULE
. ./setup_files/build_zeromq.sh # BUILD ZEROMQ LIBRARY
. ./setup_files/slam_configure.sh # CONFIGURING SOURCE ORB_SLAM2 FILES
cd ORB_SLAM2
. ./build.sh
cd ..
cd orb_module
mkdir build && cd build
cmake ..
make -j4
