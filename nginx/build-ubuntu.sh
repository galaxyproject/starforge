#!/bin/bash
# tested for ubuntu trusty, wily and xenial
set -e

. /etc/os-release


apt-get -qq update && apt-get install -y lsb-release tzdata

pkg=nginx
dch_message="Restore the nginx-upload module from 2.2 branch in Github, compatible with nginx 1.x."
DEBFULLNAME="${DEBFULLNAME:-Nathan Coraor}"
DEBEMAIL="${DEBEMAIL:-nate@bx.psu.edu}"
PPA="${PPA:-ppa:natefoo/nginx}"
GPG_KEY="${GPG_KEY:-/gpg_key.asc}"
export DEBFULLNAME DEBEMAIL PPA GPG_KEY
dch_dist=$(lsb_release -cs)
build=/host/build.$(hostname)
build_deps="git dpkg-dev debhelper debian-keyring devscripts dput ca-certificates build-essential fakeroot gnupg2"
echo -e "Building for Ubuntu-$dch_dist\n"

# set timezone for debian/changelog
echo 'America/New_York' > /etc/timezone &&
dpkg-reconfigure debconf -f noninteractive tzdata &&
apt-get install --no-install-recommends -y $build_deps &&
mkdir -p $build &&
cd $build &&
if [ "$dch_dist" != 'trusty' ]; then
    apt-get install -y dh-systemd
fi &&
if [ "$dch_dist" == 'yakkety' -o "$dch_dist" == 'xenial' ]; then
    sed -i s'/# deb-src/deb-src/' /etc/apt/sources.list &&
    apt-get update
fi &&
apt-get source $pkg &&
ubuntu_version=$(grep Version: *.dsc| cut -d' ' -f2-| head -n1) &&
nginx_version=$(ls *.orig.tar.gz|sed 's/\.orig\.tar\.gz//'|sed 's/nginx_//g') &&
ppa_version=${ubuntu_version}ppa1 &&
git clone -b 2.2 --single-branch https://github.com/vkholodkov/nginx-upload-module.git/ \
    nginx-${nginx_version}/debian/modules/nginx-upload &&
upload_module_shortrev=$(git --git-dir=nginx-${nginx_version}/debian/modules/nginx-upload/.git rev-parse --short HEAD) &&
rm -rf nginx/debian/modules/nginx-upload/.git &&
sed -e '/^ #Removed as it no longer works with 1.3.x and above.$/d' \
    -e 's/^ #\(nginx-upload\)$/ \1/' \
    -e 's%^ #\( Homepage: https://github.com/vkholodkov/nginx-upload-module\)$% \1/tree/2.2%' \
    -e "s/^ # Version: 2.2.0.*$/  Version: 2.2.1-${upload_module_shortrev}/" \
    -i nginx-${nginx_version}/debian/modules/README.Modules-versions &&
if [ "$dch_dist" == 'trusty' ]; then
    sed -e 's#\(^\t    --add-module=$(MODULESDIR)/nginx-upload-progress \\\)#\t    --add-module=$(MODULESDIR)/nginx-upload \\\n\1#' \
    -i nginx-${nginx_version}/debian/rules
else
    sed -e 's#\(\t\t\t--add-module=$(MODULESDIR)/nginx-upload-progress \\\)#\t\t\t--add-module=$(MODULESDIR)/nginx-upload \\\n\1#' \
    -i nginx-${nginx_version}/debian/rules
fi &&
cd nginx-${nginx_version} &&
dch -v ${ppa_version} -D ${dch_dist} "${dch_message}" &&
debuild -S -sd -us -uc &&
if [ -f "$GPG_KEY" ]; then
    echo "Signing source.changes and uploading to ppa" &&
    gpg2 --import --batch "$GPG_KEY" &&
    debsign -p "gpg2 --batch" -S ${build}/${pkg}_${ppa_version}_source.changes &&
    dput -u "$PPA" $build/${pkg}_${ppa_version}_source.changes
else
    echo "To sign: debsign -S ${pkg}_${ppa_version}_source.changes" &&
    echo "To push: dput "$PPA" ${pkg}_${ppa_version}_source.changes"
fi
