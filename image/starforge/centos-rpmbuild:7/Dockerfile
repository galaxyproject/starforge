FROM centos:7

MAINTAINER Nate Coraor <nate@bx.psu.edu>

VOLUME ["/host"]

RUN yum groupinstall -y 'development tools'
RUN yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
RUN yum install -y fedora-packager
RUN useradd -g mock -m -d /home/build -s /bin/bash build

ENTRYPOINT ["/bin/bash", "/host/build.sh"]
