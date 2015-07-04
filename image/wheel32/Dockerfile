FROM natefoo/debian32:squeeze

MAINTAINER Nate Coraor <nate@bx.psu.edu>

ENV DEBIAN_FRONTEND noninteractive

VOLUME ["/host"]

RUN apt-key adv --keyserver pgp.mit.edu --recv-keys 8B48AD6246925553 && \
    apt-get -qq update && \
    apt-get install --no-install-recommends -y build-essential ca-certificates wget mercurial zlib1g-dev libssl-dev && \
    mkdir /build && \
    cd /build && \
    wget https://www.python.org/ftp/python/2.6.9/Python-2.6.9.tgz && \
    wget https://www.python.org/ftp/python/2.7.10/Python-2.7.10.tgz && \
    tar zxf Python-2.6.9.tgz && \
    tar zxf Python-2.7.10.tgz && \
    cd /build/Python-2.6.9 && \
    cp Modules/posixmodule.c Modules/posixmodule.c.orig && \
    sed -e 's/u.machine/"i686"/' Modules/posixmodule.c.orig >Modules/posixmodule.c && \
    ./configure --prefix=/python/2.6-ucs2 --enable-unicode=ucs2 && \
    make install && \
    make distclean && \
    ./configure --prefix=/python/2.6-ucs4 --enable-unicode=ucs4 && \
    make install && \
    cd /build/Python-2.7.10 && \
    cp Modules/posixmodule.c Modules/posixmodule.c.orig && \
    sed -e 's/u.machine/"i686"/' Modules/posixmodule.c.orig >Modules/posixmodule.c && \
    ./configure --prefix=/python/2.7-ucs2 --enable-unicode=ucs2 && \
    make install && \
    make distclean && \
    ./configure --prefix=/python/2.7-ucs4 --enable-unicode=ucs4 && \
    make install && \
    cd /build && \
    wget --no-check-certificate https://pypi.python.org/packages/source/s/setuptools/setuptools-18.0.1.tar.gz && \
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
    hg clone https://bitbucket.org/natefoo/wheel && \
    cd wheel && \
    /python/2.6-ucs2/bin/python setup.py install && \
    rm -rf build && \
    /python/2.6-ucs4/bin/python setup.py install && \
    rm -rf build && \
    /python/2.7-ucs2/bin/python setup.py install && \
    rm -rf build && \
    /python/2.7-ucs4/bin/python setup.py install && \
    cd .. && \
    rm -rf /build
