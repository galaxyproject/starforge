#!/bin/bash
set -e

munge_version='0.5.12'
munge_src="https://github.com/dun/munge/releases/download/munge-${munge_version}/munge-${munge_version}.tar.xz"
slurm_version='17.02.3'
slurm_src="https://www.schedmd.com/downloads/latest/slurm-${slurm_version}.tar.bz2"

su - build -c "mkdir -p ~/rpmbuild/SOURCES ~/rpmbuild/SPECS"
su - build -c "curl -L -o ~/rpmbuild/SOURCES/munge-${munge_version}.tar.xz $munge_src"
su - build -c "curl -L -o ~/rpmbuild/SOURCES/slurm-${slurm_version}.tar.bz2 $slurm_src"
su - build -c "tar xf ~/rpmbuild/SOURCES/munge-${munge_version}.tar.xz --strip-components=1 -C ~/rpmbuild/SPECS munge-${munge_version}/munge.spec"
su - build -c "tar jxf ~/rpmbuild/SOURCES/slurm-${slurm_version}.tar.bz2 --strip-components=1 -C ~/rpmbuild/SPECS slurm-${slurm_version}/slurm.spec"

yum-builddep -y ~build/rpmbuild/SPECS/munge.spec
su - build -c "rpmbuild -ba ~/rpmbuild/SPECS/munge.spec"
rpm -ivh ~build/rpmbuild/RPMS/x86_64/munge-{libs-,devel-,}${munge_version}*.rpm

yum-builddep -y ~build/rpmbuild/SPECS/slurm.spec
yum install -y mariadb-devel
su - build -c "rpmbuild -ba --with mysql ~/rpmbuild/SPECS/slurm.spec"
rsync -av ~build/rpmbuild/SRPMS /host
rsync -av ~build/rpmbuild/RPMS /host

if [ -n "${CHOWN_UID}" ]; then
    chown -Rh ${CHOWN_UID}:${CHOWN_GID:-0} /host/SRPMS /host/RPMS
fi
