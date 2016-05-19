FROM quay.io/pypa/manylinux1_x86_64:latest
MAINTAINER Nate Coraor <nate@bx.psu.edu>
VOLUME ["/host"]
#COPY buildpy.sh /build/buildpy.sh
#RUN yum install -y PKGS && \
#    cd /build && \
#    bash buildpy.sh && \
#    cd / && \
#    rm -rf /build && \
#    yum clean all

RUN yum install -y PyYAML

WORKDIR /work
ADD https://pypi.python.org/packages/source/v/virtualenv/virtualenv-15.0.1.tar.gz /work/
RUN tar zxf virtualenv-15.0.1.tar.gz
RUN /opt/python/cp27-cp27mu/bin/python ./virtualenv-15.0.1/virtualenv.py -p /opt/python/cp27-cp27mu/bin/python /opt/wheelenv
WORKDIR /
RUN rm -rf /work
RUN /opt/wheelenv/bin/pip install --index-url https://wheels.galaxyproject.org/simple starforge
# FIXME: starforge depends on "Galaxy wheel" except that for manylinux1 wheels, it doesn't
RUN /opt/wheelenv/bin/pip install --upgrade wheel
RUN rm -rf /root/.cache
RUN mkdir /python
RUN ln -s /opt/python/cp27-cp27m /python/cp27m-x86_64
RUN ln -s /opt/python/cp27-cp27mu /python/cp27mu-x86_64
