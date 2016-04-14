#!/bin/bash
set -e

nginx_version='1.8.1'
srpm6='https://dl.fedoraproject.org/pub/epel/6/SRPMS/nginx-1.0.15-12.el6.src.rpm'
srpm7='https://dl.fedoraproject.org/pub/epel/7/SRPMS/n/nginx-1.6.3-8.el7.src.rpm'

su - build -c "mkdir -p ~/rpmbuild/SOURCES ~/rpmbuild/SPECS"
su - build -c "cp /host/el6.spec ~/rpmbuild/SPECS/nginx.spec"
su - build -c "mkdir nginx-el6 && cd nginx-el6 && curl -L $srpm6 | rpm2cpio - | cpio -idv"
su - build -c "mkdir nginx-el7 && cd nginx-el7 && curl -L $srpm7 | rpm2cpio - | cpio -idv"
su - build -c "curl -L -o ~/rpmbuild/SOURCES/nginx-1.8.1.tar.gz http://nginx.org/download/nginx-${nginx_version}.tar.gz"
su - build -c "curl -L -o ~/rpmbuild/SOURCES/nginx-1.8.1.tar.gz.asc http://nginx.org/download/nginx-${nginx_version}.tar.gz.asc"
su - build -c "curl -L -o ~/rpmbuild/SOURCES/2.2.tar.gz https://github.com/vkholodkov/nginx-upload-module/archive/2.2.tar.gz"
su - build -c "curl -L -o ~/rpmbuild/SOURCES/ngx_http_auth_pam_module-1.4.tar.gz http://web.iti.upv.es/~sto/nginx/ngx_http_auth_pam_module-1.4.tar.gz"
su - build -c "cd nginx-el6 && cp nginx.init nginx.sysconfig ~/rpmbuild/SOURCES"
su - build -c "cd nginx-el7 && cp nginx.logrotate nginx.conf nginx-upgrade nginx-upgrade.8 index.html poweredby.png nginx-logo.png 404.html 50x.html nginx-auto-cc-gcc.patch ~/rpmbuild/SOURCES"

yum-builddep -y ~build/rpmbuild/SPECS/nginx.spec
su - build -c "rpmbuild -ba ~/rpmbuild/SPECS/nginx.spec"
rsync -av ~build/rpmbuild/SRPMS /host
rsync -av ~build/rpmbuild/RPMS /host
