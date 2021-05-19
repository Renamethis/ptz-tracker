git clone https://github.com/opencv/opencv.git -b 3.4
git clone https://github.com/opencv/opencv_contrib.git -b 3.4

mkdir -p build && cd build

cmake -DOPENCV_EXTRA_MODULES_PATH=../opencv_contrib/modules ../opencv

cmake --build .

cd ..
