How To Port EPICS to a new OS/Architecture
==========================================

This isn’t a detailed list of tasks, but is intended to show the main stages needed to add a new build architecture to EPICS. 
If you make use of this and find there are hints you’d like to suggest, or steps missing please add them.

* Download a tarfile for the latest release of EPICS Base, or the snapshot from the R3.14 branch (not the trunk), and unpack it.
* If you’re not already familiar with EPICS, at least skim chapter 4 of the IOC Application Developers Guide (hereafter known as the AppDevGuide; our build system is different to the usual “./configure && make” approach.
* Build your <base> on a linux-x86 or solaris-sparc system so you know what a fully built system actually looks and acts like. You can build multiple architectures simultaneously in the same tree, which makes for easier comparisons. On linux the build instructions should be as simple as

::

    export EPICS_HOST_ARCH=linux-x86
    cd <base>
    make

* On the new system system, setenv EPICS_HOST_ARCH to the name for your new architecture, which usually takes the form <osname>-<cpufamily>, for example solaris-sparc, linux-x86, windows-x86
* In the <base>/configure/os directory, create these files by copying and editing the files from an existing architecture:

::

    CONFIG.Common.<arch>
    CONFIG.<arch>.Common
    CONFIG_SITE.<arch>.Common

* I would suggest looking at the darwin-ppc or linux-x86 versions to start with; for a Unix-like OS you should be able to make use of the UnixCommon and/or GnuCommon files to provide most of the definitions and rules.
* If you have to cross-compile then there’s more work you have to do and these instructions are probably not sufficient to get you there.
