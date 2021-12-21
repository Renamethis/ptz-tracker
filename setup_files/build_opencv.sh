#!/bin/bash
cd ..
git clone https://github.com/opencv/opencv.git
git clone https://github.com/opencv/opencv_contrib.git

mkdir -p build && cd build

cmake -D CMAKE_INSTALL_PREFIX=../venv \
 -D CMAKE_BUILD_TYPE=RELEASE \
 -D PYTHON_INCLUDE_DIRS=$(python3 -c "from sysconfig import get_paths as gp; print(gp()[\"include\"])")  \
 -D PYTHON_LIBRARIES=$(python3 -c "from sysconfig import get_config_var; print(\"%s/%s\" % (get_config_var(\"LIBDIR\"), get_config_var(\"INSTSONAME\")))") \
 -D BUILD_opencv_python3=ON \
 -D OPENCV_EXTRA_MODULES_PATH=../opencv_contrib/modules \
 -D PYTHON3_EXECUTABLE=$(python3 -c "import sys; print(sys.executable)") \
 -D WITH_GSTREAMER=ON \
 -D BUILD_opencv_python2=OFF \
 -D PYTHON_PACKAGES_PATH=$(python3 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())") \
 -D PYTHON_NUMPY_INCLUDE_DIRS=$(python3 -c "import os;import numpy;print(os.path.dirname(numpy.__file__))") \
 -D WITH_GTK=ON \
 ../opencv

make -j8
sudo make install
cd ..
