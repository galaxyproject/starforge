#!/bin/sh

pkg=samtools
version=1.2
build_deps="libc6-dev zlib1g-dev libncurses5-dev"
urls="
https://github.com/samtools/samtools/releases/download/${version}/samtools-${version}.tar.bz2
"

apt-get -qq update &&
    apt-get install --no-install-recommends -y $build_deps &&
    mkdir /build &&
    cd /build &&

    ( for url in $urls; do
        wget "$url" || false || exit
    done ) &&

    tar jxf samtools-${version}.tar.bz2 &&
    cd samtools-${version} &&
    make &&
    mkdir -p /build/dest/bin /build/dest/lib /build/dest/include/bam &&
    cp samtools /build/dest/bin &&
    cp libbam.a /build/dest/lib &&
    cp *.h /build/dest/include/bam &&
    cd htslib-1.2.1 &&
    make bgzip tabix &&
    cp bgzip tabix /build/dest/bin &&
    tar zcf /host/samtools-${version}-Linux-x86_64.tar.gz -C /build/dest .
