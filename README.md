# Build things in docker

Mostly for [Galaxy Tool Shed](https://toolshed.g2.bx.psu.edu) dependencies, although I'd like to use this for rebuilding debian source packages a la [vadebuildsible](https://github.com/natefoo/vadebuildsible), the [Galaxy rebuild of nginx-extras](https://launchpad.net/~galaxyproject/+archive/ubuntu/nginx), the rpms of nginx for usegalaxy.org, and so forth.

The base image for Galaxy packages is Debian Squeeze. This will hopefully produce binaries usable on Galaxy's targeted platforms (at time of writing: CentOS 6+, Debian 6.0+, Ubuntu 12.04+).

To use, install Docker, then:

```console
$ ./build <package>
```
e.g.

```console
$ ./build samtools
```
