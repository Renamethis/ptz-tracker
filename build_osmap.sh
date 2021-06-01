sudo apt-get install autoconf automake libtool curl make g++ unzip
curl -OL https://github.com/protocolbuffers/protobuf/releases/download/v3.5.0/protobuf-all-3.5.0.zip
unzip protobuf-all-3.5.0.zip -d protobuf
rm -rf protobuf-all-3.5.0.zip
cd protobuf
cd protobuf-3.5.0
./autogen.sh
./configure
make
make check
sudo make install
sudo ldconfig
### MAKE LINK TO libprotobuf.so
cd ..
cd ..
git clone https://github.com/AlejandroSilvestri/osmap.git
cd osmap
protoc --cpp_out=. osmap.proto
mv osmap.pb.cc ../ORB_SLAM2/src/osmap.pb.cc
mv osmap.pb.h ../ORB_SLAM2/include/osmap.pb.h
mv include/Osmap.h ../ORB_SLAM2/include/Osmap.h
mv src/Osmap.cpp ../ORB_SLAM2/src/Osmap.cc
cd ..
### REMOVE OR COMMENT 'private:' in System.h in line 125
