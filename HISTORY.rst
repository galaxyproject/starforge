.. :changelog:

History
-------

.. to_doc

---------------------
0.4.0.dev0
---------------------

    

---------------------
0.3.6 (2018-04-25)
---------------------

- Python 3-compatible ``setup.py`` wrapping. `Pull Request 171`_    
- Fix for pip 10. `c516bae`_

---------------------
0.3.5 (2017-10-01)
---------------------

- Support xz/lzma tarballs for wheel builds `Pull Request 166`_

---------------------
0.3.4 (2017-09-12)
---------------------

- Native support for auditwheel and delocate. (#160)

---------------------
0.3.3 (2017-09-08)
---------------------

- Do not build sdists with the `wheel` subcommand by default. (#155)

---------------------
0.3.2 (2017-09-08)
---------------------

- Fix a bug where the wrong working directory was set when building wheels with
  multiple sources. (#154)

---------------------
0.3.1 (2017-09-08)
---------------------

- Fix a bug with ``sudo`` and ``brew install`` on macOS. (#151).
- Short circuit platform caching on OS X (#150).

---------------------
0.3 (2017-01-10)
---------------------

- Drop the dependency on the "Galaxy" wheel fork, which makes installation much
  easier. "Platform-specific" wheels can still be built.
- When building Docker images, install Starforge from the local source instead
  of installing from PyPI or Github.

---------------------
0.2.1 (2016-05-27)
---------------------

- Do a case-insensitive comparison for cached tarball names (uWSGI's project
  name is ``uWSGI`` but its source tarballs are named ``uwsgi-*``). 7672547_

---------------------
0.2 (2016-05-19)
---------------------

- Added support for building manylinux1 wheels. 0dbecb7_

---------------------
0.1.1 (2016-01-20)
---------------------

- Only running prebuild during wheel builds (and not sdists) was too naive,
  since this prevents changing the version number of sdists in the prebuild
  action (a common use of the prebuild action). Instead, allow for separate
  ``wheel``, ``sdist``, and ``all`` prebuild actions.  Reverts the behavior of
  9008c57_. `Issue 64`_
- Install Galaxy pip from Github instead of wheels.galaxyproject.org so that
  Starforge images can be built with new versions of Galaxy pip before they are
  released. 97b4ba4_

---------------------
0.1 (2016-01-12)
---------------------

- Reimplemented the wheel building scripts as a library and ``starforge``
  command line
- Wrote some documentation

---------------------
Older than 0.1
---------------------

Originally Galaxy docker-build and later renamed Starforge, but as a collection
of disjointed shell scripts, Python, and YAML used to build Galaxy Tool Shed
dependencies, as well as rebuilding Debian and Ubuntu source packages with
modifications (which itself came from a project created to do the same via
Vagrant and Ansible called vadebuildsible).

.. _Galaxy: http://galaxyproject.org/

.. github_links
.. _c516bae: https://github.com/galaxyproject/starforge/commit/c516bae4052d326034c07d10ca0a639e7c393830
.. _Pull Request 171: https://github.com/galaxyproject/starforge/pull/171
.. _Pull Request 166: https://github.com/galaxyproject/starforge/pull/166
.. _9008c57: https://github.com/galaxyproject/starforge/commit/9008c57b09521298b919fac1de00fb62a448bcab
.. _97b4ba4: https://github.com/galaxyproject/starforge/commit/97b4ba4a591e359b01dc69161925c301c9a7d1b7
.. _0dbecb7: https://github.com/galaxyproject/starforge/commit/0dbecb79e28baecb62546b629cae9dbebf46df19
.. _7672547: https://github.com/galaxyproject/starforge/commit/7672547adf3fe05d19f29d62a6a766ef114fd459
.. _Issue 64: https://github.com/galaxyproject/starforge/issues/64
