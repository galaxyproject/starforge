BASE_TAGS	= debian6 debian7 debian8 debian9 ubuntu12.04 ubuntu14.04 centos6 centos7 opensuse13
BASE_TAGS_32	= $(BASE_TAGS:=-32)
WHEEL_TAGS 	= $(BASE_TAGS:=-wheel)
WHEEL_TAGS_32 	= $(WHEEL_TAGS:=-32)
ALL_TAGS	= $(BASE_TAGS) $(BASE_TAGS_32) $(WHEEL_TAGS) $(WHEEL_TAGS_32)
CLEAN_TAGS	= $(ALL_TAGS:=.clean)

DEBIAN_MIRROR	?= http://carroll.aset.psu.edu/pub/linux/distributions/debian/
UBUNTU_MIRROR	?= http://carroll.aset.psu.edu/pub/linux/distributions/ubuntu/

DEBIAN_PKGS	= build-essential ca-certificates curl zlib1g-dev libssl-dev libbz2-dev python-yaml
DEBIAN_RUN	= apt-key adv --keyserver pgp.mit.edu --recv-keys 8B48AD6246925553 \\\&\\\& apt-get -qq update \\\&\\\& apt-get install --no-install-recommends -y $(DEBIAN_PKGS)
DEBIAN_RUN_32	= apt-key adv --keyserver pgp.mit.edu --recv-keys 8B48AD6246925553 \\\&\\\& linux32 apt-get -qq update \\\&\\\& apt-get install --no-install-recommends -y $(DEBIAN_PKGS)
CENTOS_PKGS	= curl zlib-devel openssl-devel bzip2-devel PyYAML
CENTOS_RUN	= yum groupinstall -y "Development Tools" \\\&\\\& yum install -y $(CENTOS_PKGS)
CENTOS_RUN_32	= linux32 yum groupinstall -y "Development Tools" \\\&\\\& linux32 yum install -y $(CENTOS_PKGS)
OPENSUSE_PKGS	= python tar gcc gcc-c++ make glibc-devel ca-certificates-mozilla curl zlib-devel libopenssl-devel libbz2-devel python-PyYAML
OPENSUSE_RUN	= zypper --non-interactive --gpg-auto-import-keys ref \\\&\\\& zypper --non-interactive in $(OPENSUSE_PKGS)
WHEEL_VERSION	= 3f496bdf2708

all: $(BASE_TAGS) $(BASE_TAGS_32) $(WHEEL_TAGS) $(WHEEL_TAGS_32)

clean: $(CLEAN_TAGS)

distclean:
	sudo rm -rf $(ALL_TAGS)

$(ALL_TAGS): %: %/Makefile
	$(MAKE) -C $@ image-id

$(CLEAN_TAGS):
	$(MAKE) -C $(basename $@) clean

debian6/Makefile: image-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_DIST#debian#' \
		-e 's#REPLACE_BITS#64#' \
		-e 's#REPLACE_ARCH#amd64#' \
		-e 's#REPLACE_RELEASE#squeeze#' \
		-e 's#REPLACE_URL#$(DEBIAN_MIRROR)#' image-Makefile >$@

debian6-32/Makefile: image-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_DIST#debian#' \
		-e 's#REPLACE_BITS#32#' \
		-e 's#REPLACE_ARCH#i386#' \
		-e 's#REPLACE_RELEASE#squeeze#' \
		-e 's#REPLACE_URL#$(DEBIAN_MIRROR)' image-Makefile >$@

debian7/Makefile: image-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_DIST#debian#' \
		-e 's#REPLACE_BITS#64#' \
		-e 's#REPLACE_ARCH#amd64#' \
		-e 's#REPLACE_RELEASE#wheezy#' \
		-e 's#REPLACE_URL#$(DEBIAN_MIRROR)' image-Makefile >$@

debian7-32/Makefile: image-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_DIST#debian#' \
		-e 's#REPLACE_BITS#32#' \
		-e 's#REPLACE_ARCH#i386#' \
		-e 's#REPLACE_RELEASE#wheezy#' \
		-e 's#REPLACE_URL#$(DEBIAN_MIRROR)' image-Makefile >$@

debian8/Makefile: image-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_DIST#debian#' \
		-e 's#REPLACE_BITS#64#' \
		-e 's#REPLACE_ARCH#amd64#' \
		-e 's#REPLACE_RELEASE#jessie#' \
		-e 's#REPLACE_URL#$(DEBIAN_MIRROR)' image-Makefile >$@

debian8-32/Makefile: image-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_DIST#debian#' \
		-e 's#REPLACE_BITS#32#' \
		-e 's#REPLACE_ARCH#i386#' \
		-e 's#REPLACE_RELEASE#jessie#' \
		-e 's#REPLACE_URL#$(DEBIAN_MIRROR)' image-Makefile >$@

debian9/Makefile: image-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_DIST#debian#' \
		-e 's#REPLACE_BITS#64#' \
		-e 's#REPLACE_ARCH#amd64#' \
		-e 's#REPLACE_RELEASE#stretch#' \
		-e 's#REPLACE_URL#$(DEBIAN_MIRROR)' image-Makefile >$@

debian9-32/Makefile: image-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_DIST#debian#' \
		-e 's#REPLACE_BITS#32#' \
		-e 's#REPLACE_ARCH#i386#' \
		-e 's#REPLACE_RELEASE#stretch#' \
		-e 's#REPLACE_URL#$(DEBIAN_MIRROR)' image-Makefile >$@

ubuntu12.04/Makefile: image-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_DIST#debian#' \
		-e 's#REPLACE_BITS#64#' \
		-e 's#REPLACE_ARCH#amd64#' \
		-e 's#REPLACE_RELEASE#precise#' \
		-e 's#REPLACE_URL#$(UBUNTU_MIRROR)' image-Makefile >$@

