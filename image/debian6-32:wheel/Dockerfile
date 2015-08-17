#
# build with:
#
#     docker build -t natefoo/debian6-32:wheel
#

FROM natefoo/debian6-32:latest
MAINTAINER Nate Coraor <nate@bx.psu.edu>
ENV DEBIAN_FRONTEND noninteractive
VOLUME ["/host"]
ENTRYPOINT ["/usr/bin/linux32"]
RUN apt-key adv --keyserver pgp.mit.edu --recv-keys 8B48AD6246925553 && \
    linux32 apt-get -qq update && \
    linux32 apt-get install --no-install-recommends -y build-essential curl zlib1g-dev libssl-dev libbz2-dev python-yaml && \
    mkdir /build && \
    cd /build && \
    curl -O https://www.python.org/ftp/python/2.6.9/Python-2.6.9.tgz && \
    curl -O https://www.python.org/ftp/python/2.7.10/Python-2.7.10.tgz && \
    tar zxf Python-2.6.9.tgz && \
    tar zxf Python-2.7.10.tgz && \
    cd /build/Python-2.6.9 && \
    linux32 ./configure --prefix=/python/2.6-ucs2 --enable-unicode=ucs2 && \
    linux32 make install && \
    linux32 make distclean && \
    linux32 ./configure --prefix=/python/2.6-ucs4 --enable-unicode=ucs4 && \
    linux32 make install && \
    cd /build/Python-2.7.10 && \
    linux32 ./configure --prefix=/python/2.7-ucs2 --enable-unicode=ucs2 && \
    linux32 make install && \
    linux32 make distclean && \
    linux32 ./configure --prefix=/python/2.7-ucs4 --enable-unicode=ucs4 && \
    linux32 make install && \
    cd /build && \
    curl -O https://pypi.python.org/packages/source/s/setuptools/setuptools-18.0.1.tar.gz && \
    tar zxf setuptools-18.0.1.tar.gz && \
    cd setuptools-18.0.1 && \
    linux32 /python/2.6-ucs2/bin/python setup.py install && \
    rm -rf build && \
    linux32 /python/2.6-ucs4/bin/python setup.py install && \
    rm -rf build && \
    linux32 /python/2.7-ucs2/bin/python setup.py install && \
    rm -rf build && \
    linux32 /python/2.7-ucs4/bin/python setup.py install && \
    cd .. && \
    curl -O https://bitbucket.org/natefoo/wheel/get/2759ea9686ee.tar.gz && \
    tar zxf 2759ea9686ee.tar.gz && \
    cd natefoo-wheel-2759ea9686ee && \
    linux32 /python/2.6-ucs2/bin/python setup.py install && \
    rm -rf build && \
    linux32 /python/2.6-ucs4/bin/python setup.py install && \
    rm -rf build && \
    linux32 /python/2.7-ucs2/bin/python setup.py install && \
    rm -rf build && \
    linux32 /python/2.7-ucs4/bin/python setup.py install && \
    cd .. && \
    rm -rf /build
