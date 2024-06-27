Installation on Windows
=======================

``` {tags}
beginner
```

Introduction
------------

### EPICS

EPICS is a toolkit for building control systems. You can get the basic
ideas from the EPICS web site at
<https://epics-controls.org/about-epics/>.

Traditionally, an EPICS installation starts with compiling the core
parts ("EPICS Base") from source. This process is covered by these
instructions, starting from scratch on a Windows system and getting you
to the point where you have a working IOC and can connect to it from a
command line shell. Other How-Tos will guide you further.

### EPICS on Windows

While it is not its primary or most widely used target platform, the
EPICS low-level libraries have good and well-tested implementations on
Windows. EPICS runs fine on Windows targets, fast and robust.

There are, however, a few choices about how to compile and run EPICS on
Windows that you will have to take beforehand. Understanding these
choices and their implications before making decisions will help you to
avoid mistakes and spend time fixing them.

### Cygwin

As mentioned before, EPICS Base has its own native Windows
implementation of all necessary low level services. There is no need to
go through the Posix emulation layer that Cygwin provides. The native
Windows implementation is more portable and performs better. Unless you
need to use Cygwin, e.g., if you are using a binary vendor-provided
library for Cygwin, you should prefer a native Windows build.

Also, Cygwin is deprecated as a target platform for EPICS.

### Build Time

The time needed to build EPICS Base depends on a few factors, including
the speed of the processor and file system, the compiler used, the build
mode (DLL or static), possibly debugging options and others. On a medium
sized two-core machine, a complete build of EPICS 7 often takes between
15 and 30 minutes, the 3.15 branch can be built in 6 to 10 minutes.

Use `make -j<n>` to make use of multiple CPU cores.

Required Tools
--------------

-   C++ compiler: either MinGW (GCC) or Microsoft's Visual Studio
    compiler (VS)
-   archive unpacker (7zip or similar)
-   GNU Make (4.x)
-   Perl

Choice 1: Compiler
------------------

You will need a C++ compiler with its supporting C++ standard libraries.
Two major compilers are supported by EPICS and its build system:

Microsoft's Visual Studio compiler (VS)

:   Probably the most widely used compiler for EPICS on the Windows
    platform. The "Community Edition" is free to download and use.
    (You need to have Administrator rights to install it.) Any Visual
    Studio installation will need the "C++ development" parts for the
    compiler toolchain to be installed.

    EPICS is using the Make build system. You can use the Visual Studio
    IDE, but EPICS does not provide any project files or configurations
    for Visual Studio's own build system.

MinGW (GCC) - Minimalist GNU for Windows

:   A compiler toolchain based on the widely-used GNU compilers that -
    like the VS compiler - generates native Windows executables.

Both compiler toolchains can create shared libraries (DLLs) and static
libraries. On a 64bit system, both can create 64bit output (runs on
64bit systems) and 32bit output (runs on both 32bit and 64bit systems).

When using C++, libraries are not compatible between those two compilers
toolchains. When generating a binary (e.g., an IOC), all C++ code that
is being linked must have been generated uniformly by either VS or
MinGW. (The reason is different name mangling for symbol names: a symbol
needed for linking an executable will not be found in a library
generated with the other compiler, because its name is different there.)

If you need to link against vendor-provided binary C++ libraries, this
will most likely determine which compiler you need to use.

Choice 2: Build Environment and Tool Installation
-------------------------------------------------

### MSYS2

[MSYS2](https://www.msys2.org/) (available for Windows 7 and up) is a
pretty complete "feels like Linux" environment. It includes a Linux
style package manager (pacman), which makes it very easy to install the
MinGW toolchains (32 and 64 bit) and all other necessary tools. It also
offers a bash shell. If you are used to working in a Linux environment,
you will like working on MSYS2.

MSYS2 can be installed, used and updated (including tools and compilers)
without Administrator rights.

As up-to-date MinGW/GCC compilers are an integral part of the package,
MSYS2 is strongly recommended for using the MinGW compiler toolchains.

The Visual Studio compilers can also be used from the MSYS2 bash. This
needs a one-time setup of an intermediate batch script to get the Visual
Studio environment settings correctly inherited. The resulting shell can
compile using Visual Studio compilers as well as using MinGW, selected
by the EPICS_HOST_ARCH environment variable setting.

### Chocolatey

[Chocolatey](https://chocolatey.org/) is a package manager for Windows
with a comfortable GUI, making it easy to install and update software
packages (including the tools needed for building EPICS). In many cases,
Chocolatey packages wrap around the native Windows installers of
software.

Using Chocolatey needs Administrator rights.

### Windows Installers

You can also install the required tools independently, directly using
their native Windows installers.

For Perl, both Strawberry Perl and ActivePerl are known to work.
Strawberry Perl is more popular; it includes GNU Make (as gmake.exe) and
the MinGW/GCC compiler necessary to build the Channel Access Perl module
that is part of EPICS Base.

For GNU Make, the easiest way is to use the one included in Strawberry
Perl. Otherwise, there is a Windows binary provided on the EPICS web
site.

Native Windows installers often need Administrator rights.

Choice 3: Static or DLL Build / Deployment
------------------------------------------

If you configure the EPICS build system to build your IOCs dynamically
(i.e., using DLLs), they need the DLLs they have been linked against to
be present on the target system, either in the same directory as the IOC
binary or in a directory that is mentioned in the `%PATH%` environment
variable.

Depending on how you plan to deploy your IOCs into the production
system, it might be easier to use static builds when generating IOCs.
The resulting binaries will be considerably larger, but they will run on
any Windows system without providing additional EPICS DLLs.

When running many EPICS IOCs on a single target machine, the shared
aspect of a DLL build will lead to smaller memory usage. The DLL is in
memory once and used concurrently by all IOC binaries, while the
statically linked binaries each have their own copy of the library in
memory.

*Note:* When using the Visual Studio compilers, compilation uses
different flags for building DLLs and building static libraries. You
can't generate static and shared libraries in the same build. You can
provide both options in your EPICS installation by running both builds
in sequence (with `make clean` inbetween), so that your applications can
decide between static or DLL build. Or you can just provide one option
globally for your installation, which all installations will have to
use.

Windows Path Names
------------------

Make based builds do not work properly when there are space characters
or parentheses in the paths that are part of the build (including the
path where the make application resides and the path of the workspace).

If you cannot avoid paths with such characters, use the Windows short
path (can be displayed with `dir /x`) for all path components with those
characters in any path settings and/or your workspace directory.

Put Tools in the PATH
---------------------

No matter which shell and environment you use, the tools (perl, make)
should end up being in the `%PATH%`, so that they are found when called
just by their name.

Install and Build
-----------------

Depending on your set of choices, the instructions for building EPICS
Base, building IOC applications and running them are different. The
following detailed instructions focus on two common sets of choices:
using MSYS2 with the MinGW Gnu compilers and using the plain Windows
command prompt with the Visual Studio compilers.

Setting the environment for building and running applications has to be
done for either set of choices.

``` {toctree}
installation-windows-msys2 installation-windows-plain
installation-windows-env
```
