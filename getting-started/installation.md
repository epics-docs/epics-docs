# Installation Overview

:::{tags} beginner
:::

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

This section will mostly cover installing EPICS Base and Support Modules.
IOC Applications are too specific to be covered by general documentation.

## General workflow

The traditional way to install EPICS is by compiling from sources.

While the specific instructions differ between Operating Systems on your host,
the general steps are always the same:

1.  Install prerequisites
2.  Download, configure and install EPICS Base
3.  Download, configure and install Support Modules
4.  Create your IOC Application

## Which version should I chose?

Please use new versions.

Unless you have specific reasons to use an older version,
using the current release will make sure you have all the features
and all the bug fixes.
Using current versions for _all_ modules in your set of Support Modules
minimizes issues that may show up because of incompatibilities.
