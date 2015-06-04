#!/bin/sh
arch=x86_64
pkg=pkiss
version=2.2.12
build_deps="libboost-dev libboost-test-dev libboost-program-options-dev bison flex mercurial ksh"
urls="
https://launchpad.net/~bibi-help/+archive/ubuntu/bibitools/+files/bellmansgapc_2015.03.17.orig.tar.gz https://launchpad.net/~bibi-help/+archive/ubuntu/bibitools/+files/pkiss_2.2.12.orig.tar.gz
"
apt-get -qq update &&
    apt-get install -t squeeze-backports --no-install-recommends -y $build_deps &&

    ( for url in $urls; do
        wget --no-check-certificate --quiet "$url" || false || exit
    done ) 

    mkdir -p /build/dest/bin &&
    mkdir -p /build/dest/lib &&

    tar -xf bellmansgapc_2015.03.17.orig.tar.gz &&
    tar -xf pkiss_2.2.12.orig.tar.gz &&
    cd bellmansgapc-2015.03.17 &&
    cp config-templates/generic.mf config.mf &&
    sed -i 's|#PREFIX ?=|PREFIX = /build/gapc|g' config.mf &&
    make &&
    make install &&
    cp -r /build/gapc/lib /build/dest &&

    export PATH=$PATH:/build/gapc/bin &&
    cd ../pkiss_2.2.12/pkiss &&
    make -C Misc/Applications/pKiss all  &&
    cp -r Misc/Applications/lib/* /build/dest/lib &&
    
    cp Misc/Applications/pKiss/x86_64-linux-gnu/* /build/dest/bin &&
    cp Misc/Applications/pKiss/pKiss /build/dest/bin &&

    # for the librna.so and librnafast.so
    # export LD_LIBRARY_PATH=installdir/lib:$LD_LIBRARY_PATH
    # for the binaries
    # export PATH=installdir/bin:$PATH

    tar zcf /host/${pkg}-${version}-Linux-${arch}.tar.gz -C /build/dest .
