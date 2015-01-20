FROM debian:squeeze

MAINTAINER Nate Coraor <nate@bx.psu.edu>

ENV DEBIAN_FRONTEND noninteractive

ADD http://www.netlib.org/lapack/lapack-3.5.0.tgz /build/
ADD http://downloads.sourceforge.net/project/math-atlas/Stable/3.10.2/atlas3.10.2.tar.bz2 /build/
# Use for debugging to prevent frequent redownloading
#COPY lapack-3.5.0.tgz atlas3.10.2.tar.bz2 /build/
COPY static_full_blas_lapack.diff shared_libraries.diff cpu-throttling-check.diff /build/

RUN apt-get -qq update && \
    apt-get install --no-install-recommends -y bzip2 make gcc gfortran patch && \
    cd /build && \
    tar jxf atlas3.10.2.tar.bz2 && \
    mkdir ATLAS/build && \
    cd ATLAS && \
    patch -p1 </build/static_full_blas_lapack.diff && \
    patch -p1 </build/shared_libraries.diff && \
    patch -p1 </build/cpu-throttling-check.diff && \
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
    tar zcf /build/atlas-3.10.2-Linux-x86_64.tar.gz * -C /build/dest
