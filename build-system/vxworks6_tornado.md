# Configuring Tornado/vxWorks 5.5.x

## Tornado/vxWorks 5.5.x Information

This page provides a repository for information about using the WRS Tornado environment and the vxWorks 5.5.x RTOS with EPICS that doesn’t really belong anywhere else on this site.

Note that there is a [separate page](configuring-vxworks-6_x) provided for users of vxWorks 6.x and Wind River Workbench.

There is also a reasonably good Tornado 2.0 FAQ available [on the web](http://www.xs4all.nl/~borkhuis/vxworks/vxworks.html), mostly comprising answers to questions posted to the comp.os.vxworks news group.

## Tornado 2.2 (vxWorks 5.5.x)

### Installation

According to the Tornado 2.2 release notes, you cannot install multiple host and/or target architectures in the same directory.

### Linux Hosting

See [this page](https://epics.anl.gov/base/tornado-linux.php) for information building vxWorks target code on Linux.

### EPICS Support

VxWorks 5.5 is only supported on EPICS 3.14.x and 3.15.x releases. From Base-3.16 and later you must use VxWorks 6.6 or later.

## PowerPC Issues

There is a [separate page](https://epics.anl.gov/base/ppc.php) discussing the specific problems associated with using PowerPC CPUs under vxWorks/Tornado.
