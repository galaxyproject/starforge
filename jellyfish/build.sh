#!/bin/sh

. /util/utility_functions.sh

if [ -z $2 ] ; then
    pkg=jellyfish
else
    pkg=$2
fi

if [ -z $3 ] ; then
    version=1.1.11
else
    version=$3
fi

build_deps="libc6-dev zlib1g-dev"
urls="
http://www.cbcb.umd.edu/software/${pkg}/${pkg}-${version}.tar.gz
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
	./configure --prefix=/build/dest &&
    make &&
    make install &&
    tar zcf /host/${pkg}-${version}-Linux-x86_64.tar.gz -C /build/dest .

