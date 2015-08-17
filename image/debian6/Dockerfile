#
# Created with debootstrap:
#
#     sudo debootstrap --arch=amd64 squeeze debian6.dest http://carroll.aset.psu.edu/pub/linux/distributions/debian/
#     sudo tar -C debian6.dest -zcf debian6.tar.gz .
#     sudo docker build -t natefoo/debian6 .
#

FROM scratch
MAINTAINER Nate Coraor <nate@bx.psu.edu>
ADD debian6.tar.gz /
ENTRYPOINT ["/usr/bin/linux32"]
