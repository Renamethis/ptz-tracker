#!/bin/bash
output=$(cat /etc/*-release)
if ! echo $output  | grep "Ubuntu"
then
	str="dnf"
	sudo $str install dnf-plugin-system-upgrade
else
	str="apt-get"
	sudo $str upgrade --refresh
	sudo $str update
fi
sudo $str install python2.7
sudo $str install virtualenv
sudo virtualenv -p python2.7 ./venv
output=$(ls)
if ! echo $output | grep "venv"
then
	echo "Venv error!"
	exit 1
fi
echo "Venv is ok!"
. ./venv/bin/activate
sudo python2.7 get-pip.py
pip install -r requirements.txt
git clone https://github.com/tensorflow/models.git
wget "http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v2_coco_2018_03_29.tar.gz"
cp ssd_mobilenet_v2_coco_2018_03_29.tar.gz models/research/object_detection/ssd_mobilenet_v2_coco_2018_03_29.tar.gz
sudo apt-get install protobuf-compiler python-pil python-lxml python-tk
cd models/research
wget -O protobuf.zip https://github.com/google/protobuf/releases/download/v3.0.0/protoc-3.0.0-linux-x86_64.zip
unzip protobuf.zip
./bin/protoc object_detection/protos/*.proto --python_out=.
export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/slim
cd ..
cd ..
sudo python2.7 conf/conf.py
#sudo python2 setup.py $str
