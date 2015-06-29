#!/bin/sh

. /util/utility_functions.sh

if [ -z $2 ] ; then
    pkg=ViennaRNA
else
    pkg=$2
fi

if [ -z $3 ] ; then
    version=2.1.8
else
    version=$3
fi

build_deps="libc6-dev"
urls="
http://www.tbi.univie.ac.at/RNA/packages/source/${pkg}-${version}.tar.gz
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
	export LDFLAGS='-Wl,-rpath,\$$ORIGIN/../lib'
    ./configure --prefix=/build/dest --without-doc &&
    make &&
    make install &&
    cp /usr/lib/libgomp* /build/dest/lib/ &&
    tar zcf /host/${pkg}-${version}-Linux-x86_64.tar.gz -C /build/dest .

