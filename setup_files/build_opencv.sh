#!/bin/bash
cd ..
git clone https://github.com/opencv/opencv.git
git clone https://github.com/opencv/opencv_contrib.git

mkdir -p build && cd build

cmake -D CMAKE_INSTALL_PREFIX=../venv \
 -D CMAKE_BUILD_TYPE=RELEASE \
 -D INSTALL_PYTHON_EXAMPLES=ON \
 -D OPENCV_EXTRA_MODULES_PATH=../opencv_contrib/modules \
 -D PYTHON3_EXECUTABLE=../venv/bin/python3.6 \
 -D PYTHON_INCLUDE_DIR=$(python3 -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())")  \
 -D PYTHON_LIBRARY=$(python3 -c "import distutils.sysconfig as sysconfig; print(sysconfig.get_config_var('LIBDIR'))") \
 -D WITH_GSTREAMER=ON \
 -D BUILD_EXAMPLES=ON \
 -D BUILD_opencv_python2=OFF \
 -D PYTHON_PACKAGES_PATH=../venv/lib/python3.6/site-packages \
 -D PYTHON3_NUMPY_INCLUDE_DIRS=../venv/lib/python3.6/site-packages/numpy/core/include \
 ../opencv

make -j4
sudo make install
cd ..
