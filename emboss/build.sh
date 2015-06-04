#!/bin/sh
arch=x86_64
pkg=emboss
version=6.6.0
build_deps="libc6-dev zlib1g-dev libncurses5-dev"
urls="
ftp://emboss.open-bio.org/pub/EMBOSS/EMBOSS-${version}.tar.gz
"

apt-get -qq update &&
    apt-get install --no-install-recommends -y $build_deps &&
    mkdir /build &&
    cd /build &&

    ( for url in $urls; do
        wget "$url" || false || exit
    done ) &&

    mkdir -p $HOME/bin/${arch}/ /build/dest/bin /build/dest/lib &&
    tar xfvz EMBOSS-${version}.tar.gz &&
    cd EMBOSS-${version} &&
    ORIGIN='$ORIGIN' &&
    export ORIGIN &&
    LDFLAGS='-Wl,-rpath,$${ORIGIN}/../lib' ./configure --prefix /build/dest --without-x && make && make install &&
    tar zcf /host/${pkg}-${version}-Linux-${arch}.tar.gz -C /build/dest .
