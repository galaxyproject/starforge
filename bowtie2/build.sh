#!/bin/sh

. /util/utility_functions.sh

if [ -z $2 ] ; then
    pkg=bowtie2
else
    pkg=$2
fi

if [ -z $3 ] ; then
    version=2.2.5
else
    version=$3
fi

build_deps="libc6-dev unzip"
urls="
http://downloads.sourceforge.net/project/bowtie-bio/$pkg/$version/$pkg-$version-source.zip
"

binaries="
bowtie2
bowtie2-align-l
bowtie2-align-s
bowtie2-build
bowtie2-build-l
bowtie2-build-s
bowtie2-inspect
bowtie2-inspect-l
bowtie2-inspect-s
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
    make &&
    ( for binary in $binaries ; do
        cp $binary /build/dest/bin
    done ) &&
    tar zcf /host/${pkg}-${version}-Linux-x86_64.tar.gz -C /build/dest .

