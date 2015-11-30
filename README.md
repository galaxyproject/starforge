![Starforge Logo](https://raw.githubusercontent.com/galaxyproject/starforge/master/docs/starforge_logo.png)

# Galaxy Starforge: Build things in Docker

Things you can do with Starforge:

- Build [Galaxy Tool Shed](https://toolshed.g2.bx.psu.edu) dependencies
- Build [Python Wheels](http://pythonwheels.com/) (e.g. for [wheels.galaxyproject.org](https://wheels.galaxyproject.org/))
- Rebuild Debian or Ubuntu source packages (for modifications)

## Tool Shed Dependencies

There are two scripts that can be used, depending on the package recipes available:

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

## Building all the things

There's a separate `build-all.sh` which allows you to build all of the packages using their preferred build mechanism

## Notes on the two build scripts

### `build.py`

The `<version>` option is optional, and defaults to the string 'default', which
is useful for recipes that don't have version specific changes (E.g. bcftools 1.0 builds
identically to 1.2)

## Python Wheels

Starforge can build both pure Python and C-extension Python modules into wheels for Linux under Docker and for Mac OS X under QEMU/KVM. To do this, you'll want to install Starforge (preferably in a Python virtualenv) using `pip install starforge` (to install from [PyPI](https://pypi.python.org/)) or `python setup.py install` to install from the source. Docker (and QEMU) images to use are specified in [starforge/config/default.yml](https://github.com/galaxyproject/starforge/blob/master/wheels/build/wheels.yml), to modify this file, copy it to `$XDG_CONFIG_HOME/galaxy-starforge/config.yml` (`$XDG_CONFIG_HOME` is, by default `~/.config`). The sample file [wheels/build/wheels.yml](https://github.com/galaxyproject/starforge/blob/master/wheels/build/wheels.yml) is used to determine what wheels can be built and their rules for building. To use, use the `--wheels-config` argument to `starforge wheel` or copy `wheels.yml` to `$XDG_CONFIG_HOME/galaxy-starforge/wheels.yml`. Wheels can be built using `starforge wheel <package>`, e.g.:

```console
$ starforge wheel pycrypto
```

### Docker

Images used to build wheels on a variety of platforms are uploaded to the [Starforge account on Docker Hub](https://hub.docker.com/r/starforge/) and will be pulled as necessary. Typically you will only use the [base-wheel](https://hub.docker.com/r/starforge/base-wheel/) and [base32-wheel](https://hub.docker.com/r/starforge/base32-wheel/), which are Debian Squeeze-based images that will usually produce wheels usable on all Galaxy-supported platforms. The exception is the case when you need to install non-standard system libraries whose versions or location will differ by Linux distribution. In this case, a "full" set of images consisting of all distributions with official images in Docker Hub can be built. This is controlled in [wheels/build/wheels.yml](https://github.com/galaxyproject/starforge/blob/master/wheels/build/wheels.yml), see `psycopg2` for an example.

### QEMU/KVM

Due to legal reasons, an OS X image is not provided, and you are expected to provide one. Starforge then makes use of btrfs snapshots and QEMU/KVM to run the image and build wheels. An Ansible Playbook to do most of the image configuration that Starforge expects can be found in [wheels/image/osx-playbook.yml](https://github.com/galaxyproject/starforge/blob/master/wheels/image/osx-playbook.yml).

# TODO

- The build scripts themselves are targeted at whatever specific dist/release I
  am building them for at the moment and are not generalized to work on others.
