IMAGE_TARGETS		= debian32_6 debian32_7 ubuntu32_12.04 centos32_6
WHEEL_TARGETS		= debian-wheel_6 debian-wheel_7 debian-wheel_8 debian-wheel_stretch ubuntu-wheel_12.04 ubuntu-wheel_14.04 ubuntu-wheel_15.04 ubuntu-wheel_15.10 centos-wheel_6 centos-wheel_7 opensuse-wheel_13 fedora-wheel_21 fedora-wheel_22
WHEEL_TARGETS_32	= debian32-wheel_6 debian32-wheel_7 debian32-wheel_8 debian32-wheel_stretch ubuntu32-wheel_12.04 ubuntu32-wheel_14.04 ubuntu32-wheel_15.04 ubuntu32-wheel_15.10 centos32-wheel_6
ALL_TARGETS		= $(IMAGE_TARGETS) $(WHEEL_TARGETS) $(WHEEL_TARGETS_32)
CLEAN_TARGETS		= $(ALL_TARGETS:=.clean)

DEBIAN_MIRROR	?= http://mirrors.mit.edu/debian/
UBUNTU_MIRROR	?= http://mirrors.mit.edu/ubuntu/

DEBIAN_PKGS	= make gcc g++ ca-certificates curl zlib1g-dev libssl-dev libbz2-dev python-yaml
CENTOS_PKGS	= findutils python tar make gcc gcc-c++ curl zlib-devel openssl-devel bzip2-devel PyYAML
OPENSUSE_PKGS	= python tar make gcc gcc-c++ glibc-devel ca-certificates-mozilla curl zlib-devel libopenssl-devel libbz2-devel python-PyYAML

WHEEL_VERSION	= 3f496bdf2708
PIP_VERSION	= 8.0.0.dev0+gx1

all: $(ALL_TARGETS)

clean: $(CLEAN_TARGETS)

distclean:
	sudo rm -rf $(ALL_TARGETS)

$(ALL_TARGETS): %: %/Makefile
	$(MAKE) -C $@ image-id

$(CLEAN_TARGETS):
	$(MAKE) -C $(basename $@) clean

## 32 bit base images

debian32_6/Makefile: image-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_DIST#debian#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-baseimage-32.in#' \
		-e 's#REPLACE_RELEASE#squeeze#' \
		-e 's#REPLACE_URL#$(DEBIAN_MIRROR)#' \
		image-Makefile >$@

debian32_7/Makefile: image-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_DIST#debian#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-baseimage-32.in#' \
		-e 's#REPLACE_RELEASE#wheezy#' \
		-e 's#REPLACE_URL#$(DEBIAN_MIRROR)#' \
		image-Makefile >$@

ubuntu32_12.04/Makefile: image-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_DIST#debian#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-baseimage-32.in#' \
		-e 's#REPLACE_RELEASE#precise#' \
		-e 's#REPLACE_URL#$(UBUNTU_MIRROR)#' \
		image-Makefile >$@

centos32_6/Makefile: image-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_DIST#centos#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-baseimage-32.in#' \
		image-Makefile >$@

## Wheel images

# Debian 64 bit

debian-wheel_6/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#debian:6#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-debian-64.in#' \
		-e 's#REPLACE_PKGS#$(DEBIAN_PKGS)#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_PIP_VERSION#$(PIP_VERSION)#' \
		wheel-Makefile >$@

debian-wheel_7/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#debian:7#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-debian-64.in#' \
		-e 's#REPLACE_PKGS#$(DEBIAN_PKGS)#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_PIP_VERSION#$(PIP_VERSION)#' \
		wheel-Makefile >$@

debian-wheel_8/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#debian:8#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-debian-multiarch.in#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_PIP_VERSION#$(PIP_VERSION)#' \
		wheel-Makefile >$@

debian-wheel_stretch/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#debian:stretch#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-debian-multiarch.in#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_PIP_VERSION#$(PIP_VERSION)#' \
		wheel-Makefile >$@

# Debian 32 bit

debian32-wheel_6/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#starforge/debian32:6#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-debian-32.in#' \
		-e 's#REPLACE_PKGS#$(DEBIAN_PKGS)#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_PIP_VERSION#$(PIP_VERSION)#' \
		wheel-Makefile >$@

debian32-wheel_7/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#starforge/debian32:7#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-debian-32.in#' \
		-e 's#REPLACE_PKGS#$(DEBIAN_PKGS)#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_PIP_VERSION#$(PIP_VERSION)#' \
		wheel-Makefile >$@

