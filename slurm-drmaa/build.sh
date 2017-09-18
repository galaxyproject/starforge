#!/bin/bash
#
# For EL, see the slurm directory. Since there are no upstream slurm packages, we
# build slurm, munge, and slurm-drmaa all in one.
#
set -e
#set -xv

pkg=slurm-drmaa

upstream_version='1.0.7'
version='1.2.0-dev.57ebc0c'
url="https://github.com/natefoo/slurm-drmaa/releases/download/${version}/slurm-drmaa-${version}.tar.gz"

builddeps='bison gperf ragel libslurm-dev libslurmdb-dev'

DEBFULLNAME="Nathan Coraor"
DEBEMAIL="nate@bx.psu.edu"
export DEBFULLNAME DEBEMAIL

build=/host/build.$(hostname)

. /etc/os-release

case $VERSION_ID in
    14.04)
        upstream_version='1.0.6'
        libvers='26'
        # later versions set this in os-release
        UBUNTU_CODENAME="trusty"
        ;;
    16.04)
        libvers='29'
        ;;
    8)
        libvers='27'
        ;;
    9)
        libvers='30'
        ;;
    *)
        echo "Don't know how to build for $NAME $VERSION ($VERSION_ID)"
        exit 1
        ;;
esac

[ "$ID" = 'ubuntu' ] && dch_dist_arg="-D $UBUNTU_CODENAME" || dch_dist_arg=''

. /util/utility_functions.sh

export DEBIAN_FRONTEND=noninteractive

gid=$(stat -c %g /host)
uid=$(stat -c %u /host)
if [ -z "$__STARFORGE_RUN_AS" -a $uid -ne 0 ]; then
    # set timezone for debian/changelog
    echo 'America/New_York' > /etc/timezone
    dpkg-reconfigure tzdata

    apt-get -qq update
    apt-get install --no-install-recommends -y $builddeps

    [ $gid -ne 0 ] && groupadd -g $gid build
    useradd -u $uid -g $gid -d $build -m -s /bin/bash build
    exec sudo -iu build __STARFORGE_RUN_AS=1 -- ${SHELL:-/bin/bash} "$0" "$@"
elif [ -z "$__STARFORGE_RUN_AS" ]; then
    mkdir $build
fi

cd $build
apt-get source $pkg
download_tarball "$url"
ln -s "slurm-drmaa-${version}.tar.gz" "slurm-drmaa_${version%-*}.orig.tar.gz"
extract_tarball "slurm-drmaa-${version}.tar.gz"
mv slurm-drmaa-${upstream_version}/debian slurm-drmaa-${version}
cd slurm-drmaa-${version}
rm -rf debian/patches
dch -v ${version} ${dch_dist_arg} "Package version ${version}"
debuild -us -uc
