#!/usr/bin/env python
import subprocess
import re
import yaml
import sys
import os
import argparse

def main(package, version, dryrun=False):
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, package, version)
    tentative_yaml_path = os.path.join(build_dir, 'build.yml')

    if not os.path.exists(tentative_yaml_path) and not os.path.isdir(tentative_yaml_path):
        print "No yaml file found at %s" % tentative_yaml_path
        sys.exit(3)

    with open(tentative_yaml_path, 'r') as handle:
        image_data = yaml.load(handle)

    DOCKER_TEMPLATE = """
    FROM %(image)s
    MAINTAINER Nare Coraor <nate@bx.psu.edu>

    ENV DEBIAN_FRONTEND noninteractive
    %(env_string)s

    VOLUME ["/host"]
    # Pre-build packages
    %(prebuild_packages)s

    # Pre-build commands
    %(prebuild_commands)s

    ENTRYPOINT ["/bin/bash", "/host/build.sh"]
    """

    SCRIPT_TEMPLATE = """
    #!/bin/sh
    urls="
    {url_list}
    "

    mkdir -p /build/ && cd /build/;

    ( for url in $urls; do
        wget "$url" || false || exit
    done)

    {commands}
    """

    template_values = {'image': 'ubuntu'}
    # ENVIRONMENT
    # TODO: expose base image as an argparse argument
    docker_env = {}
    if 'meta' in image_data:
        docker_env.update(image_data['meta'])
        # If there's an image name, use that.
        template_values['image'] = image_data['meta'].get('image', 'ubuntu')

    if 'env' in image_data:
        docker_env.update(image_data['env'])
    template_values['env_string'] = '\n'.join(['ENV %s %s' % (key, docker_env[key])
                                            for key in docker_env])

    prebuild_packages = ['wget', 'build-essential']
    if 'prebuild' in image_data and 'packages' in image_data['prebuild']:
        prebuild_packages.extend(image_data['prebuild']['packages'].strip().split())

    template_values['prebuild_packages'] = "RUN apt-get -qq update && apt-get install --no-install-recommends -y %s" % ' '.join(prebuild_packages)

    if 'prebuild' in image_data and 'commands' in image_data['prebuild']:
        template_values['prebuild_commands'] = '\n'.join([
            'RUN %s' % command.strip()
            for command in image_data['prebuild']['commands']
        ])

    with open(os.path.join(build_dir, 'Dockerfile'), 'w') as dockerfile:
        dockerfile.write(DOCKER_TEMPLATE % template_values)

    with open(os.path.join(build_dir, 'build.sh'), 'w') as script:
        urls = image_data['build'].get('urls', [])
        commands = image_data['build'].get('commands', [])

        script.write(SCRIPT_TEMPLATE.format(url_list=' '.join(urls),
                                            commands='\n'.join(commands)))

    if not dryrun:
        image_name = re.sub('[^A-Za-z0-9_]', '_', '%s:%s' % (package, version))
        command = ['docker', 'build', '-t', image_name, '.']
        execute(command, cwd=build_dir)

        runcmd = ['docker', 'run', '--volume=%s/:/host/' % build_dir, image_name]
        print ' '.join(runcmd)
        execute(runcmd, cwd=build_dir)


def execute(command, cwd=None):
    popen = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=cwd)
    for line in iter(popen.stdout.readline, b""):
        try:
            print line,
        except KeyboardInterrupt:
            sys.exit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build things inside of docker')
    parser.add_argument('package', help='Name of the package, should be a folder')
    parser.add_argument('version', help='Version of the package, should be a folder inside package')
    parser.add_argument('--dryrun', action='store_true', help='Only generate files, does not build and run the image')
    args = parser.parse_args()
    main(**vars(args))
