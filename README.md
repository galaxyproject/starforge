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

Starforge can build both pure Python and C-extension Python modules into wheels for Linux under Docker and for Mac OS X under QEMU/KVM. The script to build is `wheel.py` in the root directory. `wheel.py` reads the contents of [wheels/build/wheels.yml](https://github.com/galaxyproject/starforge/blob/master/wheels/build/wheels.yml) to determine what wheels can be built and their rules for building, and then runs [wheels/build/build.py](https://github.com/galaxyproject/starforge/blob/master/wheels/build/build.py) in Docker or a QEMU-virtualized system. To build all appropriate wheels for the given package, call:

```console
$ ./wheel.py <name-in-wheels.yml>
```

### Docker

Images used to build wheels on a variety of platforms are uploaded to the [Galaxy account on Docker Hub](https://hub.docker.com/r/galaxy/) and will be pulled as necessary. Typically you will only use the [base-wheel](https://hub.docker.com/r/galaxy/base-wheel/) and [base32-wheel](https://hub.docker.com/r/galaxy/base32-wheel/), which are Debian Squeeze-based images that will usually produce wheels usable on all Galaxy-supported platforms. The exception is the case when you need to install non-standard system libraries whose versions or location will differ by Linux distribution. In this case, a "full" set of images consisting of all distributions with official images in Docker Hub can be built. This is controlled in [wheels/build/wheels.yml](https://github.com/galaxyproject/starforge/blob/master/wheels/build/wheels.yml), see `psycopg2` for an example.

### QEMU/KVM

Due to legal reasons, an OS X image is not provided, and you are expected to provide one. Starforge then makes use of btrfs snapshots and QEMU/KVM to run the image and build wheels. An Ansible Playbook to do most of the image configuration that Starforge expects can be found in [wheels/image/osx-playbook.yml](https://github.com/galaxyproject/starforge/blob/master/wheels/image/osx-playbook.yml).

You will need to set up a config file to provide some parameters, namely, where your btrfs image snapshots are stored and what snapshot contains the base image, as well as how to access the guest once booted:

```yaml
wheel_osx_qemu:
    qemu_use_sudo: yes
    btrfs_use_sudo: yes
    snap_root: '/btrfs/machd_snap'
    snap_src: '@wheelbuild'
    diskimage: 'mac_hdd_10.10.img'
    osk: '<my_osk>'
    ssh:
        port: '8222'
        user: 'root'
        host: 'fauxsx'
```

Because starting is slow, if you are repeatedly building wheels, you can tell Starforge not to stop the image (and if running a second time, not to start the image) using the `--no-qemu-boot` and `--no-qemu-shutdown` arguments to `wheel.py`.

# TODO

- The build scripts themselves are targeted at whatever specific dist/release I
  am building them for at the moment and are not generalized to work on others.
