#!/bin/bash
set -e

su - build -c 'git clone https://github.com/bnied/kernel-ml-aufs'
su - build -c 'cd kernel-ml-aufs/scripts && ./build_ml_kernel.sh -v=4.5 -a=x86_64 -e=7'
cp -p ~build/RPMs/* /host
