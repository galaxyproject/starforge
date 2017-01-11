FROM quay.io/pypa/manylinux1_x86_64:latest
MAINTAINER Nate Coraor <nate@bx.psu.edu>

VOLUME ["/host"]

RUN yum install -y PyYAML

WORKDIR /work

ADD https://pypi.python.org/packages/source/v/virtualenv/virtualenv-15.0.1.tar.gz /work/
RUN tar zxf virtualenv-15.0.1.tar.gz
RUN /opt/python/cp27-cp27mu/bin/python ./virtualenv-15.0.1/virtualenv.py -p /opt/python/cp27-cp27mu/bin/python /opt/wheelenv

WORKDIR /

COPY starforge.tar.gz /work/starforge.tar.gz
RUN /opt/wheelenv/bin/pip install /work/starforge.tar.gz

RUN rm -rf /work /root/.cache && \
    yum clean all

RUN mkdir /python && \
    ln -s /opt/python/cp27-cp27m /python/cp27m-x86_64 && \
    ln -s /opt/python/cp27-cp27mu /python/cp27mu-x86_64
