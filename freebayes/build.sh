#!/bin/sh

. /util/utility_functions.sh

pkg="freebayes"
build_deps="libc6-dev git-core cmake zlib1g-dev"
url="
https://github.com/ekg/freebayes.git
"
revision="bfd9832"

binaries="
freebayes
bamleftalign
"

apt-get -qq update &&
    apt-get install --no-install-recommends -y $build_deps &&
    mkdir /build &&
    cd /build &&

    git clone --recursive $url
    cd freebayes
    git checkout $revision

    mkdir -p /build/dest/bin &&
    make &&
    ( for binary in $binaries ; do
        cp ./bin/$binary /build/dest/bin
    done ) &&
    tar zcf /host/${pkg}-${revision}-Linux-x86_64.tar.gz -C /build/dest .