ubuntu12.04-32/Makefile: image-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_DIST#debian#' \
		-e 's#REPLACE_BITS#32#' \
		-e 's#REPLACE_ARCH#i386#' \
		-e 's#REPLACE_RELEASE#precise#' \
		-e 's#REPLACE_URL#$(UBUNTU_MIRROR)' image-Makefile >$@

ubuntu14.04/Makefile: image-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_DIST#debian#' \
		-e 's#REPLACE_BITS#64#' \
		-e 's#REPLACE_ARCH#amd64#' \
		-e 's#REPLACE_RELEASE#trusty#' \
		-e 's#REPLACE_URL#$(UBUNTU_MIRROR)' image-Makefile >$@

ubuntu14.04-32/Makefile: image-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_DIST#debian#' \
		-e 's#REPLACE_BITS#32#' \
		-e 's#REPLACE_ARCH#i386#' \
		-e 's#REPLACE_RELEASE#trusty#' \
		-e 's#REPLACE_URL#$(UBUNTU_MIRROR)' image-Makefile >$@

centos6/Makefile: image-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_DIST#centos#' \
		-e 's#REPLACE_BITS#64#' \
		-e 's#REPLACE_ARCH#amd64#' \
		-e 's#REPLACE_VERSION#6#' \
		-e 's#REPLACE_DASHBITS##' image-Makefile >$@

centos6-32/Makefile: image-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_DIST#centos#' \
		-e 's#REPLACE_BITS#32#' \
		-e 's#REPLACE_ARCH#i386#' \
		-e 's#REPLACE_VERSION#6#' \
		-e 's#REPLACE_DASHBITS#-32#' image-Makefile >$@

centos7/Makefile: image-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_DIST#centos#' \
		-e 's#REPLACE_BITS#64#' \
		-e 's#REPLACE_ARCH#amd64#' \
		-e 's#REPLACE_VERSION#7#' \
		-e 's#REPLACE_DASHBITS##' image-Makefile >$@

debian6-wheel/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_FROM#natefoo/debian6:latest#' \
		-e 's#REPLACE_BITS#64#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_RUN#$(DEBIAN_RUN)#' wheel-Makefile >$@

debian6-wheel-32/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_FROM#natefoo/debian6-32:latest#' \
		-e 's#REPLACE_BITS#32#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_RUN#$(DEBIAN_RUN_32)#' wheel-Makefile >$@

debian7-wheel/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_FROM#natefoo/debian7:latest#' \
		-e 's#REPLACE_BITS#64#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_RUN#$(DEBIAN_RUN)#' wheel-Makefile >$@

debian7-wheel-32/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_FROM#natefoo/debian7-32:latest#' \
		-e 's#REPLACE_BITS#32#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_RUN#$(DEBIAN_RUN_32)#' wheel-Makefile >$@

debian8-wheel/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_FROM#natefoo/debian8:latest#' \
		-e 's#REPLACE_BITS#64#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_RUN#$(DEBIAN_RUN)#' wheel-Makefile >$@

debian8-wheel-32/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_FROM#natefoo/debian8-32:latest#' \
		-e 's#REPLACE_BITS#32#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_RUN#$(DEBIAN_RUN_32)#' wheel-Makefile >$@

debian9-wheel/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_FROM#natefoo/debian9:latest#' \
		-e 's#REPLACE_BITS#64#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_RUN#$(DEBIAN_RUN)#' wheel-Makefile >$@

debian9-wheel-32/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_FROM#natefoo/debian9-32:latest#' \
		-e 's#REPLACE_BITS#32#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_RUN#$(DEBIAN_RUN_32)#' wheel-Makefile >$@

ubuntu12.04-wheel/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_FROM#natefoo/ubuntu12.04:latest#' \
		-e 's#REPLACE_BITS#64#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_RUN#$(DEBIAN_RUN)#' wheel-Makefile >$@

ubuntu12.04-wheel-32/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_FROM#natefoo/ubuntu12.04-32:latest#' \
		-e 's#REPLACE_BITS#32#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_RUN#$(DEBIAN_RUN_32)#' wheel-Makefile >$@

ubuntu14.04-wheel/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_FROM#natefoo/ubuntu14.04:latest#' \
		-e 's#REPLACE_BITS#64#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_RUN#$(DEBIAN_RUN)#' wheel-Makefile >$@

ubuntu14.04-wheel-32/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_FROM#natefoo/ubuntu14.04-32:latest#' \
		-e 's#REPLACE_BITS#32#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_RUN#$(DEBIAN_RUN_32)#' wheel-Makefile >$@

centos6-wheel/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_FROM#natefoo/centos6:latest#' \
		-e 's#REPLACE_BITS#64#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_RUN#$(CENTOS_RUN)#' wheel-Makefile >$@

centos6-wheel-32/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_FROM#natefoo/centos6-32:latest#' \
		-e 's#REPLACE_BITS#32#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_RUN#$(CENTOS_RUN_32)#' wheel-Makefile >$@

centos7-wheel/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_FROM#natefoo/centos7:latest#' \
		-e 's#REPLACE_BITS#64#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_RUN#$(CENTOS_RUN)#' wheel-Makefile >$@

opensuse13-wheel/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#natefoo/$(@D)#' \
		-e 's#REPLACE_FROM#opensuse:13.2#' \
		-e 's#REPLACE_BITS#64#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_RUN#$(OPENSUSE_RUN)#' wheel-Makefile >$@

.PHONY: $(BASE_TAGS) $(BASE_TAGS_32) $(WHEEL_TAGS) $(WHEEL_TAGS_32) all clean distclean
