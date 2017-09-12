FROM quay.io/pypa/manylinux1_i686:latest
MAINTAINER Nate Coraor <nate@bx.psu.edu>

VOLUME ["/host"]

RUN /usr/bin/linux32 yum install -y PyYAML

WORKDIR /work

ADD https://pypi.python.org/packages/d4/0c/9840c08189e030873387a73b90ada981885010dd9aea134d6de30cd24cb8/virtualenv-15.1.0.tar.gz /work/
RUN if [ ! -d "virtualenv-15.1.0" ]; then tar zxf virtualenv-15.1.0.tar.gz; fi
RUN /usr/bin/linux32 /opt/python/cp27-cp27mu/bin/python ./virtualenv-15.1.0/virtualenv.py -p /opt/python/cp27-cp27mu/bin/python /opt/wheelenv
RUN /opt/wheelenv/bin/pip install --upgrade pip setuptools

# pip is already installed in /opt/python/*

WORKDIR /

COPY starforge.tar.gz /work/starforge.tar.gz
RUN /usr/bin/linux32 /opt/wheelenv/bin/pip install /work/starforge.tar.gz

RUN rm -rf /work /root/.cache && \
    yum clean all

RUN mkdir /python && \
    ln -s /opt/python/cp27-cp27m /python/cp27m-i686 && \
    ln -s /opt/python/cp27-cp27mu /python/cp27mu-i686

ENTRYPOINT ["/usr/bin/linux32"]
