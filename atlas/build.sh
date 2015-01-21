#!/bin/bash

version=3.10.2
urls="
http://downloads.sourceforge.net/project/math-atlas/Stable/${version}/atlas${version}.tar.bz2
http://www.netlib.org/lapack/lapack-3.5.0.tgz
"

# The libgfortran muckery is because the filesystem layout looks like this, on
# squeeze:
#
# /usr/lib/gcc/x86_64-linux-gnu/4.4.5/libgfortran.so -> ../../../x86_64-linux-gnu/libgfortran.so.3
# /usr/lib/x86_64-linux-gnu/libgfortran.so.3 -> libgfortran.so.3.0.0
# /usr/lib/x86_64-linux-gnu/libgfortran.so.3.0.0 (real file)
#
# The assumption is made that the symlinks point to the most specific (e.g.
# libgfortran.so.3.0.0) version of the library. I am not aware of any linuxes
# that do not follow this convention. Regardless, this is the case on squeeze.

mkdir /build &&
    cd /build &&

    ( for url in $urls; do
        wget "$url" || false || exit
    done ) &&

    tar jxf atlas${version}.tar.bz2 &&
    cd ATLAS &&
    patch -p1 </host/static_full_blas_lapack.diff &&
    patch -p1 </host/shared_libraries.diff &&
    patch -p1 </host/cpu-throttling-check.diff &&
    mkdir build &&
    cd build &&
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
        -Si cputhrchk 0 &&
    make &&
    make install &&
    libgfortran=$(readlink -f $(gcc -print-search-dirs|grep ^install:|awk '{print $2}')/libgfortran.so) &&
    basename_libgfortran=$(basename $libgfortran) &&
    libgfortran_version=${basename_libgfortran#"libgfortran.so."} &&
    cp $libgfortran /build/dest/lib &&
    ln -s $(basename $libgfortran) /build/dest/lib/libgfortran.so.${libgfortran_version:0:1} &&
    ln -s libgfortran.so.${libgfortran_version:0:1} /build/dest/lib/libgfortran.so &&
    tar zcf /host/atlas-${version}-Linux-x86_64.tar.gz -C /build/dest .
