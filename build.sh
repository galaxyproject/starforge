#!/bin/bash
set -e

usage="usage: $(basename $0) <galaxy|ubuntu[:tag]|debian[:tag]> <PACKAGE>"

[ -z "$2" ] && echo "$usage" && exit 2

repo_arr=(${1//:/ })
case ${#repo_arr[@]} in
    1)
        repo=$1
        tag=latest
        ;;
    2)
        repo=${repo_arr[0]}
        tag=${repo_arr[1]}
        ;;
    3)
        echo "$usage"
        exit 2
        ;;
esac


case "$repo" in
    galaxy)
        baseimg='debian:squeeze'
        build_image_repository='natefoo/galaxy_build'
        buildpkgs='gfortran bzip2 patch'
        ;;
    ubuntu|debian)
        baseimg="$1"
        build_image_repository="natefoo/${repo}_build"
        buildpkgs='devscripts debhelper socat quilt fakeroot ca-certificates dh-systemd'
        ;;
    starforge/*)
        docker_args='--cap-add=SYS_ADMIN'
        build_image_repository="$repo"
        ;;
    *)
        echo "$usage"
        exit 2
        ;;
esac

[ ! -d "$2" ] && echo "$2: not found" && exit 1

for image_id in $(docker images -q $build_image_repository); do
    for image_tag in $(docker images | awk "\$1 == \"$build_image_repository\" {print \$2}"); do
        if [ "$tag" == "$image_tag" ]; then
            build_image_id=$image_id
        fi
    done
done

[ "$tag" != "latest" ] && build_image_repository="$build_image_repository:$tag"

if [ -z "$build_image_id" ]; then
    case "$build_image_repository" in
        starforge/*)
            docker build -t "$build_image_repository" ./image/$1
            ;;
        *)
            sed -e "s/BASE_NAME_AND_TAG/$baseimg/" -e "s/ADDITIONAL_BUILD_PACKAGES/$buildpkgs/" ./image/Dockerfile.in >./image/Dockerfile &&
            docker build -t "$build_image_repository" ./image
            ;;
    esac
fi

base=$(readlink -f $2)

runcmd="docker run $docker_args --rm --volume=$base/:/host/ --volume=`pwd`/util/:/util/ $build_image_repository"
echo "$runcmd $@"
$runcmd $@
