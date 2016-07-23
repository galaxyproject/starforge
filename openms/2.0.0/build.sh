#!/bin/sh
arch=x86_64
pkg=openms
version=2.0
build_deps="libc6-dev zlib1g-dev libncurses5-dev libtool libqt4-dev libbz2-dev cmake autoconf automake"
urls="
https://github.com/OpenMS/OpenMS/archive/Release2.0.0.tar.gz https://github.com/OpenMS/contrib/archive/master.tar.gz
"

# - OPENMS_DATA_PATH=/foo/bar/openms-2.0-Linux-x86_64/share/OpenMS needs to be set
# - LD_LIBRARY_PATH=/foo/bar/openms-2.0-Linux-x86_64/lib/ needs to be set

# enable backports to get a newer cmake version
echo 'deb http://http.debian.net/debian-backports squeeze-backports main' >> /etc/apt/sources.list

apt-get -qq update &&
    apt-get install -t squeeze-backports --no-install-recommends -y $build_deps &&
    mkdir /build &&
    cd /build &&

    ( for url in $urls; do
        wget "$url" || false || exit
    done ) &&

    mkdir -p /build/dest/bin /build/dest/lib &&/usr/lib/x86_64-linux-gnu/libgthread-2.0.so
    tar xfz Release2.0.0.tar.gz &&
    tar xfz master.tar.gz &&
    mv contrib-master OpenMS-Release2.0.0/contrib &&
    cd OpenMS-Release2.0.0/contrib &&
    cmake . -DBUILD_TYPE=SEQAN &&
    cmake . -DBUILD_TYPE=LIBSVM &&
    cmake . -DBUILD_TYPE=XERCESC &&
    cmake . -DBUILD_TYPE=GSL &&
    cmake . -DBUILD_TYPE=BOOST -DNUMBER_OF_JOBS=4 &&
    cmake . -DBUILD_TYPE=COINOR &&
    cmake . -DBUILD_TYPE=BZIP2 &&
    cmake . -DBUILD_TYPE=GLPK &&
    cmake . -DBUILD_TYPE=EIGEN &&
    cmake . -DBUILD_TYPE=WILDMAGIC &&
    cd .. &&
    mkdir build && cd build &&
    ORIGIN='$ORIGIN' &&
    export ORIGIN &&
    LDFLAGS='-Wl,-rpath,$${ORIGIN}/../lib' cmake .. -DCMAKE_INSTALL_PREFIX=/build/dest -DHAS_XSERVER=OFF -DENABLE_TUTORIALS=OFF -DENABLE_STYLE_TESTING=OFF -DENABLE_UNITYBUILD=OFF -DWITH_GUI=OFF &&
    make OpenMS TOPP UTILS &&
    make install &&
    cp -d /usr/lib/libQtCore* /build/dest/lib/ &&
    cp -d /usr/lib/libQtNetwork* /build/dest/lib/ &&
    cp -d /usr/lib/libgomp.* /build/dest/lib/ &&
    cp -d /lib/libglib-2.0* /build/dest/lib/ &&
    cp -d /usr/lib/libgthread-2.0.so* /build/dest/lib/ &&
    cp -d /lib/libpcre.so* /build/dest/lib/ &&
    tar zcf /host/${pkg}-${version}-Linux-${arch}.tar.gz -C /build/dest .
