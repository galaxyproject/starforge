IMAGE_TARGETS		= debian32_6 debian32_7 ubuntu32_12.04 centos32_6
WHEEL_TARGETS		= debian-wheel_7 debian-wheel_8 debian-wheel_stretch ubuntu-wheel_14.04 ubuntu-wheel_16.04 ubuntu-wheel_16.10 centos-wheel_6 centos-wheel_7 fedora-wheel_23 fedora-wheel_22 fedora-wheel_25 opensuse-wheel-13 opensuse-wheel_42
WHEEL_TARGETS_32	= debian32-wheel_7 debian32-wheel_8 debian32-wheel_stretch ubuntu32-wheel_14.04 ubuntu32-wheel_16.04 ubuntu32-wheel_16.10 centos32-wheel_6
ALL_TARGETS		= $(IMAGE_TARGETS) $(WHEEL_TARGETS) $(WHEEL_TARGETS_32)
CLEAN_TARGETS		= $(ALL_TARGETS:=.clean)

DEBIAN_MIRROR	?= http://mirrors.mit.edu/debian/
UBUNTU_MIRROR	?= http://mirrors.mit.edu/ubuntu/


all: $(ALL_TARGETS)

clean: $(CLEAN_TARGETS)

distclean:
	sudo rm -rf $(ALL_TARGETS)

wheels: $(WHEEL_TARGETS) $(WHEEL_TARGETS_32)

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

debian-wheel_7/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#debian:7#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-debian-64.in#' \
		wheel-Makefile >$@

debian-wheel_8/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#debian:8#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-debian-multiarch.in#' \
		wheel-Makefile >$@

debian-wheel_stretch/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#debian:stretch#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-debian-multiarch.in#' \
		wheel-Makefile >$@

# Debian 32 bit

debian32-wheel_7/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#starforge/debian32:7#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-debian-32.in#' \
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

ubuntu-wheel_14.04/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#ubuntu:14.04#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-debian-multiarch.in#' \
		wheel-Makefile >$@

ubuntu-wheel_16.04/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#ubuntu:16.04#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-debian-multiarch.in#' \
		wheel-Makefile >$@

ubuntu-wheel_16.10/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#ubuntu:16.10#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-debian-multiarch.in#' \
		wheel-Makefile >$@

# Ubuntu 32 bit

# Ubuntu >= 14.04 is fully multiarch capable
ubuntu32-wheel_14.04/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-linux32.in#' \
		-e 's#REPLACE_FROM#starforge/ubuntu-wheel:14.04#' \
		wheel-Makefile >$@

ubuntu32-wheel_16.04/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-linux32.in#' \
		-e 's#REPLACE_FROM#starforge/ubuntu-wheel:16.04#' \
		wheel-Makefile >$@

ubuntu32-wheel_16.10/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-linux32.in#' \
		-e 's#REPLACE_FROM#starforge/ubuntu-wheel:16.10#' \
		wheel-Makefile >$@

# CentOS 64 bit

centos-wheel_6/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#centos:6#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-centos-64.in#' \
		wheel-Makefile >$@

centos-wheel_7/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#centos:7#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-centos-64.in#' \
		wheel-Makefile >$@

# CentOS 32 bit

centos32-wheel_6/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#starforge/centos32:6#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-centos-32.in#' \
		wheel-Makefile >$@

# Fedora

fedora-wheel_21/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#fedora:21#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-centos-64.in#' \
		wheel-Makefile >$@

fedora-wheel_22/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#fedora:22#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-centos-64.in#' \
		wheel-Makefile >$@

# openSUSE

opensuse-wheel_13/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#opensuse:harlequin#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-opensuse.in#' \
		wheel-Makefile >$@

opensuse-wheel_42/Makefile: wheel-Makefile
	mkdir -p $(@D)
	sed -e 's#REPLACE_TAG#starforge/$(subst _,:,$(@D))#' \
		-e 's#REPLACE_FROM#opensuse:leap#' \
		-e 's#REPLACE_DOCKERFILE#Dockerfile-opensuse.in#' \
		wheel-Makefile >$@

.PHONY: $(ALL_TARGETS) $(CLEAN_TARGETS) all clean distclean wheels
