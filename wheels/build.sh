#!/bin/bash

pkgvers=$1
url=$2

mkdir -p /host/$pkgvers &&
mkdir /build &&
cd /build &&
wget --no-check-certificate $url &&
tar zxf `basename $url` &&
cd $pkgvers &&
/python/2.6-ucs2/bin/python setup.py bdist_wheel &&
rm -rf build &&
/python/2.6-ucs4/bin/python setup.py bdist_wheel &&
rm -rf build &&
/python/2.7-ucs2/bin/python setup.py bdist_wheel &&
rm -rf build &&
/python/2.7-ucs4/bin/python setup.py bdist_wheel &&
mv dist/* /host/$pkgvers
