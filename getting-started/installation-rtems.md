# Installation on RTEMS 6 (Release 6.1)

```{tags} developer, advanced
```

## RTEMS 6 (Release 6.1) Information

RTEMS 6.1 was released on 22 January 2025. New in this release is the support of different network stacks. The familiar BSD stack (‘legacy’ stack) is still supported. This was used in the previous EPICS customisations for RTEMS 4.9 and 4.10. This BSD stack is a bit outdated and does not support NFSv4, for example, which is now mandatory for many organisations for security reasons. In order to be able to support these requirements in the future, the RTEMS developers have decided to use the libbsd stack from FreeBSD for new releases. With RTEMS 6.1, however, both stacks are supported for the time being. Unfortunately, the new stack does not support all the boards previously used in our environment. The missing Nexus device drivers are mostly missing.

This documentation provides a advice on using the RTEMS Source Builder to build the RTEMS tools, kernel and 3rd party packages from source. The process for creating this environment is documented [here] (https://ftp.rtems.org/pub/rtems/releases/6/6.1/). If you discover any other information that ought to be published here, please [let me know](mailto:junkes@fhi.mpg.de).

Please note that we are specifically addressing the hardware used in the EPICS environment, primarily with RTEMS.

*   VMEbus CPUs (MVME3100, MVME6100, MVME2500)
*   Development boards (Beagleboneblack, ZYBO Z7-20, ...)
*   Qemu - Support e.g. xilinx\_zynq\_a9\_qemu

In order to support these systems, the tools for the *arm* and *powerpc* architectures must be installed.

> ### On Mac development host
>
> If the environment is to be installed on a Mac. It is helpful to create a virtual hard disc with a case-sensitive APFS file system (e.g. /Volumes/Epics): ![](media/Mac_AFPFS.png)
>

We are now starting with our first board MVME6100 (aka beatnik). Unfortunately, there is no bsps-setup file for this in the source builder in the release, so we have to control the steps for installing the tools and the kernel with our own script.

>On Mac: Make sure that the installation path used is on the APFS (case-sensitive) file system.


``` 
#!/bin/bash
#RTEMS development
export RTEMS_VERSION=6
export RTEMS_RELEASE=6.1
export RTEMS_CPU=powerpc
export RTEMS_BSP=beatnik
export RTEMS_ARCH=${RTEMS_CPU}-rtems${RTEMS_VERSION}
SCRIPT=$(readlink -f $0)
export RTEMS_ROOT=`dirname $SCRIPT`/rtems/${RTEMS_RELEASE}

#install rsb
wget https://ftp.rtems.org/pub/rtems/releases/6/6.1/sources/rtems-source-builder-6.1.tar.xz
tar Jxf rtems-source-builder-6.1.tar.xz

#build the tools
cd rtems-source-builder-6.1/rtems
../source-builder/sb-set-builder \
  --prefix=${RTEMS_ROOT} \
  6/rtems-${RTEMS_CPU}
```

Building the powerpc tools takes a while > 30 min.

In *./rtems/6.1/bin* you should then find the powerpc-tools:

```
rtems@rtems-dev:~/RTEMS_MVME6100_legacy_stack$ ls  rtems/6.1/bin/
convert-dtsv0             powerpc-rtems6-c++filt     powerpc-rtems6-gdb            powerpc-rtems6-size       rtems-record-lttng
dtc                       powerpc-rtems6-cpp         powerpc-rtems6-gdb-add-index  powerpc-rtems6-strings    rtems-run
dtdiff                    powerpc-rtems6-elfedit     powerpc-rtems6-gprof          powerpc-rtems6-strip      rtems-syms
fdtdump                   powerpc-rtems6-g++         powerpc-rtems6-ld             rtems-addr2line           rtems-test
fdtget                    powerpc-rtems6-gcc         powerpc-rtems6-ld.bfd         rtems-bin2c               rtems-tftp-proxy
fdtoverlay                powerpc-rtems6-gcc-13.3.0  powerpc-rtems6-lto-dump       rtems-boot-image          rtems-tftp-server
fdtput                    powerpc-rtems6-gcc-ar      powerpc-rtems6-nm             rtems-bsp-builder         rtems-tld
mkimage.py                powerpc-rtems6-gcc-nm      powerpc-rtems6-objcopy        rtems-exeinfo             trace-converter
powerpc-rtems6-addr2line  powerpc-rtems6-gcc-ranlib  powerpc-rtems6-objdump        rtems-gen-acpica-patches
powerpc-rtems6-ar         powerpc-rtems6-gcov        powerpc-rtems6-ranlib         rtems-ld
powerpc-rtems6-as         powerpc-rtems6-gcov-dump   powerpc-rtems6-readelf        rtems-ra
powerpc-rtems6-c++        powerpc-rtems6-gcov-tool   powerpc-rtems6-run            rtems-rap
```

>Now you can use the same script (except git clone) for other architectures  by adapting *RTEMS_CPU*. e.g:

>`
>export RTEMS_CPU=arm
>`

Now we install the kernel for the desired BSP (here beatnik).

```
#!/bin/bash
#RTEMS development
export RTEMS_VERSION=6
export RTEMS_RELEASE=6.1
export RTEMS_CPU=powerpc
export RTEMS_BSP=beatnik
export RTEMS_ARCH=${RTEMS_CPU}-rtems${RTEMS_VERSION}
SCRIPT=$(readlink -f $0)
export RTEMS_ROOT=`dirname $SCRIPT`/rtems/${RTEMS_RELEASE}

export PATH=${RTEMS_ROOT}/bin:${PATH}
echo ${PATH}

git clone https://gitlab.rtems.org/rtems/rtos/rtems.git kernel
cd kernel
git checkout origin/6
./waf bspdefaults --rtems-bsps=${RTEMS_CPU}/${RTEMS_BSP} > config.ini
sed -i \
-e "s|RTEMS_POSIX_API = False|RTEMS_POSIX_API = True|" \
-e "s|BUILD_TESTS = False|BUILD_TESTS = True|" \
config.ini

./waf configure --prefix=${RTEMS_ROOT}
./waf
./waf install
```

In *./rtems/6.1/powerpc-rtems6* you should then find the beatnik dependend stuff:

```
rtems@rtems-dev:~/RTEMS_MVME6100_legacy_stack$ ls -l rtems/6.1/powerpc-rtems6/
total 16
drwxr-xr-x  4 rtems rtems 4096 Feb 16 17:33 beatnik
drwxr-xr-x  2 rtems rtems 4096 Feb 16 15:43 bin
drwxr-xr-x 11 rtems rtems 4096 Feb 16 16:13 include
drwxr-xr-x 12 rtems rtems 4096 Feb 16 16:13 lib
```
Now we have to select the desired network stack.

* Legacy network stack, supports old network drivers, old cards 
* LibBSD stack, requires Nexus drivers for network interfaces, prerequisite for e.g. NFSv4

1. MVME6100 with legacy stack:

```
#!/bin/bash
#RTEMS development
export RTEMS_VERSION=6
export RTEMS_RELEASE=6.1
export RTEMS_CPU=powerpc
export RTEMS_BSP=beatnik
export RTEMS_ARCH=${RTEMS_CPU}-rtems${RTEMS_VERSION}
SCRIPT=$(readlink -f $0)
export RTEMS_ROOT=`dirname $SCRIPT`/rtems/${RTEMS_RELEASE}

export PATH=${RTEMS_ROOT}/bin:${PATH}
echo ${PATH}

git clone https://gitlab.rtems.org/rtems/pkg/rtems-net-legacy.git
cd rtems-net-legacy
git checkout origin/6
git submodule init
git submodule update

./waf configure --prefix=${RTEMS_ROOT}
./waf build
./waf install
```

> 2. MVME6100 with libBsd (FreeBSD) stack:
>
> ```
> #!/bin/bash
> #RTEMS development
> export RTEMS_VERSION=6
> export RTEMS_RELEASE=6.1
> export RTEMS_CPU=powerpc
> export RTEMS_BSP=beatnik
> export RTEMS_ARCH=${RTEMS_CPU}-rtems${RTEMS_VERSION}
> SCRIPT=$(readlink -f $0)
> export RTEMS_ROOT=`dirname $SCRIPT`/rtems/${RTEMS_RELEASE}
>
> export PATH=${RTEMS_ROOT}/bin:${PATH}
> echo ${PATH}
> 
> git clone https://gitlab.rtems.org/rtems/pkg/rtems-libbsd.git
> cd rtems-libbsd
> git checkout 6-freebsd-12
> git submodule init
> git submodule update
>
> ./waf configure --prefix=${RTEMS_ROOT}
> ./waf build
> ./waf install
> ```

In order to use network services such as *ntp*, we need to install the rtems-net-services.

```
#!/bin/bash
#RTEMS development
export RTEMS_VERSION=6
export RTEMS_RELEASE=6.1
export RTEMS_CPU=powerpc
export RTEMS_BSP=beatnik
export RTEMS_ARCH=${RTEMS_CPU}-rtems${RTEMS_VERSION}
SCRIPT=$(readlink -f $0)
export RTEMS_ROOT=`dirname $SCRIPT`/rtems/${RTEMS_RELEASE}

export PATH=${RTEMS_ROOT}/bin:${PATH}
echo ${PATH}

git clone https://gitlab.rtems.org/rtems/pkg/rtems-net-services.git
cd rtems-net-services
git checkout origin/6
git submodule init
git submodule update

./waf configure --prefix=${RTEMS_ROOT}
./waf
./waf install
```

## EPICS on RTEMS

Install EPICS in the usual way:

```
mkdir EPICS
cd EPICS
git clone --recursive https://github.com/epics-base/epics-base.git

```
Switch to epics-base which has already been unpacked in the step before.
You have to change a file (*CONFIG\_SITE.Common.RTEMS*) and add another one (*CONFIG_SITE.local*).

```
diff --git a/configure/os/CONFIG_SITE.Common.RTEMS b/configure/os/CONFIG_SITE.Common.RTEMS
index 6857dc9a9..644ee73aa 100644
--- a/configure/os/CONFIG_SITE.Common.RTEMS
+++ b/configure/os/CONFIG_SITE.Common.RTEMS
@@ -13,8 +13,8 @@
 #

 # FHI:
-#RTEMS_VERSION = 5
-#RTEMS_BASE = /home/h1/DBG/rtems
+RTEMS_VERSION = 6
+RTEMS_BASE = /home/rtems/RTEMS_MVME6100_legacy_stack/rtems/6.1
 #RTEMS_BASE = /home/ad/MVME6100/rtems/$(RTEMS_VERSION)
 #RTEMS_BASE = /opt/RTEMS/qoriq/rtems/$(RTEMS_VERSION)
```
```
rtems@rtems-dev:~/RTEMS_MVME6100_legacy_stack/EPICS/epics-base$ cat configure/CONFIG_SITE.local
CROSS_COMPILER_TARGET_ARCHS=RTEMS-beatnik
```

Now it's finally time to build EPICS:

```
make -j20
```

If everything went well, these files should have been build:

```
rtems@rtems-dev:~/RTEMS_MVME6100_legacy_stack/EPICS/epics-base$ ls -l bin/RTEMS-beatnik/
total 420172
-rwxr-xr-x 1 rtems rtems 55349884 Feb 16 18:27 caTestHarness
-rwxr-xr-x 1 rtems rtems  4515040 Feb 16 18:27 caTestHarness.boot
-rwxr-xr-x 1 rtems rtems 21777472 Feb 16 18:25 dbTestHarness
-rwxr-xr-x 1 rtems rtems  2213564 Feb 16 18:25 dbTestHarness.boot
-rwxr-xr-x 1 rtems rtems 21249380 Feb 16 18:25 filterTestHarness
-rwxr-xr-x 1 rtems rtems  2080716 Feb 16 18:25 filterTestHarness.boot
-rwxr-xr-x 1 rtems rtems 19929700 Feb 16 18:25 libComTestHarness
-rwxr-xr-x 1 rtems rtems  1989920 Feb 16 18:25 libComTestHarness.boot
-rwxr-xr-x 1 rtems rtems 21132804 Feb 16 18:25 linkTestHarness
-rwxr-xr-x 1 rtems rtems  2056596 Feb 16 18:25 linkTestHarness.boot
-rwxr-xr-x 1 rtems rtems 53219524 Feb 16 18:28 pvDbTestHarness
-rwxr-xr-x 1 rtems rtems  3411912 Feb 16 18:28 pvDbTestHarness.boot
-rwxr-xr-x 1 rtems rtems 49988884 Feb 16 18:27 pvaTestHarness
-rwxr-xr-x 1 rtems rtems  3478136 Feb 16 18:27 pvaTestHarness.boot
-rwxr-xr-x 1 rtems rtems 39176160 Feb 16 18:25 pvdTestHarness
-rwxr-xr-x 1 rtems rtems  2885528 Feb 16 18:25 pvdTestHarness.boot
-rwxr-xr-x 1 rtems rtems 26978440 Feb 16 18:25 recordTestHarness
-rwxr-xr-x 1 rtems rtems  6118604 Feb 16 18:25 recordTestHarness.boot
-rwxr-xr-x 1 rtems rtems 24487456 Feb 16 18:25 softIoc
-rwxr-xr-x 1 rtems rtems  2819524 Feb 16 18:25 softIoc.boot
-rwxr-xr-x 1 rtems rtems 60756264 Feb 16 18:27 softIocPVA
-rwxr-xr-x 1 rtems rtems  4588816 Feb 16 18:27 softIocPVA.boot
```










