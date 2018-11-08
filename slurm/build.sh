#!/bin/bash
set -e
set -x

# If you are building for depot.galaxyproject.org and building a new prerelease of slurm-drmaa where the version (e.g.
# 1.2.0) has not changed, you *MUST* increment slurm_drmaa_rpm_build.

munge_version='0.5.13'
munge_src="https://github.com/dun/munge/releases/download/munge-${munge_version}/munge-${munge_version}.tar.xz"
slurm_version='17.11.9-2'
slurm_src="https://download.schedmd.com/slurm/slurm-${slurm_version}.tar.bz2"
slurm_drmaa_version='1.2.0-dev.deca826'
slurm_drmaa_rpm_version=${slurm_drmaa_version%%-*}
slurm_drmaa_rpm_build=1
slurm_drmaa_src="https://github.com/natefoo/slurm-drmaa/releases/download/${slurm_drmaa_version}/slurm-drmaa-${slurm_drmaa_version}.tar.gz"

su - build -c "mkdir -p ~/rpmbuild/SOURCES ~/rpmbuild/SPECS"
su - build -c "curl -L -o ~/rpmbuild/SOURCES/munge-${munge_version}.tar.xz $munge_src"
su - build -c "curl -L -o ~/rpmbuild/SOURCES/slurm-${slurm_version}.tar.bz2 $slurm_src"
su - build -c "curl -L -o ~/rpmbuild/SOURCES/slurm-drmaa-${slurm_drmaa_version}.tar.gz $slurm_drmaa_src"
su - build -c "tar xf ~/rpmbuild/SOURCES/munge-${munge_version}.tar.xz --strip-components=1 -C ~/rpmbuild/SPECS munge-${munge_version}/munge.spec"
su - build -c "tar jxf ~/rpmbuild/SOURCES/slurm-${slurm_version}.tar.bz2 --strip-components=1 -C ~/rpmbuild/SPECS slurm-${slurm_version}/slurm.spec"
su - build -c "tar zxf ~/rpmbuild/SOURCES/slurm-drmaa-${slurm_drmaa_version}.tar.gz --strip-components=1 -C ~/rpmbuild/SPECS slurm-drmaa-${slurm_drmaa_version}/slurm-drmaa.spec"
su - build -c "sed -i -e 's/^\(Release:\s*\)[0-9]*\(.*\)$/\1${slurm_drmaa_rpm_build}\2/' ~/rpmbuild/SPECS/slurm-drmaa.spec"

if [ $slurm_drmaa_version != $slurm_drmaa_rpm_version ]; then
    su - build -c "tar zxf ~/rpmbuild/SOURCES/slurm-drmaa-${slurm_drmaa_version}.tar.gz --transform='s#^slurm-drmaa-${slurm_drmaa_version}#slurm-drmaa-${slurm_drmaa_rpm_version}#' -C ~/rpmbuild/SOURCES"
    su - build -c "tar zcf ~/rpmbuild/SOURCES/slurm-drmaa-${slurm_drmaa_rpm_version}.tar.gz -C ~/rpmbuild/SOURCES slurm-drmaa-${slurm_drmaa_rpm_version}"
fi

yum-builddep -y ~build/rpmbuild/SPECS/munge.spec
su - build -c "rpmbuild -ba ~/rpmbuild/SPECS/munge.spec"
rpm -ivh ~build/rpmbuild/RPMS/x86_64/munge-{libs-,devel-,}${munge_version}*.rpm

yum-builddep -y ~build/rpmbuild/SPECS/slurm.spec
yum install -y mariadb-devel
su - build -c "rpmbuild -ba --with mysql ~/rpmbuild/SPECS/slurm.spec"
rpm -ivh ~build/rpmbuild/RPMS/x86_64/slurm-{example-configs-,devel-,}${slurm_version}*.rpm

yum-builddep -y ~build/rpmbuild/SPECS/slurm-drmaa.spec
cp /etc/slurm/slurm.conf.example /etc/slurm/slurm.conf
yum install -y which
su - build -c "rpmbuild -ba ~/rpmbuild/SPECS/slurm-drmaa.spec"

rsync -av ~build/rpmbuild/SRPMS /host
rsync -av ~build/rpmbuild/RPMS /host

if [ -n "${CHOWN_UID}" ]; then
    chown -Rh ${CHOWN_UID}:${CHOWN_GID:-0} /host/SRPMS /host/RPMS
fi
