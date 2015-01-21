#!/bin/sh

version=3.10.2
urls="
http://downloads.sourceforge.net/project/math-atlas/Stable/${version}/atlas${version}.tar.bz2
http://www.netlib.org/lapack/lapack-3.5.0.tgz
"

apt-get -qq update &&
    mkdir /build &&
    cd /build &&

    ( for url in $urls; do
        wget "$url" || false || exit
    done ) &&

    tar jxf atlas${version}.tar.bz2 && \
    cd ATLAS && \
    patch -p1 </host/static_full_blas_lapack.diff && \
    patch -p1 </host/shared_libraries.diff && \
    patch -p1 </host/cpu-throttling-check.diff && \
    mkdir build && \
    cd build && \
    ../configure \
        --prefix="/build/dest" \
        -D c -DWALL \
        -b 64 \
        -Fa alg '-fPIC' \
        -Ss f77lib "-L$(gcc -print-search-dirs|grep ^install:|awk '{print $2}') -lgfortran -lgcc_s -lpthread"  \
        --with-netlib-lapack-tarfile=/build/lapack-3.5.0.tgz \
        -A 14 \
        -V 384 \
        -v 2 \
        -t 0 \
        -Ss ADdir ../../archdefs/amd64 \
        -Si cputhrchk 0 && \
    make && \
    make install && \
    tar zcf /host/atlas-${version}-Linux-x86_64.tar.gz -C /build/dest .
