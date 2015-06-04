#!/bin/bash

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

build=/host/build.$(hostname)

apt-get -qq update &&
    # set timezone for debian/changelog
    echo 'America/New_York' > /etc/timezone &&
    dpkg-reconfigure tzdata &&
    apt-get install --no-install-recommends -y $build_deps &&
    mkdir $build &&
    cd $build &&
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
    cd nginx-${nginx_version} &&
    patch -p0 </host/rules.patch &&
    patch -p0 </host/control.patch &&
    head -1 debian/changelog | sed -e 's/nginx (\(.*\)) .*/\1/' >debian/nginxSourceDebVersion &&
    ( for name in core extras full light; do
        for f in debian/nginx-${name}.*; do
            ext="${f##*.}"
            base="${f%.*}"
            if [ $f == debian/nginx-${name}.install ]; then
                sed -i -e "s#^debian/build-${name}/#debian/build-${name}-upload/#" $f
            fi
            mv $f ${base}-upload.${ext}
        done
    done ) &&
    dch -v ${ppa_version} -D ${dch_dist} "${dch_message}" &&
    debuild -S -sd -us -uc &&
    # build binary packages
    #apt-get install --no-install-recommends -y autotools-dev dh-systemd \
    #  libexpat-dev libgd2-dev libgeoip-dev liblua5.1-dev libmhash-dev \
    #  libpam0g-dev libpcre3-dev libperl-dev libssl-dev libxslt1-dev zlib1g-dev && 
    #debuild -sd -us -uc &&
    echo "To sign: debsign -S ${pkg}_${ppa_version}_source.changes" &&
    echo "To push: dput ppa:natefoo/nginx-upload ${pkg}_${ppa_version}_source.changes"
