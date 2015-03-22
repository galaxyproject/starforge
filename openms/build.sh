#!/bin/sh
arch=x86_64
pkg=openms
version=2.0
build_deps="libc6-dev zlib1g-dev libncurses5-dev libtool libqt4-dev libbz2-dev cmake autoconf automake"
urls="
https://github.com/OpenMS/OpenMS/archive/develop.tar.gz https://github.com/OpenMS/contrib/archive/master.tar.gz
"

"""
ToDo:
 - it's not working with './build galaxy openms' because cmake is to old in debian
 - export OPENMS_DATA_PATH=/foo/bar/openms-2.0-Linux-x86_64/share/OpenMS needs to be set
 - LDFLAGS magic is not working, LD_LIBRARY_PATH needs to be set
"""


apt-get -qq update &&
    apt-get install --no-install-recommends -y $build_deps &&
    mkdir /build &&
    cd /build &&

    ( for url in $urls; do
        wget "$url" || false || exit
    done ) &&

    mkdir -p /build/dest/bin /build/dest/lib &&
    tar xfz develop.tar.gz &&
    tar xfz master.tar.gz &&
    mv contrib-master OpenMS-develop/contrib &&
    cd OpenMS-develop/contrib &&
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
    tar zcf /host/${pkg}-${version}-Linux-${arch}.tar.gz -C /build/dest .
