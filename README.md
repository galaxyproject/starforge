# Build things in Docker

Things you can do with docker-build:

- Build [Galaxy Tool Shed](https://toolshed.g2.bx.psu.edu) dependencies
- Rebuild Debian or Ubuntu source packages (for modifications)

The base image for Galaxy packages is Debian Squeeze. This will hopefully
produce binaries usable on Galaxy's targeted platforms (at time of writing:
CentOS 6+, Debian 6.0+, Ubuntu 12.04+).

To use, install Docker. Then, for Tool Shed dependencies:

```console
$ ./build galaxy <package>
```
e.g.

```console
$ ./build galaxy samtools
```

For building dpkgs, use:

```console
$ ./build <dist>[:tag] <package>
```

e.g.:

```console
$ ./build ubuntu:trusty nginx
```

## TODO

- The build scripts themselves are targeted at whatever specific dist/release I
  am building them for at the moment and are not generalized to work on others.
- Some things in the build scripts probably belong in some sort of build script
  library.
