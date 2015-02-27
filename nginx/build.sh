#!/bin/sh

# for ubuntu:trusty

pkg=nginx
nginx_version=1.4.6
ubuntu_version=${nginx_version}-1ubuntu3.2
ppa_version=${ubuntu_version}ppa1
dch_message="Restore the nginx-upload module from 2.2 branch in Github, now compatible with nginx 1.4.x."
build_deps="git"

DEBFULLNAME="Nathan Coraor"
DEBEMAIL="nate@bx.psu.edu"
export DEBFULLNAME DEBEMAIL
dch_dist=$(lsb_release -cs)

apt-get -qq update &&
    # set timezone for debian/changelog
    echo 'America/New_York' > /etc/timezone &&
    dpkg-reconfigure tzdata &&
    apt-get install --no-install-recommends -y $build_deps &&
    mkdir /build &&
    cd /build &&
    apt-get source $pkg &&
    git clone -b 2.2 --single-branch https://github.com/vkholodkov/nginx-upload-module.git/ \
        nginx-${nginx_version}/debian/modules/nginx-upload &&
    upload_module_shortrev=$(git --git-dir=nginx-${nginx_version}/debian/modules/nginx-upload/.git rev-parse --short HEAD) &&
    rm -rf nginx/debian/modules/nginx-upload/.git &&
    sed -e '/^ #Removed as it no longer works with 1.3.x and above.$/d' \
        -e 's/^ #\(nginx-upload\)$/ \1/' \
        -e 's%^ #\( Homepage: https://github.com/vkholodkov/nginx-upload-module\)$% \1/tree/2.2%' \
        -e "s/^ # Version: 2.2.0.*$/  Version: 2.2.1-${upload_module_shortrev}/" \
        -i nginx-${nginx_version}/debian/modules/README.Modules-versions &&
    sed -e 's#\(^\t    --add-module=$(MODULESDIR)/nginx-upload-progress \\\)#\t    --add-module=$(MODULESDIR)/nginx-upload \\\n\1#' \
        -i nginx-${nginx_version}/debian/rules &&
    cd nginx-${nginx_version} &&
    dch -v ${ppa_version} -D ${dch_dist} "${dch_message}" &&
    debuild -S -sd -us -uc &&
    cd .. &&
    cp nginx_*ppa* /host &&
    echo "To sign: debsign -S ${pkg}_${ppa_version}_source.changes" &&
    echo "To push: dput ppa:natefoo/nginx ${pkg}_${ppa_version}_source.changes" &&
    echo "To push: dput ppa:galaxyproject/nginx ${pkg}_${ppa_version}_source.changes"
