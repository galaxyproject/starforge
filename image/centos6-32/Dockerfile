#
# Created with yumbootstrap:
#
#     https://github.com/dozzie/yumbootstrap
#
# For 32-bit, it is necessary to create:
#
#     /etc/yumboostrap/suites/centos-6-32.suite
#     /etc/yumboostrap/suites/packages/centos-6-32.list
#
# In the case of centos-*.suite, replace `$basearch` with `i386`. Then:
#
#     sudo yumbootstrap --verbose --include=setarch --groups=Core centos-6-32 centos6-32.dest
#     sudo tar -C centos6-32.dest -zcf centos6-32.tar.gz .
#

FROM scratch
MAINTAINER Nate Coraor <nate@bx.psu.edu>
ADD centos6-32.tar.gz /
ENTRYPOINT ["/usr/bin/linux32"]
