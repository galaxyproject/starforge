.. figure:: https://raw.githubusercontent.com/galaxyproject/starforge/master/docs/starforge_logo.png
   :alt: Starforge Logo
   :align: center
   :figwidth: 100%
   :target: https://github.com/galaxyproject/Starforge

Starforge: Build `Galaxy`_ things in virtualization

Things you can do with Starforge:

- Build `Galaxy Tool Shed`_ dependencies
- Build `Python Wheels`_ (e.g. for the `Galaxy Wheels Server`_)
- Rebuild Debian or Ubuntu source packages (for modifications)

These things will be built in Docker. Additionally, wheels can be built in
QEMU/KVM virtualized systems.

Documentation can be found at `starforge.readthedocs.org
<http://starforge.readthedocs.org/>`_

Quick Start
-----------

For all types of builds, begin by `installing Docker`_.

Tool Shed Dependencies
~~~~~~~~~~~~~~~~~~~~~~

There are two scripts that can be used, depending on the package recipes
available:

.. sourcecode:: console

    $ ./build.sh <package>
    $ python build.py <package> --version 1.0

``build.sh`` is the older format, and simply uses a single
``<package>build.sh`` file, like Atlas. `build.py` is the newer format, and
uses yaml metadata in ``<package>/<version>/build.yml``.

The base image for Galaxy packages is Debian Squeeze. This will hopefully
produce binaries usable on Galaxy's targeted platforms (at time of writing:
CentOS 6+, Debian 6.0+, Ubuntu 12.04+).

.. sourcecode:: console

    $ ./build galaxy <package>
    $ python build.py <package>

To build packages against a different OS, you can use the `--image` flag, e.g.:

.. sourcecode:: console

    $ ./build <dist>[:tag] <package>
    $ python build.py <package> --image <dist>[:tag]

e.g.

.. sourcecode:: console

    $ ./build ubuntu:trusty nginx
    $ python build.py nginx --image debian:squeeze

**Building all the things:**

There's a separate ``build-all.sh`` which allows you to build all of the
packages using their preferred build mechanism

Notes on the two build scripts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**build.py**

The ``<version>`` option is optional, and defaults to the string ``'default'``,
which is useful for recipes that don't have version specific changes (E.g.
bcftools 1.0 builds identically to 1.2)

Python Wheels
~~~~~~~~~~~~~

Starforge can build both pure Python and C-extension Python modules into wheels
for Linux under Docker and for Mac OS X under QEMU/KVM. To do this, you'll want
to install Starforge (preferably in a Python virtualenv) using ``pip install
starforge`` (to install from PyPI_) or ``python setup.py install`` to install
from the source.

Docker (and QEMU) images to use are specified in `starforge/config/default.yml
<https://github.com/galaxyproject/starforge/blob/master/wheels/build/wheels.yml>`_.
To modify this file, copy it to
``$XDG_CONFIG_HOME/galaxy-starforge/config.yml`` (``$XDG_CONFIG_HOME`` is, by
default ``~/.config``). The sample file `wheels/build/wheels.yml`_ is used to
determine what wheels can be built and their rules for building. To use this
file, use the ``--wheels-config`` argument to ``starforge wheel`` or copy
``wheels.yml`` to ``$XDG_CONFIG_HOME/galaxy-starforge/wheels.yml``.

Wheels can be built using ``starforge wheel <package>``, e.g.:

.. sourcecode:: console

    $ starforge wheel pycrypto
    $ starforge wheel --no-qemu pysam   # only build on docker

See the output of ``starforge --help`` for help using the Starforge command-line interface.

Pull Request wheel builder
^^^^^^^^^^^^^^^^^^^^^^^^^^

Pull requests to the `Starforge`_ repository on Github that modify
`wheels/build/wheels.yml`_ can automatically be built for all specified
platforms on a dedicated Starforge build server by the `Galaxy Jenkins`_
service. To utilize, modify wheels.yml as appropriate and create a pull
request. Any member of the `Galaxy Committers`_ group can then authorize
Jenkins to initiate the build. If it fails, you can modify the pull request and
further builds can be triggered.

Notes on images
^^^^^^^^^^^^^^^

**Linux**

Images used to build wheels on a variety of platforms are uploaded to the
`Starforge Docker Hub`_ repo and will be pulled as necessary. Typically you
will only use the `base-wheel
<https://hub.docker.com/r/starforge/base-wheel/>`_ and `base32-wheel
<https://hub.docker.com/r/starforge/base32-wheel/>`_ images, which are Debian
Squeeze-based images that will usually produce wheels usable on all
Galaxy-supported platforms. The exception is the case when you need to install
non-standard system libraries whose versions or location will differ by Linux
distribution. In this case, a "full" set of images consisting of all
distributions with official images in Docker Hub can be built. This is
controlled in `wheels/build/wheels.yml`_, see ``psycopg2`` for an example.

**Mac OS X**

Mac OS X mages are not provided due to legal reasons. Consult the :doc:`osx`
documentation for details.

.. _Galaxy: http://galaxyproject.org/
.. _Galaxy Tool Shed: http://toolshed.g2.bx.psu.edu/
.. _Python Wheels: http://pythonwheels.com/
.. _Galaxy Wheels Server: http://wheels.galaxyproject.org/
.. _installing Docker: https://docs.docker.com/engine/installation/
.. _PyPI: https://pypi.python.org/
.. _Starforge Docker Hub: https://hub.docker.com/r/starforge/
.. _wheels/build/wheels.yml:
.. _Galaxy Jenkins: http://jenkins.galaxyproject.org
.. _Starforge: https://github.com/galaxyproject/starforge/
.. _Galaxy Committers: https://github.com/galaxyproject/galaxy/blob/dev/doc/source/project/organization.rst
