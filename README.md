# Build things in Docker

Things you can do with docker-build:

- Build [Galaxy Tool Shed](https://toolshed.g2.bx.psu.edu) dependencies
- Rebuild Debian or Ubuntu source packages (for modifications)
- Build [Python Wheels](http://pythonwheels.com/)

To use, install Docker. Then for building packages there are two scripts that
can be used, depending on the package recipes available:

```console
$ ./build.sh <package>
$ python build.py <package> --version 1.0
```

The `build.sh` is the older format, and simply uses a single
`<package>build.sh` file, like [Atlas](Atlas/). The `build.py` is the newer
format, and uses yaml metadata in `<package>/<version>/build.yml`.

The base image for Galaxy packages is Debian Squeeze. This will hopefully
produce binaries usable on Galaxy's targeted platforms (at time of writing:
CentOS 6+, Debian 6.0+, Ubuntu 12.04+).

To use, install Docker. Then, for Tool Shed dependencies, e.g.

```console
$ ./build galaxy <package>
$ python build.py <package>
```

To build packages against a different OS, you can use the `--image` flag, e.g.:

```console
$ ./build <dist>[:tag] <package>
$ python build.py <package> --image <dist>[:tag]
```

e.g.

```console
$ ./build ubuntu:trusty nginx
$ python build.py nginx --image debian:squeeze
```

# Building all the things

There's a separate `build-all.sh` which allows you to build all of the packages using their preferred build mechanism

# Notes on the two build scripts

## `build.py`

The `<version>` option is optional, and defaults to the string 'default', which
is useful for recipes that don't have version specific changes (E.g. bcftools 1.0 builds
identically to 1.2)


## TODO

- The build scripts themselves are targeted at whatever specific dist/release I
  am building them for at the moment and are not generalized to work on others.
