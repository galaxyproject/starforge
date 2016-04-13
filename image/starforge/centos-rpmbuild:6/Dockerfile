FROM centos:6

MAINTAINER Nate Coraor <nate@bx.psu.edu>

VOLUME ["/host"]

RUN yum groupinstall -y 'development tools'
RUN yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-6.noarch.rpm
RUN yum install -y fedora-packager
RUN useradd -g mock -m -d /build -s /bin/bash build
