#!/bin/sh

. /util/utility_functions.sh

pkg=Lmod
version=6.0
build_deps="libc6-dev zlib1g-dev unzip tcl lua5.2 lua5.2-filesystem lua5.2-posix lua5.2-term "
urls="
http://downloads.sourceforge.net/project/lmod/${pkg}-${version}.tar.bz2
"

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
    mkdir -p /build/dest/bin &&
    ./configure --prefix=/build/dest/ &&
    make install &&
    tar zcf /host/${pkg}-${version}-Linux-x86_64.tar.gz -C /build/dest .

