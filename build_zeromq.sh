git clone git://github.com/jedisct1/libsodium.git
cd libsodium
./autogen.sh 
./configure && make check 
sudo make install 
sudo ldconfig
cd ../
# Build, check, and install the latest version of ZeroMQ
git clone git://github.com/zeromq/libzmq.git
cd libzmq
./autogen.sh 
./configure --with-libsodium && make
sudo make install
sudo ldconfig
cd ../
# Now install ZMQPP
git clone git://github.com/zeromq/zmqpp.git
cd zmqpp
make
make check
make client
sudo make install
make installcheck
