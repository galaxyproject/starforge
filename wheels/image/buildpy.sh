#!/bin/bash
set -e

arch=$(uname -m)

case $arch in
    i686)
        CC='gcc -m32'
        CXX='g++ -m32'
        F77='gfortran -m32'
        LDFLAGS='-L/usr/lib/i386-linux-gnu'
        export CC CXX F77 LDFLAGS
        ;;
    x86_64)
        LDFLAGS='-L/usr/lib/x86_64-linux-gnu'
        export LDFLAGS
        ;;
esac

build_and_install_py()
{
    cp=$1 && py=$2 && ucs=$3 && \
    ./configure --prefix=/python/${cp}-${arch} --enable-unicode=${ucs} && \
    make install && \
    # remove test suite files for space
    mv /python/${cp}-${arch}/lib/python${py}/test /python/${cp}-${arch}/lib/python${py}/test.tmp && \
    mkdir /python/${cp}-${arch}/lib/python${py}/test && \
    mv /python/${cp}-${arch}/lib/python${py}/test.tmp/{regrtest.py*,test_support.py*,__init__.py*,pystone.py*} \
        /python/${cp}-${arch}/lib/python${py}/test/ && \
    rm -rf /python/${cp}-${arch}/lib/python${py}/test.tmp && \
    # remove extra copy of libpythonX.Y.a, save some space
    rm /python/${cp}-${arch}/lib/libpython${py}.a && \
    ln -s /python/${cp}-${arch}/lib/python${py}/config/libpython${py}.a /python/${cp}-${arch}/lib/libpython${py}.a && \
    make distclean || return 1
}

build_and_install_py $1 $2 $3
