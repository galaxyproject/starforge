#!/bin/bash
set -e
# to debug:
#set -xv

depotuser='depot'
depothost='orval.galaxyproject.org'
depotroot='/srv/nginx/depot.galaxyproject.org/root/starforge/wheels'
base_branch='remotes/origin/master'

if [ -z "$BUILD_NUMBER" -o -z "$WORKSPACE" ]; then
    echo '$BUILD_NUMBER is unset, are you running from Jenkins?'
    exit 1
else
    output=$(realpath -m wheels/dist/build-${BUILD_NUMBER})
fi


function build_wheel()
{
    l_wheel=$1

    [ ! -d $output ] && mkdir -p $output
    cd $output
    starforge --debug wheel --wheels-config=$WORKSPACE/wheels/build/wheels.yml --exit-on-failure $l_wheel
    echo "Contents of $output after building $l_wheel:"
    ls -l $output
}


PATH="/sbin:$PATH"  # for btrfs
tempdir=$(mktemp -d -t starforge_wheel_build_XXXXXXXX)
virtualenv $tempdir/venv
. $tempdir/venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install .

if [ -z "$1" -o "$1" = 'none' ]; then

    echo "Detecting changes to wheels.yml..."

    wheels_patch=$tempdir/wheels.yml.patch
    wheels_tmp=$tempdir/wheels.yml.tmp

    cp $WORKSPACE/wheels/build/wheels.yml $wheels_tmp
    git -C $WORKSPACE diff --color=never HEAD $base_branch -- wheels/build/wheels.yml >$wheels_patch

    if [ $(stat -c %s $wheels_patch) -ne 0 ]; then
        patch -s $wheels_tmp $wheels_patch
        build_wheels=()
        while read op wheel; do
            case "$op" in
                A|M)
                    build_wheels+=($wheel)
                    ;;
            esac
        done < <(starforge wheel_diff --wheels-config=$WORKSPACE/wheels/build/wheels.yml $wheels_tmp)
        for wheel in "${build_wheels[@]}"; do
            echo "Building '$wheel' wheel"
            build_wheel $wheel
        done
    fi

else

    for wheel in "$@"; do
        echo "Building specified wheel: $wheel"
        build_wheel $wheel
    done

fi

cd $WORKSPACE
rm -rf $tempdir

if [ -d ${output} ]; then
    sha256sum ${output}/* | tee ${output}/checksums.txt
    ssh ${depotuser}@${depothost} "mkdir -p ${depotroot}/build-${BUILD_NUMBER}"
    scp ${output}/* ${depotuser}@${depothost}:${depotroot}/build-${BUILD_NUMBER}
    ssh ${depotuser}@${depothost} "chmod 0644 ${depotroot}/build-${BUILD_NUMBER}/*"
    echo "Wheels available at: https://depot.galaxyproject.org/starforge/wheels/build-${BUILD_NUMBER}"
fi
