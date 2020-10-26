#!/bin/bash
os=($cat /etc/*-release)
if ! grep "Fedora" $os 
then
	str="apt-get"
else
	str="dnf"
fi
$str upgrade --refresh
$str install dnf-plugin-system-upgrade
$str install python2 
python get-pip.py
$str install -U virtualenv
python2 setup.py $str
