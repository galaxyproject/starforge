FROM quay.io/pypa/manylinux1_i686:latest
MAINTAINER Nate Coraor <nate@bx.psu.edu>

VOLUME ["/host"]

RUN /usr/bin/linux32 yum install -y PyYAML

WORKDIR /work

ADD https://pypi.python.org/packages/source/v/virtualenv/virtualenv-15.0.1.tar.gz /work/
RUN tar zxf virtualenv-15.0.1.tar.gz
RUN /usr/bin/linux32 /opt/python/cp27-cp27mu/bin/python ./virtualenv-15.0.1/virtualenv.py -p /opt/python/cp27-cp27mu/bin/python /opt/wheelenv

WORKDIR /

COPY starforge.tar.gz /work/starforge.tar.gz
RUN /usr/bin/linux32 /opt/wheelenv/bin/pip install /work/starforge.tar.gz

RUN rm -rf /work /root/.cache && \
    yum clean all

RUN mkdir /python && \
    ln -s /opt/python/cp27-cp27m /python/cp27m-i686 && \
    ln -s /opt/python/cp27-cp27mu /python/cp27mu-i686

ENTRYPOINT ["/usr/bin/linux32"]
