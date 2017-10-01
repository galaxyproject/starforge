"""
Interface to build platform-specific wheels with the wheel package.

To use, import before importing wheel
"""
from __future__ import absolute_import

import errno
import json
import os
import distutils.util

import wheel.pep425tags
import wheel.bdist_wheel
from wheel.pep425tags import get_impl_version_info, get_impl_ver, get_abbr_impl, get_abi_tag
from lionshead import get_specific_platform
from lionshead.util import normalize_name


def get_platforms(supplied=None, major_only=False):
    """Return our platform name 'win32', 'linux_x86_64'"""
    # XXX remove distutils dependency
    platforms = ['any']
    if supplied:
        platforms.append(normalize_name(supplied))
    plat = distutils.util.get_platform()
    platforms.append(normalize_name(plat))
    spec_plat = get_specific_platform()
    if spec_plat is not None:
        dist, major, full, stability = spec_plat
        # TODO: underspecify if ABI is unstable?
        major_version = normalize_name('-'.join([plat] + [dist, major]))
        full_version = normalize_name('-'.join([plat] + [dist, full]))
        platforms.append(major_version)
        if not major_only and major_version != full_version:
            platforms.append(full_version)
    elif plat.startswith('linux-'):
        platforms.append(normalize_name('-'.join([plat] + ['unknown_distribution',
                                                           'unknown_version'])))
    return list(reversed(platforms))


def bdist_wheel_initialize_options(self):
    self._initialize_options()
    self.__plat_compat = None


def bdist_wheel_finalize_options(self):
    self._finalize_options()
    if not self.plat_name_supplied and self.plat_name == distutils.util.get_platform():
        self.plat_name = get_platforms(major_only=True)[0]


def bdist_wheel_plat_compat(self):
    if self.__plat_compat is None:
        compat_files = [os.path.join(os.sep, 'etc', 'python', 'binary-compatibility.cfg')]
        if 'VIRTUAL_ENV' in os.environ:
            compat_files.append(os.path.join(os.environ['VIRTUAL_ENV'], 'binary-compatibility.cfg'))
        self.__plat_compat = {}
        for compat_file in compat_files:
            try:
                with open(compat_file) as compat:
                    self.__plat_compat.update(json.load(compat))
            except IOError as exc:
                # Should EACCES issue a warning instead?
                if exc.errno != errno.ENOENT:
                    raise
    return self.__plat_compat


def bdist_wheel_get_tag(self):
    supplied = self.plat_name if self.plat_name_supplied else None
    supported_tags = pep425tags_get_supported(supplied_platform=supplied)

    if self.root_is_pure:
        if self.universal:
            impl = 'py2.py3'
        else:
            impl = self.python_tag
        tag = (impl, 'none', 'any')
    else:
        plat_name = self.plat_name
        if plat_name is None:
            plat_name = get_platforms(major_only=True)[0]
        plat_name = plat_name.replace('-', '_').replace('.', '_')
        impl_name = get_abbr_impl()
        impl_ver = get_impl_ver()
        # PEP 3149
        abi_tag = str(get_abi_tag()).lower()
        tag = (impl_name + impl_ver, abi_tag, plat_name)
        # XXX switch to this alternate implementation for non-pure:
        assert tag in supported_tags
        if plat_name in self.plat_compat and 'build' in self.plat_compat[plat_name]:
            tag = (impl_name + impl_ver, abi_tag, self.plat_compat[plat_name]['build'])
    return tag


def pep425tags_get_supported(versions=None, supplied_platform=None):
    """Return a list of supported tags for each version specified in
    `versions`.

    :param versions: a list of string versions, of the form ["33", "32"],
        or None. The first version will be assumed to support our ABI.
    """
    supported = []

    # Versions must be given with respect to the preference
    if versions is None:
        versions = []
        version_info = get_impl_version_info()
        major = version_info[:-1]
        # Support all previous minor Python versions.
        for minor in range(version_info[-1], -1, -1):
            versions.append(''.join(map(str, major + (minor,))))

    impl = get_abbr_impl()

    abis = []

    abi = get_abi_tag()
    if abi:
        abis[0:0] = [abi]

    abi3s = set()
    import imp
    for suffix in imp.get_suffixes():
        if suffix[0].startswith('.abi'):
            abi3s.add(suffix[0].split('.', 2)[1])

    abis.extend(sorted(list(abi3s)))

    abis.append('none')

    platforms = get_platforms(supplied=supplied_platform)

    # Current version, current API (built specifically for our Python):
    for abi in abis:
        for arch in platforms:
            supported.append(('%s%s' % (impl, versions[0]), abi, arch))

    # No abi / arch, but requires our implementation:
    for i, version in enumerate(versions):
        supported.append(('%s%s' % (impl, version), 'none', 'any'))
        if i == 0:
            # Tagged specifically as being cross-version compatible
            # (with just the major version specified)
            supported.append(('%s%s' % (impl, versions[0][0]), 'none', 'any'))

    # Major Python version + platform; e.g. binaries not using the Python API
    for arch in platforms:
        supported.append(('py%s' % (versions[0][0]), 'none', arch))

    # No abi / arch, generic Python
    for i, version in enumerate(versions):
        supported.append(('py%s' % (version,), 'none', 'any'))
        if i == 0:
            supported.append(('py%s' % (version[0]), 'none', 'any'))

    return supported


wheel.bdist_wheel.bdist_wheel._initialize_options = wheel.bdist_wheel.bdist_wheel.initialize_options
wheel.bdist_wheel.bdist_wheel.initialize_options = bdist_wheel_initialize_options
wheel.bdist_wheel.bdist_wheel._finalize_options = wheel.bdist_wheel.bdist_wheel.finalize_options
wheel.bdist_wheel.bdist_wheel.finalize_options = bdist_wheel_finalize_options
wheel.bdist_wheel.bdist_wheel.plat_compat = property(bdist_wheel_plat_compat)
wheel.bdist_wheel.bdist_wheel.get_tag = bdist_wheel_get_tag
wheel.pep425tags.get_supported = pep425tags_get_supported
