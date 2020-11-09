#!/bin/bash
output=$(cat /etc/*-release)
if ! echo $output  | grep "Ubuntu"
then
	str="dnf"
	sudo $str upgrade --refresh
else
	str="apt-get"
	sudo $str install dnf-plugin-system-upgrade
fi
sudo $str install virtualenv
output=$(ls)
if ! echo $output | grep "venv"
then
	echo "Venv error!"
	exit 1
fi
echo "Venv is ok!"
sudo virtualenv -p python2.7 ./venv
cd venv
cd bin
./activate
cd ..
cd ..
sudo python2 get-pip.py
sudo pip install -r requirements.txt
sudo wget "http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v2_coco_2018_03_29.tar.gz"
sudo cp ssd_mobilenet_v2_coco_2018_03_29.tar.gz models/research/object_detection/
#sudo python2 setup.py $str
