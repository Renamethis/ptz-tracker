git clone https://github.com/opencv/opencv.git -b 3.4
git clone https://github.com/opencv/opencv_contrib.git -b 3.4

mkdir -p build && cd build

cmake -D CMAKE_INSTALL_PREFIX=/usr/local \
 -D OPENCV_EXTRA_MODULES_PATH=../opencv_contrib/modules \
 -D PYTHON_EXECUTABLE=venv/bin/python3.8 \
 -D CMAKE_INSTALL_PREFIX=$(python3 -c "import sys; print(sys.prefix)") \
 -D PYTHON3_INCLUDE_DIR=$(python3 -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())") \
 -D PYTHON3_PACKAGES_PATH=$(python3 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())") \
 -D WITH_GSTREAMER=ON \
 -D BUILD_EXAMPLES=ON \
 -D BUILD_opencv_python2=OFF \
 ../opencv

cmake --build .
sudo make install
cd ..
