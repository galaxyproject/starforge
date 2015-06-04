#!/bin/sh

. /util/utility_functions.sh

if [ -z $2 ] ; then
    pkg=R
else
    pkg=$2
fi

if [ -z $3 ] ; then
    version=3.2.0
else
    version=$3
fi

build_deps="libc6-dev zlib1g-dev tcl-dev tk-dev libblas-dev liblapack-dev libcairo2-dev libpng12-dev libtiff4-dev libjpeg-dev libreadline-dev default-jre"
urls="http://cran.rstudio.com/src/base/R-3/$pkg-$version.tar.gz"

apt-get -qq update &&
    apt-get install --no-install-recommends -y $build_deps &&
    mkdir /build &&
    cd /build &&

    ( for url in $urls; do
        tarball=`download_tarball $url` || false || exit
    done ) &&

    ( for tarball in * ; do
      extract_tarball $tarball || false || exit
    done ) &&

    cd ${pkg}-${version} &&
    export LDFLAGS='-Wl,-rpath,\$$ORIGIN/../lib' &&
    ./configure --with-readline=yes \
                --with-x=no \
                --with-blas \
                --with-lapack \
                --with-cairo \
                --with-libpng \
                --enable-R-shlib \
                --libdir=/build/dest/lib \
                --prefix=/build/dest \
                --with-tcltk &&
    make &&
    make install &&
    sed -i 's#/build/dest#${R_ROOT_DIR}#g' /build/dest/bin/R &&
    sed -i 's#/build/dest#${R_ROOT_DIR}#g' /build/dest/lib/R/bin/R &&
    sed -i 's#/build/dest#$(R_ROOT_DIR)#g' /build/dest/lib/R/etc/Makeconf &&
    cp /usr/lib/libgfortran* /build/dest/lib/ &&
    cp /usr/lib/libgomp* /build/dest/lib/ &&
    cp /usr/lib/libblas.so.3gf /build/dest/lib &&
    cd /build/dest/lib &&
    ln -s libgfortran.so.3 libgfortran.so &&
    ln -s libgomp.so.1.0.0 libgomp.so &&
    cd - &&
    cd /build/dest/lib/R/lib &&
    for i in ../../lib* ; do ln -s $i ; done &&
    cd - &&
    tar zcf /host/${pkg}-${version}-Linux-x86_64.tar.gz -C /build/dest .

