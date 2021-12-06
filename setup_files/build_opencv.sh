#!/bin/bash
cd ..
git clone https://github.com/opencv/opencv.git
git clone https://github.com/opencv/opencv_contrib.git

mkdir -p build && cd build

cmake -D CMAKE_INSTALL_PREFIX=../venv \
 -D CMAKE_BUILD_TYPE=RELEASE \
 -D PYTHON_INCLUDE_DIRS=../venv/include/python3.6m  \
 -D PYTHON_LIBRARIES=../usr/lib64/libpython3.6m.so \
 -D BUILD_opencv_python3=ON \
 -D OPENCV_EXTRA_MODULES_PATH=../opencv_contrib/modules \
 -D PYTHON3_EXECUTABLE=../venv/bin/python3.6 \
 -D WITH_GSTREAMER=ON \
 -D BUILD_opencv_python2=OFF \
 -D PYTHON_PACKAGES_PATH=../venv/lib64/python3.6/site-packages \
 -D PYTHON_NUMPY_INCLUDE_DIRS=../venv/lib/python3.6/site-packages/numpy/core/include \
 -D WITH_GTK=ON \
 ../opencv

make -j8
sudo make install
cd ..
