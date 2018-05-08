#!/bin/bash
set -e

singularity_version='2.5.1'
singularity_src="https://github.com/singularityware/singularity/releases/download/${singularity_version}/singularity-${singularity_version}.tar.gz"

su - build -c "mkdir -p ~/rpmbuild/SOURCES ~/rpmbuild/SPECS"
su - build -c "curl -L -o ~/rpmbuild/SOURCES/singularity-${singularity_version}.tar.gz $singularity_src"
su - build -c "tar zxf ~/rpmbuild/SOURCES/singularity-${singularity_version}.tar.gz --strip-components=1 -C ~/rpmbuild/SPECS singularity-${singularity_version}/singularity.spec"

yum-builddep -y ~build/rpmbuild/SPECS/singularity.spec
su - build -c "rpmbuild -ba ~/rpmbuild/SPECS/singularity.spec"

rsync -av ~build/rpmbuild/SRPMS /host
rsync -av ~build/rpmbuild/RPMS /host

if [ -n "${CHOWN_UID}" ]; then
    chown -Rh ${CHOWN_UID}:${CHOWN_GID:-0} /host/SRPMS /host/RPMS
fi
