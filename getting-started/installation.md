# How EPICS installations work

An EPICS installation typically consists of multiple software modules.

EPICS Base will always be one of them.
Base and additional modules that provide libraries or tools
are often referred to as _Support Modules_,
while the modules that produce your control system
are often called _IOC Application Modules_.

EPICS Base and the Support Modules are usually common and shared
between the IOC Applications of an installation.
You can consider a stable and tested set of Base and Support Modules
a _release_ of your development environment.

As Support Modules are shared, have a longer life cycle
and are held more stable than the IOC Applications that use them,
it is a good idea to keep the Support Modules and IOC Applications separate.

These pages cover installing EPICS Base and Support Modules.
IOC Applications are too specific to be covered by general documentation.

## General workflow

The traditional way to install EPICS is by compiling from sources.

While the specific instructions differ between Operating Systems on your host,
the general steps are always the same:

1.  Install prerequisites
2.  Download, configure and install
    [EPICS Base](installation-base.md)
3.  Download, configure and install
    [Support Modules](../software/epics-related-software.md)
4.  [Create your IOC Application](creating-ioc.rst)

## Which version should I choose?

Please use new versions.

Unless you have specific reasons to use an older version,
using the current release will make sure you have all the features
and all the bug fixes.
Using current versions for _all_ modules in your set of Support Modules
minimizes issues that may show up because of incompatibilities.

The
[EPICS 7.0 Release Notes](https://docs.epics-controls.org/projects/base/en/latest/RELEASE_NOTES.html)
list what changed in each release of EPICS Base.

## Distributions and deployment frameworks

Several projects take the workflow above off your hands,
distributing EPICS as ready-built packages or images
rather than as a source tree you configure and compile yourself.
They differ mainly in what they distribute and how IOCs are deployed:

*   [e3](https://epics-e3.github.io), the ESS EPICS Environment,
    which distributes Base and Support Modules as conda packages.
    Modules are built as dynamically loadable modules
    that a generic IOC loads at runtime,
    so an IOC application need not be compiled for each deployment,
    and isolated environments let IOCs needing different sets of modules,
    or different versions of Base, run on the same host.
    It is not limited to ESS.
*   [EPNix](https://epics-extensions.github.io/EPNix/),
    which distributes EPICS software as Nix packages.
    Application and system dependencies alike are declared explicitly,
    so the same definition reproduces the same build
    on another machine or at a later date.
    It also packages tools such as procServ and Phoebus
    for any Linux distribution, and provides NixOS service modules.
*   [epics-containers](https://epics-containers.github.io),
    which distributes generic IOCs as container images
    that a configuration file turns into specific IOC instances.
    The same image runs under Docker or Podman on a workstation
    and under Kubernetes in production,
    where Helm and Argo CD manage the deployment.

Each still installs the same components described above.
Which one suits you, if any,
depends on how many IOCs you expect to manage and how you deploy them.
