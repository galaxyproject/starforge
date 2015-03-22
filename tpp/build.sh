#!/bin/sh
arch=x86_64
pkg=tpp
version=4.8.0
build_deps="libc6-dev zlib1g-dev libncurses5-dev libbz2-dev time libxml-parser-perl libgd2-xpm-dev"
build_dir="/build/dest/"
urls="
http://downloads.sourceforge.net/project/sashimi/Trans-Proteomic%20Pipeline%20%28TPP%29/TPP%20v4.8%20%28philae%29%20rev%200/TPP_${version}-src.tgz
"

apt-get -qq update &&
    apt-get install --no-install-recommends -y $build_deps &&
    mkdir /build &&
    cd /build &&

    ( for url in $urls; do
        wget "$url" || false || exit
    done ) &&

    mkdir -p ${build_dir}/bin ${build_dir}/lib &&
    tar xfvz TPP_${version}-src.tgz &&
    cd TPP-${version}/trans_proteomic_pipeline/src/ &&
    echo "TPP_ROOT=${build_dir}" > Makefile.config.incl &&
    echo "TPP_WEB=${build_dir}/web/" >> Makefile.config.incl &&
    echo "CGI_USER_DIR=${build_dir}/cgi-bin/" >> Makefile.config.incl &&
    #echo "OBJ_ARCH=${build_dir}" >> Makefile.config.incl &&
    echo "HTMLDOC_BIN=" >> Makefile.config.incl &&
    echo "LINK=shared" >> Makefile.config.incl &&
    echo "LIBEXT=a" >> Makefile.config.incl &&
    make ARCH=linux-${arch} && make install ARCH=linux-${arch} &&
    #make && make install &&
    tar zcf /host/${pkg}-${version}-Linux-${arch}.tar.gz -C /build/dest .

