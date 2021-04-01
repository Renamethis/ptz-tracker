# PANGOLIN
sudo apt install g++
sudo apt install libgl1-mesa-dev
sudo apt install libglew-dev
sudo apt install cmake
sudo apt install libpython2.7-dev
sudo apt install pkg-config
sudo apt install libegl1-mesa-dev libwayland-dev libxkbcommon-dev wayland-protocols
sudo apt install ffmpeg libavcodec-dev libavutil-dev libavformat-dev libswscale-dev libavdevice-dev
sudo apt install libdc1394-22-dev libraw1394-dev
sudo apt install libjpeg-dev libpng12-dev libtiff5-dev libopenexr-dev
git clone https://github.com/stevenlovegrove/Pangolin.git
cd Pangolin
mkdir build
cd build
cmake ..
cmake --build .

# OPENCV

sudo apt-get install build-essential
sudo apt-get install cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev
sudo apt-get install python-dev python-numpy libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libdc1394-22-dev
git clone https://github.com/opencv/opencv.git
git clone https://github.com/opencv/opencv_contrib.git
cd opencv
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=Release -D CMAKE_INSTALL_PREFIX=/usr/local ..
make -j4
sudo make install

# EIGEN

git clone https://gitlab.com/libeigen/eigen.git
cd eigen
mkdir build
cd build
cmake ..
make -j4
sudo make install
sudo ln -s /usr/include/eigen3/Eigen /usr/local/include/Eigen

# ROS

sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-melodic.list'
sudo apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
sudo apt update
sudo apt install ros-melodic-desktop-full
echo "source /opt/ros/melodic/setup.bash" >> ~/.bashrc
source ~/.bashrc
sudo apt-get install python-rosdep
sudo rosdep init
rosdep update
### export ORB_SLAM2/Examples/ROS/
### SOLVE PROBLEM WITH usleep
### MAKE LINK WITH libprotobuf.so
### INSTALL OSMAP
### CHANGE CMakeLists.txt with libprotobuf from /usr/lib
### INSTALL ZEOMQ ( cppzmq )
### roslaunch rtsp_ros_driver rtsp_camera.launch hostname:=172.18.191.72 username:=admin password:=Supervisor stream:="rtsp://172.18.191.72/Streaming/Channels/2"

