# Installing EPICS Base

EPICS Base is the first component of any EPICS installation,
and the one every Support Module and IOC Application is built against.
See [How EPICS installations work](installation.md)
for how it fits together with the rest of an installation.

## Getting the source

Released versions are published on the
[EPICS Base releases page](https://github.com/epics-base/epics-base/releases).
Each release provides a source tarball, `base-<version>.tar.gz`,
and a detached GPG signature, `base-<version>.tar.gz.asc`.

The platform guides below fetch the same tarball
from <https://epics-controls.org/download/base/>.

To follow development instead of a release,
clone <https://github.com/epics-base/epics-base>
and check out the branch you want.
Releases are tested to work as documented; branches are not.

## Building from source

Compiling Base yourself is the usual route.
The platform guides at the end of this page take you through it
on each supported host.

Building puts the build configuration in your hands.
`configure/CONFIG_SITE`, and the files it includes,
decide what gets built and where it ends up. For example:

*   `INSTALL_LOCATION` sets the installation directory.
    It defaults to `$(TOP)`, the top of the source tree,
    so setting it is how you install Base somewhere else.
*   `CROSS_COMPILER_TARGET_ARCHS` lists the targets to cross compile for,
    which is how you build for an embedded target from your workstation.
*   `SHARED_LIBRARIES` (`YES` or `NO`) chooses
    between shared and static libraries.

The {doc}`Build Facility <../build-system/specifications>` documents these
and the rest of the build configuration in full.

## Prebuilt packages

The [conda-forge](https://conda-forge.org) channel publishes prebuilt
`epics-base` packages for Linux (x86-64 and aarch64),
macOS (Intel and Apple silicon) and Windows (x86-64):

```bash
conda install conda-forge::epics-base
```

The packages include the headers and libraries as well as the tools,
so you can build Support Modules and IOC applications against them,
without needing a compiler or a build step to install Base itself.

The trade-off is that the build-time choices above have been made for you.
If you need to change any of them, build from source instead.

If you do not already have conda,
conda-forge's [introduction for users](https://conda-forge.org/docs/user/introduction/)
covers enabling the channel and recommends miniforge for a fresh install.

## Platform guides

Pick the guide matching the host you are building on.

:::{toctree}
:maxdepth: 2
:titlesonly:

installation-linux
installation-windows
installation-rtems
os-specifics
:::
