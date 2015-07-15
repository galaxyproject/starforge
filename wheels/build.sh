#!/bin/bash

pkg=$1
url=$2
tgz=`basename $url`

case `getconf LONG_BIT` in
    32)
        plat=linux_i686
        ;;
    64)
        plat=linux_x86_64
        ;;
esac

mkdir -p /host/dist/$pkg &&
mkdir /build &&
cd /build &&
wget --no-check-certificate $url &&
dir=`tar ztf $tgz | grep / | head -1 | awk -F/ '{print $1}'` &&
tar zxf $tgz &&
cd $dir &&
if [ -f /host/prebuild/$pkg ]; then
    . /host/prebuild/$pkg
else
    true
fi &&

( for py in 2.6-ucs2 2.6-ucs4 2.7-ucs2 2.7-ucs4; do
    /python/${py}/bin/python setup.py $build_args bdist_wheel --plat-name=${plat} &&
    rm -rf build || exit 1
done ) &&
mv dist/* /host/dist/$pkg
