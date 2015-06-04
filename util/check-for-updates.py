#!/usr/bin/env python
import fnmatch
import shutil
import filecache
import os
import yaml
import urllib2
import json
import re


class UpdateFetcher(object):

    def __init__(self):
        self.packages = {}

    def register_package(self, package, version):
        if package not in self.packages:
            self.packages[package] = []
        self.packages[package].append(version)

    def check_for_updates(self):
        flu_kwattrs = {}
        for package in self.packages:
            if 'default' in self.packages[package]:
                version = 'default'
            else:
                version = sorted(self.packages[package])[0]

            if package in ('bcftools', 'samtools'):
                flu_kwattrs['version_scheme'] = 'numbered'

            urls = self.get_urls(package, version)
            versioned_urls = [url for url in urls if '${' in url]
            if len(versioned_urls) > 0:
                for url in versioned_urls:
                    latest_version = self.find_latest_url(url, **flu_kwattrs)

                    # If that latest version doesn't have a folder all to itself...
                    if latest_version is not None:
                        if latest_version not in self.packages[package]:
                            self.create_new_version(package, version, latest_version)
                        else:
                            print "Already have %s@%s" % (package, latest_version)

    def create_new_version(self, package, version, latest):
        """Given a package name, a version to copy from, and the version to
        create...create a new folder for that version
        """
        print 'Creating %s %s %s' % (package, version, latest)

        src_yml = os.path.join(package, version, 'build.yml')
        dest = os.path.join(package, latest)
        dest_yml = os.path.join(package, latest, 'build.yml')
        os.mkdir(dest)

        with open(dest_yml, 'w') as out_handle:
            with open(src_yml, 'r') as in_handle:
                data = yaml.load(in_handle)
                data['meta']['version'] = latest
                out_handle.write(yaml.dump(data, default_flow_style=False))

    def get_urls(self, package, version):
        with open(os.path.join(package, version, 'build.yml'), 'r') as handle:
            data = yaml.load(handle)
            return data.get('build', {}).get('urls', [])

    @classmethod
    def filter_version(cls, version_list, scheme):
        if scheme == 'numbered':
            return [v for v in version_list if re.match('^[0-9.]*$', v)]

    @filecache.filecache(60 * 60 * 24)
    def find_latest_url(self, url, version_scheme=None):
        """Given a URL, find the most recent version of that available on the
        website.

        This is obviously not an error-free process, and will involve lots of
        hardcoded data, however, if it replaces a human doing it, that's all we
        need.
        """

        if 'github' in url:
            url_parts = url.split('/')
            username = url_parts[3]
            reponame = url_parts[4]
            if '/archive/' in url:
                # Latest is tough here as we're downloading a specific revision
                # number.
                gh_api_url = 'https://api.github.com/repos/%s/%s/git/refs/heads/master' % (username, reponame)
                gh_api_response = urllib2.urlopen(gh_api_url)
                return json.load(gh_api_response).get('object', {}).get('sha', None)
            elif 'releases/download' in url:
                gh_api_url = 'https://api.github.com/repos/%s/%s/tags' % (username, reponame)
                gh_api_response = urllib2.urlopen(gh_api_url)
                try:
                    versions = json.load(gh_api_response)
                    good_versions = self.filter_version([x['name'] for x in versions], version_scheme)
                    return good_versions[0]
                    # Have to catch the case when it isn't a list
                except Exception:
                    return None
            else:
                print "Unknown github URL type %s" % url
        elif 'hgdownload.soe.ucsc.edu' in url:
            ucsc_url = 'http://hgdownload.soe.ucsc.edu/admin/'
            ucsc_response = urllib2.urlopen(ucsc_url).read()
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(ucsc_response)
            versions = [x.text.replace('jksrc.v', '').replace('.zip', '')
                        for x in soup.find_all('a') if 'jksrc.v' in x.text]
            return str(sorted(map(int, versions))[-1])
        elif 'emboss.open-bio' in url:
            emboss_url = 'ftp://emboss.open-bio.org/pub/EMBOSS/'
            emboss_response = urllib2.urlopen(emboss_url).read()
            emboss_tar = [line for line in emboss_response.split('\n') if
                          'EMBOSS-' in line and 'latest' not in line]
            return emboss_tar[0].strip().split()[-1].replace('EMBOSS-', '').replace('.tar.gz', '')
        else:
            print "Updated unimplemented for %s" % url
            return None
        # http://downloads.sourceforge.net/project/math-atlas/Stable/${version}/atlas${version}.tar.bz2


def main():
    uf = UpdateFetcher()
    for root, dirs, files in os.walk('.'):
        for filename in files:
            if fnmatch.fnmatch(filename, 'build.yml'):
                package, version = os.path.split(root)
                package = package[2:]
                uf.register_package(package, version)

    uf.check_for_updates()


if __name__ == '__main__':
    main()
