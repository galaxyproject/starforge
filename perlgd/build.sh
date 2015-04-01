#!/bin/sh
arch=x86_64
pkg=perlgd
version=2.56
build_deps=""
urls="
https://cpan.metacpan.org/authors/id/L/LD/LDS/GD-${version}.tar.gz
"

build=/build/

apt-get -qq update &&
    apt-get install --no-install-recommends -y $build_deps &&
    mkdir ${build} &&
    cd ${build} &&

    ( for url in $urls; do
        wget "$url" || false || exit
    done ) &&

    tar xfz GD-${version}.tar.gz &&
    pwd &&
    chmod ugo+w GD-${version}/bdf_scripts/* &&
    tar zcf /host/GD-${version}.tar.gz GD-${version}/
