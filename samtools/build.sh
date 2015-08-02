#!/bin/sh

pkg=samtools
version=1.2
build_deps="libc6-dev zlib1g-dev libncurses5-dev curl"
urls="
http://github.com/samtools/samtools/releases/download/${version}/samtools-${version}.tar.bz2
"

apt-get -qq update &&
    apt-get install --no-install-recommends -y $build_deps &&
    mkdir /build &&
    cd /build &&

    ( for url in $urls; do
        curl -L -O "$url" || false || exit
    done ) &&

    tar jxf samtools-${version}.tar.bz2 &&
    cd samtools-${version} &&
    make &&
    cd htslib-* &&
    make bgzip tabix &&
    mkdir -p /build/dest/bin /build/dest/lib /build/dest/include/bam &&
    cp -f bgzip tabix /build/dest/bin &&
    cd .. &&
    cp samtools /build/dest/bin &&
    cp libbam.a /build/dest/lib &&
    cp *.h /build/dest/include/bam &&
    tar zcf /host/samtools-${version}-Linux-x86_64.tar.gz -C /build/dest .