# Debian >= 8 is fully multiarch capable, so the "32 bit" image is built from
# the 64 bit image (sets linux32 as the entrypoint)
debian32-wheel_8/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#starforge/debian-wheel:8#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-linux32.in#' \
		wheel-Makefile >$@

debian32-wheel_stretch/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#starforge/debian-wheel:stretch#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-linux32.in#' \
		wheel-Makefile >$@

# Ubuntu 64 bit

ubuntu-wheel_12.04/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#ubuntu:12.04#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-debian-64.in#' \
		-e 's#REPLACE_PKGS#$(DEBIAN_PKGS)#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_PIP_VERSION#$(PIP_VERSION)#' \
		wheel-Makefile >$@

ubuntu-wheel_14.04/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#ubuntu:14.04#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-debian-multiarch.in#' \
		-e 's#REPLACE_PKGS#$(DEBIAN_PKGS)#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_PIP_VERSION#$(PIP_VERSION)#' \
		wheel-Makefile >$@

ubuntu-wheel_15.04/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#ubuntu:15.04#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-debian-multiarch.in#' \
		-e 's#REPLACE_PKGS#$(DEBIAN_PKGS)#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_PIP_VERSION#$(PIP_VERSION)#' \
		wheel-Makefile >$@

ubuntu-wheel_15.10/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#ubuntu:15.10#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-debian-multiarch.in#' \
		-e 's#REPLACE_PKGS#$(DEBIAN_PKGS)#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_PIP_VERSION#$(PIP_VERSION)#' \
		wheel-Makefile >$@

# Ubuntu 32 bit

ubuntu32-wheel_12.04/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#starforge/ubuntu32:12.04#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-debian-32.in#' \
		-e 's#REPLACE_PKGS#$(DEBIAN_PKGS)#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_PIP_VERSION#$(PIP_VERSION)#' \
		wheel-Makefile >$@

# Ubuntu >= 14.04 is fully multiarch capable
ubuntu32-wheel_14.04/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-linux32.in#' \
		-e 's#REPLACE_FROM#starforge/ubuntu-wheel:14.04#' \
		wheel-Makefile >$@

ubuntu32-wheel_15.04/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-linux32.in#' \
		-e 's#REPLACE_FROM#starforge/ubuntu-wheel:15.04#' \
		wheel-Makefile >$@

ubuntu32-wheel_15.10/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-linux32.in#' \
		-e 's#REPLACE_FROM#starforge/ubuntu-wheel:15.10#' \
		wheel-Makefile >$@

# CentOS 64 bit

centos-wheel_6/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#centos:6#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-centos-64.in#' \
		-e 's#REPLACE_PKGS#$(CENTOS_PKGS)#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_PIP_VERSION#$(PIP_VERSION)#' \
		wheel-Makefile >$@

centos-wheel_7/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#centos:7#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-centos-64.in#' \
		-e 's#REPLACE_PKGS#$(CENTOS_PKGS)#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_PIP_VERSION#$(PIP_VERSION)#' \
		wheel-Makefile >$@

# CentOS 32 bit

centos32-wheel_6/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#starforge/centos32:6#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-centos-32.in#' \
		-e 's#REPLACE_PKGS#$(CENTOS_PKGS)#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_PIP_VERSION#$(PIP_VERSION)#' \
		wheel-Makefile >$@

# openSUSE

opensuse-wheel_13/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#opensuse:13.2#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-opensuse.in#' \
		-e 's#REPLACE_PKGS#$(OPENSUSE_PKGS)#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_PIP_VERSION#$(PIP_VERSION)#' \
		wheel-Makefile >$@

# Fedora

fedora-wheel_21/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#fedora:21#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-centos-64.in#' \
		-e 's#REPLACE_PKGS#$(CENTOS_PKGS)#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_PIP_VERSION#$(PIP_VERSION)#' \
		wheel-Makefile >$@

fedora-wheel_22/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#fedora:22#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-centos-64.in#' \
		-e 's#REPLACE_PKGS#$(CENTOS_PKGS)#' \
		-e 's#REPLACE_WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#REPLACE_PIP_VERSION#$(PIP_VERSION)#' \
		wheel-Makefile >$@

.PHONY: $(ALL_TARGETS) $(CLEAN_TARGETS) all clean distclean
