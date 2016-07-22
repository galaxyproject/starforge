#!/bin/sh

if [ ! -f "/etc/galaxy" ]; then
    galaxy-config --config-dir /etc/galaxy --data-dir /var/lib/galaxy/data --wsgi-server uwsgi-http
    chown galaxy:galaxy /var/lib/galaxy/data /var/log/galaxy
fi
