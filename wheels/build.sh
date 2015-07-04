#!/bin/bash

pkgvers=$1
url=$2

case `getconf LONG_BIT` in
    32)
        plat=linux_i686
        ;;
    64)
        plat=linux_x86_64
        ;;
esac

mkdir -p /host/$pkgvers &&
mkdir /build &&
cd /build &&
wget --no-check-certificate $url &&
tar zxf `basename $url` &&
cd $pkgvers &&
/python/2.6-ucs2/bin/python setup.py bdist_wheel --plat-name=${plat} &&
rm -rf build &&
/python/2.6-ucs4/bin/python setup.py bdist_wheel --plat-name=${plat} &&
rm -rf build &&
/python/2.7-ucs2/bin/python setup.py bdist_wheel --plat-name=${plat} &&
rm -rf build &&
/python/2.7-ucs4/bin/python setup.py bdist_wheel --plat-name=${plat} &&
mv dist/* /host/$pkgvers
