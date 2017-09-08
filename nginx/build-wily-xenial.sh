#!/bin/bash
set -e

# for ubuntu:wily or xenial

. /etc/os-release

dch_dist="$UBUNTU_CODENAME"

if [ "$dch_dist" == 'xenial' ]; then
    nginx_version=1.10.0
    ubuntu_version=${nginx_version}-0ubuntu0.16.04.4
    ppa_version=${ubuntu_version}ppa1
elif [ "$dch_dist" == 'wily' ]; then
    nginx_version=1.9.3
    ubuntu_version=${nginx_version}-3ubuntu3.3
    ppa_version=${ubuntu_version}ppa1
else
    echo "Use build-trusty.sh to build for trusty, or adapt script for newer distribution"
    exit 1
fi

pkg=nginx
dch_message="Restore the nginx-upload module from 2.2 branch in Github, compatible with nginx 1.9.x."
build_deps="git"

DEBFULLNAME="Nathan Coraor"
DEBEMAIL="nate@bx.psu.edu"
export DEBFULLNAME DEBEMAIL

build=/host/build.$(hostname)

apt-get -qq update

# set timezone for debian/changelog
echo 'America/New_York' > /etc/timezone
dpkg-reconfigure tzdata

apt-get install --no-install-recommends -y $build_deps

mkdir $build
cd $build

apt-get source $pkg

git clone -b 2.2 --single-branch https://github.com/vkholodkov/nginx-upload-module.git/ \
    nginx-${nginx_version}/debian/modules/nginx-upload
upload_module_shortrev=$(git --git-dir=nginx-${nginx_version}/debian/modules/nginx-upload/.git rev-parse --short HEAD)
rm -rf nginx/debian/modules/nginx-upload/.git

sed -e '/^ #Removed as it no longer works with 1.3.x and above.$/d' \
    -e 's/^ #\(nginx-upload\)$/ \1/' \
    -e 's%^ #\( Homepage: https://github.com/vkholodkov/nginx-upload-module\)$% \1/tree/2.2%' \
    -e "s/^ # Version: 2.2.0.*$/  Version: 2.2.1-${upload_module_shortrev}/" \
    -i nginx-${nginx_version}/debian/modules/README.Modules-versions

sed -e 's#\(\t\t\t--add-module=$(MODULESDIR)/nginx-upload-progress \\\)#\t\t\t--add-module=$(MODULESDIR)/nginx-upload \\\n\1#' \
    -i nginx-${nginx_version}/debian/rules

cd nginx-${nginx_version}
dch -v ${ppa_version} -D ${dch_dist} "${dch_message}"
debuild -S -sd -us -uc

echo "To sign: debsign -S ${pkg}_${ppa_version}_source.changes"
echo "To push: dput ppa:natefoo/nginx ${pkg}_${ppa_version}_source.changes"
echo "To push: dput ppa:galaxyproject/nginx ${pkg}_${ppa_version}_source.changes"
