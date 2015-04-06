#!/bin/sh

. /util/utility_functions.sh

if [ -z $2 ] ; then
    pkg=kraken
else
    pkg=$2
fi

if [ -z $3 ] ; then
    version=0.10.5-beta
else
    version=$3
fi

build_deps="libc6-dev zlib1g-dev unzip"
urls="
https://ccb.jhu.edu/software/${pkg}/dl/${pkg}-${version}.tgz
"

binaries="
kraken
kraken-build
kraken-filter
kraken-mpa-report
kraken-report
kraken-translate
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
    sh install_kraken.sh /build/dest/bin ;
    tar zcf /host/${pkg}-${version}-Linux-x86_64.tar.gz -C /build/dest .

