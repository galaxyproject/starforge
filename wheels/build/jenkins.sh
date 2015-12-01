#!/bin/bash
set -e
set -xv

wheels_patch=$(mktemp)
wheels_tmp=$(mktemp)

sfuser='jenkins'
sfbuild='mjolnir0.galaxyproject.org'
base_branch='master'
sfvenv='/home/jenkins/sfvenv'


function build_wheel()
{
    wheel=$1
    new=$2

    output=$(ssh ${sfuser}@${sfbuild} mktemp -d)
    ssh ${sfuser}@${sfbuild} "cd $output && PATH="/sbin:\$PATH" && . ${sfvenv}/bin/activate && starforge --debug wheel --wheels-config=$new $wheel"
    scp ${sfuser}@${sfbuild}:${output}/\*.whl ${sfuser}@${sfbuild}:${output}/\*.tar.gz .
}

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
