#!/bin/bash
#
# For EL, see the slurm directory. Since there are no upstream slurm packages, we
# build slurm, munge, and slurm-drmaa all in one.
#
# On Ubuntu we only build the source package, for uploading to a PPA.
set -e
#set -xv

pkg=slurm-drmaa

# increment $pkg_build when all dists/versions need a rebuild of the same upstream
pkg_build=1
# set/increment $series_build when just a particular dist/version needs a rebuild
#series_build=1

# upstream slurm-drmaa version
version='1.1.3'

url="https://github.com/natefoo/slurm-drmaa/releases/download/${version}/slurm-drmaa-${version}.tar.gz"

# NOTE: if this does not match debian/control, Launchpad builds will likely fail
builddeps='bison gperf ragel libslurm-dev bats'

DEBFULLNAME="Nathan Coraor"
DEBEMAIL="nate@bx.psu.edu"
export DEBFULLNAME DEBEMAIL

build=/host/build.$(hostname)

. /etc/os-release


function unsupported() {
    echo "Don't know how to build for $NAME $VERSION [$ID] ($VERSION_ID)"
    exit 1
}


case $ID in
    ubuntu)
        dch_dist_arg="--distribution $UBUNTU_CODENAME"
        debuild_args='-S'
        ;;
    debian)
        dch_dist_arg='--distribution unstable'
        ;;
    *)
        unsupported
        ;;
esac

case "$PRETTY_NAME" in
    *bullseye*)
        VERSION_ID=11
        ;;
    *bookworm*)
        VERSION_ID=12
        ;;
esac

# can be used to set any version-specific vars
case $VERSION_ID in
    20.04)
        builddeps="dh-systemd ${builddeps}"
        ;;
    11|12|22.04)
        ;;
    *)
        unsupported
        ;;
esac

. /util/utility_functions.sh

export DEBIAN_FRONTEND=noninteractive

gid=$(stat -c %g /host)
uid=$(stat -c %u /host)
if [ -z "$__STARFORGE_RUN_AS" -a $uid -ne 0 ]; then
    # set timezone for debian/changelog
    echo 'America/New_York' > /etc/timezone

    apt-get -qq update
    apt-get install --no-install-recommends -y wget tzdata sudo build-essential devscripts debhelper quilt fakeroot ca-certificates

    dpkg-reconfigure tzdata

    apt-get install --no-install-recommends -y $builddeps

    [ $gid -ne 0 ] && groupadd -g $gid build
    useradd -u $uid -g $gid -d $build -m -s /bin/bash build
    exec sudo -iu build __STARFORGE_RUN_AS=1 -- ${SHELL:-/bin/bash} "$0" "$@"
elif [ -z "$__STARFORGE_RUN_AS" ]; then
    mkdir $build
fi

case $version in
    *-dev.*)
        dch_version=${version%.*}${pkg_build}.${version/*.}
        ;;
    *)
        dch_version=${version}-${pkg_build}
        ;;
esac

# the logic for setting this isn't flawless but dput fails if the .orig.tar.gz has already been uploaded, so we can only
# use -sa once per upstream version? if this build adds the change to changelog.natefoo and the package build id is 1,
# this indicates a new upstream version and -sa will be set, otherwise -sd.
source_arg='-sd'

cd $build
download_tarball "$url"
ln -s "slurm-drmaa-${version}.tar.gz" "slurm-drmaa_${version%-*}.orig.tar.gz"
extract_tarball "slurm-drmaa-${version}.tar.gz"
cp -r $(dirname $0)/debian slurm-drmaa-${version}
cd slurm-drmaa-${version}

# use specific overrides if provided
for base in rules control; do
    override="debian/${base}.${ID}-${VERSION_ID}"
    [ -f "$override" ] && cp "${override}" "debian/${base}"
    # remove this and others so they're not included in the debian tarball
    rm -f debian/${base}.*
done

# the distribution needs to be correct in the .changes file for launchpad to build the PPA packages (but otherwise
# doesn't matter), the distribution is derived from the changelog, and we don't want to maintain a bunch of changelogs
#dch -v ${dch_version} ${dch_dist_arg} "New upstream release"
if ! grep -q "^slurm-drmaa (${dch_version})" debian/changelog.natefoo; then
    if [ $pkg_build -eq 1 ]; then
        source_arg='-sa'
        : ${DCH_MESSAGE:=New upstream release}
    else
        : ${DCH_MESSAGE:=New package build}
    fi

    cd debian
    [ ! -f changelog.natefoo ] && dch_create_args="--create --package=${pkg}"
    dch ${dch_create_args} -v ${dch_version} --distribution unstable --force-distribution --changelog changelog.natefoo "$DCH_MESSAGE"
    cd ..

    cp debian/changelog.natefoo $(dirname $0)/debian/changelog.natefoo
fi

# now create this package's changelog
case "$ID" in
    ubuntu)
        dch_version+="ubuntu${series_build:-1}~${VERSION_ID}"
        ;;
    debian)
        dch_version+="+deb${VERSION_ID}u${series_build:-1}"
        ;;
esac
cat debian/changelog.natefoo debian/changelog.${ID} > debian/changelog
dch -v "${dch_version}" $dch_dist_arg "Series package"
rm debian/changelog.*

# -S to build source package
# -sa to include source, -sd to exclude source and only include the diff
# -us to not sign source, -uc to not sign changes
debuild ${debuild_args} ${source_arg} -us -uc
echo "packages in ${pkg}/$(basename $build)"
echo "To sign: debsign -S ${pkg}_${dch_version}_source.changes" &&
echo "To push: dput ${PPA:=ppa:natefoo/slurm-drmaa-test} ${pkg}_${dch_version}_source.changes"
echo " or on Debian: dput -c ../dput.cf ${PPA:=ppa:natefoo/slurm-drmaa-test} ${pkg}_${dch_version}_source.changes"
