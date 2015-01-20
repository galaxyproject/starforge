FROM debian:squeeze

MAINTAINER Nate Coraor <nate@bx.psu.edu>

ENV DEBIAN_FRONTEND noninteractive

VOLUME ["/host"]

RUN apt-get -qq update && \
    apt-get install --no-install-recommends -y wget build-essential gfortran bzip2 patch

ENTRYPOINT ["/bin/sh", "/host/build.sh"]
