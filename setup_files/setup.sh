#!/bin/bash
cd ..
output=$(cat /etc/*-release)
if ! echo $output  | grep "Ubuntu"
then
	echo "OS is incompatible"
	exit 1
fi
sudo apt-get upgrade
sudo apt-get update
sudo apt-get install libhdf5-serial-dev hdf5-tools libhdf5-dev zlib1g-dev zip libjpeg8-dev liblapack-dev libblas-dev gfortran
sudo apt-get install python3 python3-dev
sudo apt-get install curl cmake g++ authbind
sudo touch /etc/authbind/byport/80
sudo chmod 777 /etc/authbind/byport/80
virtualenv -p python3 venv
sudo chmod -R 770 venv
output=$(ls)
if ! echo $output | grep "venv"
then
	echo "Venv error!"
	exit 1
fi
echo "Venv is ok!"
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo python3 get-pip.py
. ./venv/bin/activate
git clone https://github.com/FalkTannhaeuser/python-onvif-zeep.git
cd python-onvif-zeep
python3 setup.py install
pip3 install --upgrade onvif_zeep
mv wsdl ../wsdl
cd ..
sudo rm -rf python-onvif-zeep
output=$(cat /etc/nv_tegra_release)
if echo $output | grep aarch64
then
	pip3 install --pre --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/$1 tensorflow
	sed -i '$ d' settings.ini
	echo 'device = Jetson' >> settings.ini
else
	sed -i '$ d' settings.ini
	echo 'device = CPU' >> settings.ini
	echo 'tensorflow' >> requirements.txt
fi
pip3 install -r requirements.txt
