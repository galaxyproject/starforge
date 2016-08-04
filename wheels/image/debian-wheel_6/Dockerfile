FROM debian:6
MAINTAINER Nate Coraor <nate@bx.psu.edu>

ENV DEBIAN_FRONTEND noninteractive
VOLUME ["/host"]

COPY buildpy.sh /build/buildpy.sh
COPY sources.list /etc/apt/sources.list
COPY 90ignore-release-date /etc/apt/apt.conf.d/90ignore-release-date

RUN apt-get -qq update && \
    apt-get install --no-install-recommends -y make gcc g++ ca-certificates curl zlib1g-dev libssl-dev libbz2-dev python-yaml

RUN cd /build && \
    bash buildpy.sh && \
    cd / && \
    rm -rf /build && \
    apt-get clean 
