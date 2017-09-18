FROM quay.io/pypa/manylinux1_x86_64:latest
MAINTAINER Nate Coraor <nate@bx.psu.edu>

VOLUME ["/host"]

RUN yum install -y PyYAML xz-devel

WORKDIR /work

ADD https://pypi.python.org/packages/d4/0c/9840c08189e030873387a73b90ada981885010dd9aea134d6de30cd24cb8/virtualenv-15.1.0.tar.gz /work/
RUN if [ ! -d "virtualenv-15.1.0" ]; then tar zxf virtualenv-15.1.0.tar.gz; fi
RUN /opt/python/cp27-cp27mu/bin/python ./virtualenv-15.1.0/virtualenv.py -p /opt/python/cp27-cp27mu/bin/python /opt/wheelenv
RUN /opt/wheelenv/bin/pip install --upgrade pip setuptools

# pip is already installed in /opt/python/*

WORKDIR /

COPY starforge.tar.gz /work/starforge.tar.gz
RUN /opt/wheelenv/bin/pip install /work/starforge.tar.gz[lzma]

RUN rm -rf /work /root/.cache && \
    yum clean all

RUN mkdir /python && \
    ln -s /opt/python/cp27-cp27m /python/cp27m-x86_64 && \
    ln -s /opt/python/cp27-cp27mu /python/cp27mu-x86_64
