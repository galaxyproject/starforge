#!/bin/sh
arch=x86_64
pkg=ucsc
version=312
build_deps="libc6-dev zlib1g-dev libncurses5-dev libmysqlclient-dev unzip libpng-dev libssl-dev"
urls="
http://hgdownload.soe.ucsc.edu/admin/jksrc.v${version}.zip
"

build=/build
dest="build/${pkg}_${arch}_${version}"

apt-get -qq update &&
    apt-get install --no-install-recommends -y $build_deps &&
    mkdir ${build} &&
    cd ${build} &&

    ( for url in $urls; do
        wget "$url" || false || exit
    done ) &&

    mkdir -p $HOME/bin/${arch}/ ${build}/${dest}/bin ${build}/${dest}/lib &&
    unzip jksrc.v${version}.zip &&
    cd kent/src/lib/ &&
    make &&
    cd ../utils/ &&
    COPT='-O -g -Wl,-rpath,$${ORIGIN}/../lib' &&
    ORIGIN='$ORIGIN'
    export COPT ORIGIN &&
    find . -type d -maxdepth 1 -mindepth 1 -exec make -C '{}' \; &&
    mv $HOME/bin/${arch}/* ${build}/${dest}/bin/ &&
    for lib in $(ldd ${build}/${dest}/bin/faToTwoBit | grep -o '=> /[^ ]*' | sed 's/=> //g'); do
        case $lib in
            */libcrypto.so*|*/libgcc_s.so*|*/libmysqlclient.so*|*/libssl.so*|*/libstdc++.so*)
                echo "including $lib"
                cp $lib ${build}/${dest}/lib/
                ;;
        esac
    done
    tar zcf /host/${pkg}-${version}-Linux-${arch}.tar.gz -C ${build}/${dest}/../ .
