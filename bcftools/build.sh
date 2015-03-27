#!/bin/sh

. /util/utility_functions.sh

if [ -z $2 ] ; then
    pkg=$2
else
    pkg=bcftools
fi

if [ -z $3 ] ; then
    version=$3
else
    version=1.0
fi

build_deps="libc6-dev zlib1g-dev"
urls="
https://github.com/samtools/${pkg}/releases/download/${version}/${pkg}-${version}.tar.bz2
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
    sed -i.bak 's#/usr/local#/build/dest#' Makefile &&
    make &&
    make install &&
    tar zcf /host/${pkg}-${version}-Linux-x86_64.tar.gz -C /build/dest .

