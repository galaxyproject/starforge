#
# Created with debootstrap:
#
#     sudo debootstrap --arch=i386 squeeze debian6-32.dest http://carroll.aset.psu.edu/pub/linux/distributions/debian/
#     sudo tar -C debian6-32.dest -zcf debian6-32.tar.gz .
#     sudo docker build -t natefoo/debian6-32 .
#

FROM scratch
MAINTAINER Nate Coraor <nate@bx.psu.edu>
ADD debian6-32.tar.gz /
ENTRYPOINT ["/usr/bin/linux32"]
