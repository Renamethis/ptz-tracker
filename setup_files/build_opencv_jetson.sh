cd ..
git clone https://github.com/opencv/opencv.git
git clone https://github.com/opencv/opencv_contrib.git
mkdir build && cd build
cmake -D WITH_CUDA=ON -D CUDA_ARCH_BIN="5.3" -D CUDA_ARCH_PTX="" -D WITH_GSTREAMER=ON -D WITH_LIBV4L=ON -D BUILD_TESTS=OFF -D BUILD_PERF_TESTS=OFF -D BUILD_EXAMPLES=ON -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=../venv -D INSTALL_PYTHON_EXAMPLES=OFF -D INSTALL_C_EXAMPLES=OFF  -D OPENCV_EXTRA_MODULES_PATH=../opencv_contrib/modules  -D PYTHON3_EXECUTABLE=../venv/bin/python3 -D PYTHON3_NUMPY_INCLUDE_DIRS=../venv/lib/python3.6/site-packages/numpy/core/include/ BUILD_opencv_python3=yes -D PYTHON_PACKAGES_PATH=../ptz-tracker/venv/lib/python3.6/site-packages/ -D PYTHON_LIBRARY=/usr/lib/aarch64-linux-gnu/libpython3.6m.so  ../opencv
make -j4
sudo make install
