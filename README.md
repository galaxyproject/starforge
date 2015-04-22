# Build things in Docker

Things you can do with docker-build:

- Build [Galaxy Tool Shed](https://toolshed.g2.bx.psu.edu) dependencies
- Rebuild Debian or Ubuntu source packages (for modifications)

To use, install Docker. Then for building packages:

```console
$ python build.py <package> --version 1.0
```

Build recipes are stored as yaml metadata in `<package>/<version>/build.yml`

The `<version>` option is optional, and defaults to the string 'default', which
is useful for recipes that are versionless. (E.g. bcftools 1.0 builds
identically to 1.2)

The base image for Galaxy packages is Debian Squeeze. This will hopefully
produce binaries usable on Galaxy's targeted platforms (at time of writing:
CentOS 6+, Debian 6.0+, Ubuntu 12.04+).

To use, install Docker. Then, for Tool Shed dependencies, e.g.

```console
$ python build.py samtools
```

To build packages against a different OS, you can use the `--image` flag, e.g.:

```console
$ python build.py nginx --image debian:squeeze
```


## TODO

- The build scripts themselves are targeted at whatever specific dist/release I
  am building them for at the moment and are not generalized to work on others.
