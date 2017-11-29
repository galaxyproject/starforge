#!/bin/bash
set -e

nginx_version='1.12.2'
srpm7='http://dl.fedoraproject.org/pub/epel/7/SRPMS/Packages/n/nginx-1.12.2-1.el7.src.rpm'

su - build -c "mkdir -p ~/rpmbuild/SOURCES ~/rpmbuild/SPECS"
su - build -c "cp /host/el7.spec ~/rpmbuild/SPECS/nginx.spec"
su - build -c "mkdir nginx-el7 && cd nginx-el7 && curl -L $srpm7 | rpm2cpio - | cpio -idv"
su - build -c "curl -L -o ~/rpmbuild/SOURCES/nginx-${nginx_version}.tar.gz http://nginx.org/download/nginx-${nginx_version}.tar.gz"
su - build -c "curl -L -o ~/rpmbuild/SOURCES/nginx-${nginx_version}.tar.gz.asc http://nginx.org/download/nginx-${nginx_version}.tar.gz.asc"
su - build -c "curl -L -o ~/rpmbuild/SOURCES/2.255-nfs.tar.gz https://github.com/natefoo/nginx-upload-module/archive/2.255-nfs.tar.gz"
su - build -c "curl -L -o ~/rpmbuild/SOURCES/ngx_http_auth_pam_module-1.4.tar.gz http://web.iti.upv.es/~sto/nginx/ngx_http_auth_pam_module-1.4.tar.gz"
su - build -c "cd nginx-el7 && cp nginx.logrotate nginx.conf nginx.service nginx-upgrade nginx-upgrade.8 index.html poweredby.png nginx-logo.png 404.html 50x.html nginx-auto-cc-gcc.patch README.dynamic UPGRADE-NOTES-1.6-to-1.10 ~/rpmbuild/SOURCES"

yum-builddep -y ~build/rpmbuild/SPECS/nginx.spec
su - build -c "rpmbuild -ba ~/rpmbuild/SPECS/nginx.spec"
rsync -av ~build/rpmbuild/SRPMS /host
rsync -av ~build/rpmbuild/RPMS /host
