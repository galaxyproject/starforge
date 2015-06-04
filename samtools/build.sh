#!/bin/sh

pkg=samtools
version=0.1.19
build_deps="libc6-dev zlib1g-dev libncurses5-dev"
urls="
http://downloads.sourceforge.net/project/samtools/samtools/${version}/samtools-${version}.tar.bz2
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
    mkdir -p /build/dest/bin /build/dest/lib /build/dest/include/bam /build/dest/include/bcf &&
    cp samtools bcftools/bcftools bcftools/vcfutils.pl /build/dest/bin &&
    cp libbam.a bcftools/libbcf.a /build/dest/lib &&
    cp *.h /build/dest/include/bam &&
    cp bcftools/*.h /build/dest/include/bcf &&
    tar zcf /host/samtools-${version}-Linux-x86_64.tar.gz -C /build/dest .

