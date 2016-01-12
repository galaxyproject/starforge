Building on Mac OS X under QEMU/KVM
-----------------------------------

Due to legal reasons, a Mac OS X image can not be provided. However, an
`Ansible`_ playbook is available at `wheels/image/osx-playbook.yml
<https://github.com/galaxyproject/starforge/blob/master/wheels/image/osx-playbook.yml>`_.
that can be used to perform most of the image bootstrapping.

The Starforge developers make no claims as to the legality of virtualizing Mac
OS X under QEMU/KVM. Common readings of the Mac OS X license suggest that
virtualization of Mac OS X on Linux is legal as long as the underlying hardware
is an Apple computer. However, as with the rest of the Starforge project, the
authors are not liable for any claim, damages or other liability, as laid out
in the `Starforge License`_.

Once the image is available (and configured in ``config.yml``), Starforge will
use Btrfs_ to create snapshots of the image. Thus, you will need to store the
Mac OS X image in a btrfs subvolume on the host OS. 

Configuring the host OS
~~~~~~~~~~~~~~~~~~~~~~~

TODO

Creating the image
~~~~~~~~~~~~~~~~~~

TODO

Configuring the image
~~~~~~~~~~~~~~~~~~~~~

TODO

Configuring Starforge
~~~~~~~~~~~~~~~~~~~~~

TODO

.. _Ansible: http://www.ansible.com
.. _Starforge License: https://github.com/galaxyproject/starforge/blob/master/LICENSE
.. _Btrfs: https://btrfs.wiki.kernel.org/
