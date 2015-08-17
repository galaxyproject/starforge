#
# build with:
#
#     docker build -t natefoo/debian6:wheel
#

FROM natefoo/debian6:latest
MAINTAINER Nate Coraor <nate@bx.psu.edu>
ENV DEBIAN_FRONTEND noninteractive
VOLUME ["/host"]
RUN apt-key adv --keyserver pgp.mit.edu --recv-keys 8B48AD6246925553 && \
    apt-get -qq update && \
    apt-get install --no-install-recommends -y build-essential curl zlib1g-dev libssl-dev libbz2-dev python-yaml && \
    mkdir /build && \
    cd /build && \
    curl -O https://www.python.org/ftp/python/2.6.9/Python-2.6.9.tgz && \
    curl -O https://www.python.org/ftp/python/2.7.10/Python-2.7.10.tgz && \
    tar zxf Python-2.6.9.tgz && \
    tar zxf Python-2.7.10.tgz && \
    cd /build/Python-2.6.9 && \
    ./configure --prefix=/python/2.6-ucs2 --enable-unicode=ucs2 && \
    make install && \
    make distclean && \
    ./configure --prefix=/python/2.6-ucs4 --enable-unicode=ucs4 && \
    make install && \
    cd /build/Python-2.7.10 && \
    ./configure --prefix=/python/2.7-ucs2 --enable-unicode=ucs2 && \
    make install && \
    make distclean && \
    ./configure --prefix=/python/2.7-ucs4 --enable-unicode=ucs4 && \
    make install && \
    cd /build && \
    curl -O https://pypi.python.org/packages/source/s/setuptools/setuptools-18.0.1.tar.gz && \
    tar zxf setuptools-18.0.1.tar.gz && \
    cd setuptools-18.0.1 && \
    /python/2.6-ucs2/bin/python setup.py install && \
    rm -rf build && \
    /python/2.6-ucs4/bin/python setup.py install && \
    rm -rf build && \
    /python/2.7-ucs2/bin/python setup.py install && \
    rm -rf build && \
    /python/2.7-ucs4/bin/python setup.py install && \
    cd .. && \
    curl -O https://bitbucket.org/natefoo/wheel/get/2759ea9686ee.tar.gz && \
    tar zxf 2759ea9686ee.tar.gz && \
    cd natefoo-wheel-2759ea9686ee && \
    /python/2.6-ucs2/bin/python setup.py install && \
    rm -rf build && \
    /python/2.6-ucs4/bin/python setup.py install && \
    rm -rf build && \
    /python/2.7-ucs2/bin/python setup.py install && \
    rm -rf build && \
    /python/2.7-ucs4/bin/python setup.py install && \
    cd .. && \
    rm -rf /build
