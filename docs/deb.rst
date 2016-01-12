(Re)building Debian Packages
----------------------------

Starforge can be used to build or rebuild Debian or Ubuntu source packages with
very little effort. These are suitable for use on a private APT repository or
Ubuntu PPA.

The only example of this Starforge build type currently in the repository is
the `nginx <https://github.com/galaxyproject/starforge/tree/master/nginx>`_
package, which is modified to include the nginx upload module.

**How to build packages:**

1. Create a build recipe. You can use the nginx package as an example.

2. Run the appropriate build method (``build`` or ``build.py``).

3. Packages and related artifacts will be output to the package directory. From
   here, on the (Debian-based) host system, you can sign the packages using:

   .. sourcecode:: console

        % debsign -S <pkg>-<version>_source.changes

4. Upload to a PPA with: 

   .. sourcecode:: console

        % dput ppa:<owner>/<repo> <pkg>-<version>_source.changes
