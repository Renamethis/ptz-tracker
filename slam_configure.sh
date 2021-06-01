#!/bin/bash
### THiS SCRIPT PROVIDES CONFIGURING OF ORB_SLAM2 LIBRARY ###
### WARNING! RUN THIS SCRIPT ONLY ONCE ###
include_add_files="LocalMapping.cc LoopClosing.cc Tracking.cc System.cc Viewer.cc"
include_string="#include <unistd.h> \n#include <stdio.h>\n#include <stdlib.h>"
cd ORB_SLAM2/src
for file in $include_add_files; do
	sed -i "1i$include_string" $file
done
cd ..
sed -i -e "80,114d" CMakeLists.txt
src="src/Osmap.cc\nsrc/osmap.pb.cc"
prot_find="include(FindProtobuf)\nfind_package(Protobuf REQUIRED)"
prot_include="\${PROTOBUF_INCLUDE_DIR}"
prot_lib="\${PROTOBUF_LIBRARIES}"
eig_find="const KeyFrame\*"
eig_repl="KeyFrame\* const"
sed -i "/Viewer.cc/a $src" CMakeLists.txt
sed -i "/project(ORB_SLAM2)/a $prot_find" CMakeLists.txt
sed -i "/{Pangolin_INCLUDE_DIRS}/a $prot_include" CMakeLists.txt
sed -i "/libg2o.so/a $prot_lib" CMakeLists.txt
sed -i -e "125d" include/System.h
sed -i "s/$eig_find/$eig_repl/g" include/LoopClosing.h
cd ..
