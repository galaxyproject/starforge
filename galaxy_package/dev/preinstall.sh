#!/bin/sh

if ! id -u galaxy >/dev/null 2>&1; then
    useradd -c 'Galaxy Server' -d /var/lib/galaxy -m -r -s /bin/bash galaxy
fi
