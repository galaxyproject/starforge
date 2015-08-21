#!/bin/bash
#
# quick hack to update the version of my wheel modifications in the wheel images
#

wheel_version='35e48cf7c4af'

images="
debian6-wheel
debian7-wheel
debian8-wheel
debian9-wheel
ubuntu12.04-wheel
centos6-wheel
centos7-wheel
debian6-wheel-32
debian7-wheel-32
debian8-wheel-32
debian9-wheel-32
centos6-wheel-32
"
#ubuntu14.04-wheel
#ubuntu12.04-wheel-32
#ubuntu14.04-wheel-32

for image in $images; do
    echo $image
    if [[ $image == *"-32" ]]; then
        linux32='linux32'
    else
        linux32=
    fi
    docker run --name="${image}-update" natefoo/$image sh -c "mkdir /build && cd /build && curl -O https://bitbucket.org/natefoo/wheel/get/${wheel_version}.tar.gz && tar zxf ${wheel_version}.tar.gz && cd natefoo-wheel-${wheel_version} && $linux32 /python/2.6-ucs2/bin/python setup.py install && rm -rf build && $linux32 /python/2.6-ucs4/bin/python setup.py install && rm -rf build && $linux32 /python/2.7-ucs2/bin/python setup.py install && rm -rf build && $linux32 /python/2.7-ucs4/bin/python setup.py install && cd .. && rm -rf /build"
    docker commit ${image}-update natefoo/$image
    docker rm -v ${image}-update
done
