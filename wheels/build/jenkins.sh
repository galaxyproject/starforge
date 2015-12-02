#!/bin/bash
set -e
# to debug:
#set -xv

sfuser='jenkins'
sfbuild='mjolnir0.galaxyproject.org'
depotuser='depot'
depothost='orval.galaxyproject.org'
depotroot='/srv/nginx/depot.galaxyproject.org/root/starforge/wheels'
base_branch='remotes/origin/master'
sfvenv='/home/jenkins/sfvenv'

if [ -z "${BUILD_NUMBER}" ]; then
    echo '$BUILD_NUMBER is unset, are you running from Jenkins?'
    exit 1
else
    output=$(realpath wheels/dist/build-${BUILD_NUMBER})
fi


function build_wheel()
{
    wheel=$1
    new=$2

    outtmp=$(ssh ${sfuser}@${sfbuild} mktemp -d)
    ssh ${sfuser}@${sfbuild} "cd $outtmp && PATH="/sbin:\$PATH" && . ${sfvenv}/bin/activate && starforge --debug wheel --wheels-config=$new $wheel"
    [ ! -d ${output} ] && mkdir -p ${output}
    scp ${sfuser}@${sfbuild}:${outtmp}/\*.whl ${sfuser}@${sfbuild}:${outtmp}/\*.tar.gz ${output}
    echo "Contents of ${output} after building ${wheel}:"
    ls -l ${output}
}


if [ -z "$1" -o "$1" = 'none' ]; then

    echo "Detecting changes to wheels.yml..."

    wheels_patch=$(mktemp)
    wheels_tmp=$(mktemp)

    read new old < <(ssh ${sfuser}@${sfbuild} 'mktemp && mktemp' | xargs echo)

    cp wheels/build/wheels.yml $wheels_tmp
    git diff --color=never HEAD $base_branch -- wheels/build/wheels.yml >$wheels_patch

    if [ $(stat -c %s $wheels_patch) -ne 0 ]; then
        patch -s $wheels_tmp $wheels_patch
        scp -q wheels/build/wheels.yml ${sfuser}@${sfbuild}:${new}
        scp -q $wheels_tmp ${sfuser}@${sfbuild}:${old}
        while read op wheel; do
            case "$op" in
                A)
                    echo "Building new wheel $wheel"
                    build_wheel $wheel $new
                    ;;
                M)
                    echo "Rebuilding modified wheel $wheel"
                    build_wheel $wheel $new
                    ;;
            esac
        done < <(ssh ${sfuser}@${sfbuild} ${sfvenv}/bin/starforge wheel_diff --wheels-config=$new $old)
        ssh ${sfuser}@${sfbuild} "rm ${new} ${old}"
    fi

    rm ${wheels_patch} ${wheels_tmp}

else

    new=$(ssh ${sfuser}@${sfbuild} mktemp)
    scp -q wheels/build/wheels.yml ${sfuser}@${sfbuild}:${new}

    for wheel in "$@"; do
        echo "Building specified wheel: ${wheel}"
        build_wheel $wheel $new
    done

    ssh ${sfuser}@${sfbuild} "rm ${new}"

fi

if [ -d ${output} ]; then
    ssh ${depotuser}@${depothost} "mkdir -p ${depotroot}/build-${BUILD_NUMBER}"
    scp ${output}/* ${depotuser}@${depothost}:${depotroot}/build-${BUILD_NUMBER}
    ssh ${depotuser}@${depothost} "chmod 0644 ${depotroot}/build-${BUILD_NUMBER}/\*"
fi
