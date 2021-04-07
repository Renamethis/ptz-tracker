sudo apt-get install autoconf automake libtool curl make g++ unzip
git clone https://github.com/protocolbuffers/protobuf.git
cd protobuf
git submodule update --init --recursive
./autogen.sh
./configure
make
make check
sudo make install
sudo ldconfig
### MAKE LINK TO libprotobuf.so
cd ..
git clone https://github.com/AlejandroSilvestri/osmap.git
cd osmap
protoc --cpp_out=. osmap.proto
mv osmap.pb.cc ../ORB_SLAM2/src/osmap.pb.cc
mv osmap.pb.h ../ORB_SLAM2/include/osmap.pb.h
mv include/Osmap.h ../ORB_SLAM2/include/Osmap.h
mv src/Osmap.cpp ../ORB_SLAM2/src/Osmap.cc
### REMOVE OR COMMENT 'private:' in System.h in line 125
