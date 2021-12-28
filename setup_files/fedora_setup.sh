#!/bin/bash
cd ..
sudo yum install cmake
sudo yum install python-devel numpy
sudo yum install gcc gcc-c++
sudo yum install gtk2-devel
sudo yum install libdc1394-devel
sudo yum install libv4l-devel
sudo ln -s /usr/include/libv4l1-videodev.h   /usr/include/linux/videodev.h
sudo dnf install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
sudo dnf install https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm
sudo dnf install ffmpeg ffmpeg-devel
sudo dnf install gstreamer1-plugins-{bad-\*,good-\*,base} gstreamer1-plugin-openh264 gstreamer1-libav --exclude=gstreamer1-plugins-bad-free-devel
sudo dnf install lame\* --exclude=lame-devel
sudo dnf group upgrade --with-optional Multimedia
sudo yum install libpng-devel
sudo yum install libjpeg-turbo-devel
sudo yum install jasper-devel
sudo yum install openexr-devel
sudo yum install libtiff-devel
sudo yum install libwebp-devel
sudo yum install python3
sudo yum install virtualenv
sudo dnf install gtk3-devel
### VIRTUALENV ###
virtualenv --system-site-packages -p python3 venv
sudo chmod -R 770 venv
output=$(ls)
if ! echo $output | grep "venv"
then
	echo "Venv error!"
	exit 1
fi
echo "Venv is ok!"
. ./venv/bin/activate
### ONVIF ###
git clone https://github.com/FalkTannhaeuser/python-onvif-zeep.git
cd python-onvif-zeep
python3 setup.py install
cd ..
python3 -m pip install --upgrade onvif_zeep
python3 -m pip install -r requirements_cpu.txt
### ORB_SLAM ###
. ./build_slam.sh
