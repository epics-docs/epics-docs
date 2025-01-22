# Building an Application

## Required Header (.h) Files

An application that uses the CA client library functions described in
this document will need to include the cadef.h header files as follows.

``` c
#include "cadef.h"
```

This header file is located at {file}`{epics-base}/include/`. It includes
many other header files (operating system specific and otherwise), and
therefore the application must also specify
{file}`{epics-base}/include/os/{architecture}` in its header file search path.

For more information,
see the the {doc}`epics-base:cadef_h` reference documentation.

## Required Libraries

An application that uses the Channel Access Client Library functions
described in this document will need to link with the EPICS CA Client
Library and also the EPICS Common Library. The EPICS CA Client Library
calls the EPICS Common Library. The following table shows the names of
these libraries on UNIX and Windows systems.

|                             | UNIX Object | UNIX Shareable | Windows Object | Windows Shareable |
|-----------------------------|-------------|----------------|----------------|-------------------|
| **EPICS CA Client Library** | `libca.a`   | `libca.so`     | `ca.lib`       | `ca.dll`          |
| **EPICS Common Library**    | `libCom.a`  | `libCom.so`    | `Com.lib`      | `Com.dll`         |

The above libraries are located in {file}`{epics-base}/lib/{architecture}`.

## Compiler and System Specific Build Options

If you do not use the EPICS build environment (layered make files) then
it may be helpful to run one of the EPICS make files and watch the
compile/link lines. This may be the simplest way to capture the latest
system and compiler specific options required by your build environment.
Some snapshots of typical build lines are shown below, but this
information may be out of date.

### Typical Linux Build Options

``` bash
gcc -D_GNU_SOURCE -DOSITHREAD_USE_DEFAULT_STACK -D_X86_ -DUNIX -Dlinux -O3 -g -Wall -I. -I.. -I../../../../include/compiler/gcc -I../../../../include/os/Linux -I../../../../include -c ../acctst.c`
g++ -o acctst -L/home/user/epics/base-3.15/lib/linux-x86 -Wl,-rpath,/home/user/epics/base-3.15/lib/linux-x86 acctstMain.o acctst.o -lca -lCom`
```

### Typical Solaris Build Options

``` bash
/opt/SUNWspro/bin/cc -c -D_POSIX_C_SOURCE=199506L -D_XOPEN_SOURCE=500 -DOSITHREAD_USE_DEFAULT_STACK -DUNIX -DSOLARIS=9 -mt -D__EXTENSIONS__ -Xc -v -xO4 -I. -I.. -I../../../../include/compiler/solStudio -I../../../../include/os/solaris -I../../../../include ../acctst.c`
/opt/SUNWspro/bin/CC -o acctst -L/home/user/epics/base-3.15/lib/solaris-sparc/ -mt -z ignore -z combreloc -z lazyload -R/home/user/epics/base-3.15/lib/solaris-sparc acctstMain.o acctst.o -lca -lCom`
```

### Typical Windows Build Options

``` bash
cl -c /nologo /D__STDC__=0 /Ox /GL /W3 /w44355 /MD -I. -I.. -I..\\..\\..\\..\\include\\compiler\\msvc -I..\\..\\..\\..\\include\\os\\WIN32 -I..\\..\\..\\..\\include ..\\acctst.c`
link -nologo /LTCG /incremental:no /opt:ref /release /version:3.15 -out:acctst.exe acctstMain.obj acctst.obj d:/user/epics/base-3.15/lib/win32-x86/ca.lib d:/user/epics/base-3.15/lib/win32-x86/Com.lib`
```

### Typical vxWorks Build Options

``` bash
/usr/local/vxWorks-6.9/gnu/4.3.3-vxworks-6.9/x86-linux2/bin/ccppc -DCPU=PPC32 -DvxWorks=vxWorks -O2 -Wall -mstrict-align -mlongcall -fno-builtin -include /usr/local/vxWorks-6.9/vxworks-6.9/target/h/vxWorks.h -I. -I../O.Common -I.. -I../../../../include/compiler/gcc -I../../../../include/os/vxWorks -I../../../../include -I/usr/local/vxWorks-6.9/vxworks-6.9/target/h -I/usr/local/vxWorks-6.9/vxworks-6.9/target/h/wrn/coreip -c ../acctst.c
```

### Other Systems and Compilers

Contributions gratefully accepted.
