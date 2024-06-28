# Installation on RTEMS 6

```{tags} developer, advanced
```

## RTEMS 6 Information

Unfortunately, RTEMS 6 has not yet been released at the time of writing. This page provides a advice on using the RTEMS Source Builder to build the RTEMS tools, kernel and 3rd party packages from source. The process for creating this environment is documented [here] (https://docs.rtems.org/branches/master/user/rsb/index.html#). If you discover any other information that ought to be published here, please [let me know](mailto:junkes@fhi.mpg.de).

Please note that we are specifically addressing the hardware used in the EPICS environment, primarily with RTEMS.

*   VMEbus CPUs (MVME3100, MVME6100, MVME2500)
*   Development boards (Beagleboneblack, ZYBO Z7-20, ...)
*   Qemu - Support e.g. xilinx\_zynq\_a9\_qemu

In order to support these systems, the tools for the *arm* and *powerpc* architectures must be installed.

The environment was installed on an M2 Mac. It is helpful to create a virtual hard disc with a case-sensitive APFS file system (e.g. /Volumes/Epics): ![](media/Mac_AFPFS.png)

The following installation script refers to a path in this volume.

``` 
junkes@Zarquon RTEMS_FOR_EPICS % pwd
/Volumes/Epics/LONG_ISLAND/RTEMS_FOR_EPICS
junkes@Zarquon RTEMS_FOR_EPICS % more INSTALLING_6 
#!/bin/bash
# ----
# RTEMS6 tools for arm architecture
# ----

export RTEMS_VERSION=6
export RTEMS_CPU=arm
export RTEMS_ARCH=${RTEMS_CPU}-rtems${RTEMS_VERSION}
export RTEMS_ROOT=/Volumes/Epics/LONG_ISLAND/RTEMS_FOR_EPICS/rtems/${RTEMS_VERSION}

#install rsb and rtems arm tools
git clone https://gitlab.rtems.org/rtems/tools/rtems-source-builder.git  rsb
cd rsb/rtems
../source-builder/sb-check
if [ $? -ne 0 ]; then
    echo "sb check failed"
    exit
fi
echo "... check ok ... proceed ..."
../source-builder/sb-set-builder --list-bsets
echo "... building tool set for " ${RTEMS_CPU}
../source-builder/sb-set-builder --warn-all --log --no-clean \
--with-python-version=python3.12 --prefix=${RTEMS_ROOT} \
${RTEMS_VERSION}/rtems-${RTEMS_CPU}
if [ $? -ne 0 ]; then
    echo "building failed"
    exit
fi
```
In */Volumes/Epics/LONG_ISLAND/RTEMS\_FOR\_EPICS/rtems/6/bin* you should find the arm-tools:

```
junkes@Zarquon RTEMS_FOR_EPICS % ls rtems/6/bin 
arm-rtems6-addr2line		arm-rtems6-ld			mkimage.py
arm-rtems6-ar			arm-rtems6-ld.bfd		rtems-addr2line
arm-rtems6-as			arm-rtems6-lto-dump		rtems-bin2c
arm-rtems6-c++			arm-rtems6-nm			rtems-boot-image
arm-rtems6-c++filt		arm-rtems6-objcopy		rtems-bsp-builder
arm-rtems6-cpp			arm-rtems6-objdump		rtems-exeinfo
arm-rtems6-elfedit		arm-rtems6-ranlib		rtems-ld
arm-rtems6-g++			arm-rtems6-readelf		rtems-ra
arm-rtems6-gcc			arm-rtems6-run			rtems-rap
arm-rtems6-gcc-13.3.0		arm-rtems6-size			rtems-record-lttng
arm-rtems6-gcc-ar		arm-rtems6-strings		rtems-run
arm-rtems6-gcc-nm		arm-rtems6-strip		rtems-syms
arm-rtems6-gcc-ranlib		convert-dtsv0			rtems-test
arm-rtems6-gcov			dtc				rtems-tftp-proxy
arm-rtems6-gcov-dump		dtdiff				rtems-tftp-server
arm-rtems6-gcov-tool		fdtdump				rtems-tld
arm-rtems6-gdb			fdtget				trace-converter
arm-rtems6-gdb-add-index	fdtoverlay
arm-rtems6-gprof		fdtput
```

Now you can use the same script (except git clone) for other architectures  by adapting *RTEMS_CPU*. e.g:

`
export RTEMS_CPU=powerpc
`

After that (! takes a little longer) you have also created tools for the *powerpc* architecture:

```
junkes@Zarquon RTEMS_FOR_EPICS % ls rtems/6/bin 
arm-rtems6-addr2line		arm-rtems6-strings		powerpc-rtems6-ld
arm-rtems6-ar			arm-rtems6-strip		powerpc-rtems6-ld.bfd
arm-rtems6-as			convert-dtsv0			powerpc-rtems6-lto-dump
arm-rtems6-c++			dtc				powerpc-rtems6-nm
arm-rtems6-c++filt		dtdiff				powerpc-rtems6-objcopy
arm-rtems6-cpp			fdtdump				powerpc-rtems6-objdump
arm-rtems6-elfedit		fdtget				powerpc-rtems6-ranlib
arm-rtems6-g++			fdtoverlay			powerpc-rtems6-readelf
arm-rtems6-gcc			fdtput				powerpc-rtems6-run
arm-rtems6-gcc-13.3.0		mkimage.py			powerpc-rtems6-size
arm-rtems6-gcc-ar		powerpc-rtems6-addr2line	powerpc-rtems6-strings
arm-rtems6-gcc-nm		powerpc-rtems6-ar		powerpc-rtems6-strip
arm-rtems6-gcc-ranlib		powerpc-rtems6-as		rtems-addr2line
arm-rtems6-gcov			powerpc-rtems6-c++		rtems-bin2c
arm-rtems6-gcov-dump		powerpc-rtems6-c++filt		rtems-boot-image
arm-rtems6-gcov-tool		powerpc-rtems6-cpp		rtems-bsp-builder
arm-rtems6-gdb			powerpc-rtems6-elfedit		rtems-exeinfo
arm-rtems6-gdb-add-index	powerpc-rtems6-g++		rtems-ld
arm-rtems6-gprof		powerpc-rtems6-gcc		rtems-ra
arm-rtems6-ld			powerpc-rtems6-gcc-13.3.0	rtems-rap
arm-rtems6-ld.bfd		powerpc-rtems6-gcc-ar		rtems-record-lttng
arm-rtems6-lto-dump		powerpc-rtems6-gcc-nm		rtems-run
arm-rtems6-nm			powerpc-rtems6-gcc-ranlib	rtems-syms
arm-rtems6-objcopy		powerpc-rtems6-gcov		rtems-test
arm-rtems6-objdump		powerpc-rtems6-gcov-dump	rtems-tftp-proxy
arm-rtems6-ranlib		powerpc-rtems6-gcov-tool	rtems-tftp-server
arm-rtems6-readelf		powerpc-rtems6-gdb		rtems-tld
arm-rtems6-run			powerpc-rtems6-gdb-add-index	trace-converter
arm-rtems6-size			powerpc-rtems6-gprof
```

Once the tools have been installed, the RTEMS kernel must now be created for the various boards. This can also be done with the RTEMS source builder, but also manually ([RTEMS docs](https://docs.rtems.org/branches/master/user/start/bsp-build.html#)).

Example RTEMS source builder (MVME2500, in *rsb/rtems*):

```
#!//bin/bash

export RTEMS_VERSION=6
export RTEMS_CPU=powerpc
export RTEMS_BSP=qoriq_e500
export RTEMS_ARCH=${RTEMS_CPU}-rtems${RTEMS_VERSION}
export RTEMS_ROOT=/Volumes/Epics/LONG_ISLAND/RTEMS_FOR_EPICS/rtems/${RTEMS_VERSION}

echo "... building kernel set for " ${RTEMS_CPU}/${RTEMS_BSP}

../source-builder/sb-set-builder --jobs=20 --prefix=${RTEMS_ROOT} \
--target=${RTEMS_CPU}-rtems${RTEMS_VERSION} \
--with-rtems-bsp=${RTEMS_CPU}/${RTEMS_BSP} \
--with-rtems-tests=yes ${RTEMS_VERSION}/rtems-kernel

if [ $? -ne 0 ]; then
    echo "building failed"
    exit
fi

```
To find out which BSPs are supported by the RTEMS source builder:

`
source-builder/sb-set-builder --list-bsets
`

Example manualy (MVME6100, in */Volumes/Epics/LONG_ISLAND/RTEMS\_FOR\_EPICS*):

```
#!/bin/bash

export RTEMS_VERSION=6
export RTEMS_CPU=powerpc
export RTEMS_BSP=beatnik
export RTEMS_ARCH=${RTEMS_CPU}-rtems${RTEMS_VERSION}
export RTEMS_ROOT=/Volumes/Epics/LONG_ISLAND/RTEMS_FOR_EPICS/rtems/${RTEMS_VERSION}

export PATH=${RTEMS_ROOT}/bin:${PATH}
echo ${PATH}

# building kernel
https://gitlab.rtems.org/rtems/rtos/rtems.git
cd kernel
./waf bspdefaults --rtems-bsps=${RTEMS_CPU}/${RTEMS_BSP} > config.ini
sed -i '' \
-e "s|RTEMS_POSIX_API = False|RTEMS_POSIX_API = True|" \
-e "s|BUILD_TESTS = False|BUILD_TESTS = True|" \
config.ini

./waf configure --prefix=${RTEMS_ROOT}
./waf
./waf install

```
To find out which BSPs are supported by the RTEMS kernel:

`
rtems-bsps 
`

Now we can create the other BSPs (with the RTEMS source builder mode).

```
./waf bspdefaults --rtems-bsps=arm/beagleboneblack > config.ini
sed -i ...
./waf confgiure ...
./waf
./waf install

./waf bspdefaults --rtems-bsps=arm/xilinx_zynq_a9_qemu >config.ini

./waf bspdefaults --rtems-bsps=powerpc/mvme3100 >config.ini

```

Now we can select the desired network stack per BSP. The following are available:

* Legacy network stack, supports old network drivers, old cards 
* LibBSD stack, requires Nexus drivers for network interfaces, prerequisite for e.g. NFSv3

1. MVME6100 with legacy stack:


```
../source-builder/sb-set-builder --jobs=20 --prefix=${RTEMS_ROOT} \
${RTEMS_VERSION}/rtems-net-legacy --host=powerp-rtems6 \
--with-rtems-bsp=powerpc/beatnik  

Unfortunately, the main-repo has an error at the time of this writing. 
```

2. MVME2500 with libBsd stack:

```
Unfortunately, the main-repo has an error at the time of this writing.
```
As the RTEMS source builder system contains a bug at the time of writing this guide, we install the network stacks manually (see *README.waf* in the repos).

3. MVME6100 with legacy stack (manualy with waf):

```
git clone https://gitlab.rtems.org/rtems/pkg/rtems-net-legacy.git
cd rtems-net-legacy

git submodule init
git submodule update

git checkout remotes/origin/6-freebsd-12

./waf configure --prefix=${RTEMS_ROOT} --rtems-bsps=powerpc/beatnik
./waf build install
```

4. MVME2500 with libBsd stack:

```
git clone https://gitlab.rtems.org/rtems/pkg/rtems-libbsd

git submodule init
git submodule update rtems_waf

git checkout remotes/origin/6-freebsd-12

./waf configure --prefix=${RTEMS_ROOT} --rtems-bsps=powerpc/qoriq_e500 \
--buildset=buildset/default.ini
./waf
./waf install
```

5. The other systems:

```
./waf configure --prefix=${RTEMS_ROOT} --rtems-bsps=arm/beagleboneblack \
--buildset=buildset/default.ini
./waf
./waf install

./waf configure --prefix=${RTEMS_ROOT} \
--rtems-bsps=arm/xilinx_zynq_a9_qemu --buildset=buildset/default.ini
./waf
./waf install
 
./waf configure --prefix=${RTEMS_ROOT} --rtems-bsps=powerpc/mvme3100 \
--buildset=buildset/default.ini
./waf
./waf install
```

### Use of RTEMS 

In the first step, we will now concentrate on a qemu variant:

*xilinx\_zynq\_a9\_qemu*

Run tests with this target:

```

junkes@Zarquon rtems-libbsd % ../rtems/6/bin/rtems-test --rtems-bsp=xilinx_zynq_a9_qemu build
RTEMS Testing - Tester, 6.0.not_released
 Command Line: ../rtems/6/bin/rtems-test --rtems-bsp=xilinx_zynq_a9_qemu build
 Host: Darwin Zarquon.local 23.5.0 Darwin Kernel Version 23.5.0: Wed May  1 20:14:38 PDT 2024; root:xnu-10063.121.3~5/RELEASE_ARM64_T6020 arm64
 Python: 3.11.9+ (heads/3.11:35c799d, Jun 12 2024, 20:06:09) [Clang 15.0.0 (clang-1500.3.9.4)]
Host: macOS-14.5-arm64-arm-64bit (Darwin Zarquon.local 23.5.0 Darwin Kernel Version 23.5.0: Wed May  1 20:14:38 PDT 2024; root:xnu-10063.121.3~5/RELEASE_ARM64_T6020 arm64 arm)
[  2/226] p:0   f:0   u:0   e:0   I:0   B:0   t:0   L:0   i:0   W:0   | arm/xilinx_zynq_a9_qemu: cdev01.exe
[  1/226] p:0   f:0   u:0   e:0   I:0   B:0   t:0   L:0   i:0   W:0   | arm/xilinx_zynq_a9_qemu: arphole.exe
[  3/226] p:0   f:0   u:0   e:0   I:0   B:0   t:0   L:0   i:0   W:0   | arm/xilinx_zynq_a9_qemu: commands01.exe
[  4/226] p:0   f:0   u:0   e:0   I:0   B:0   t:0   L:0   i:0   W:0   | arm/xilinx_zynq_a9_qemu: condvar01.exe
[  6/226] p:0   f:0   u:0   e:0   I:0   B:0   t:0   L:0   i:0   W:0   | arm/xilinx_zynq_a9_qemu: debugger01.exe
[  9/226] p:0   f:0   u:0   e:0   I:0   B:0   t:0   L:0   i:0   W:0   | arm/xilinx_zynq_a9_qemu: epoch01.exe
[  7/226] p:0   f:0   u:0   e:0   I:0   B:0   t:0   L:0   i:0   W:0   | arm/xilinx_zynq_a9_qemu: dhcpcd01.exe
[  5/226] p:0   f:0   u:0   e:0   I:0   B:0   t:0   L:0   i:0   W:0   | arm/xilinx_zynq_a9_qemu: crypto01.exe
[ 11/226] p:0   f:0   u:0   e:0   I:0   B:0   t:0   L:0   i:0   W:0   | arm/xilinx_zynq_a9_qemu: foobarclient.exe
...
```

## EPICS on RTEMS

### First we use the virtual CPU *xilinx\_zynq\_a9\_qemu* to test, install and configure EPICS:

We are currently using an adaptation of EPICS to RTEMS by Chris Johns. This customisation can only be meaningfully integrated into EPICS when an RTEMS6 release (6.1?) is available.

```
git clone --recursive https://github.com/kiwichris/epics-base.git

cd epics-base
git checkout rtems-ntpd-7_0
M	.ci
M	modules/pvAccess
M	modules/pvData
M	modules/pvDatabase
M	modules/pva2pva
Switched to branch 'rtems-ntpd-7_0'
Your branch is up to date with 'origin/rtems-ntpd-7_0'.
```
This NTP support requires the *rtems-net-services* package.

Unpack this in the same place as the other packages. (here : */Volumes/Epics/LONG\_ISLAND/RTEMS\_FOR\_EPICS/*)

```
junkes@Zarquon RTEMS_FOR_EPICS % git clone \
https://gitlab.rtems.org/rtems/pkg/rtems-net-services.git
Cloning into 'rtems-net-services'...
remote: Enumerating objects: 806, done.
remote: Counting objects: 100% (31/31), done.
remote: Compressing objects: 100% (26/26), done.
remote: Total 806 (delta 16), reused 6 (delta 5), pack-reused 775 (from 1)
Receiving objects: 100% (806/806), 1.29 MiB | 469.00 KiB/s, done.
Resolving deltas: 100% (250/250), done.

cd rtems-net-services

git submodule init
git submodule update

./waf configure --prefix=${RTEMS_ROOT} --rtems-bsps=arm/xilinx_zynq_a9_qemu
./waf
./waf install
```

Switch to epics-base which has already been unpacked in the step before.
You have to change a file (*CONFIG\_SITE.Common.RTEMS*) and add another one (*CONFIG_SITE.local*).

```
diff --git a/configure/os/CONFIG_SITE.Common.RTEMS b/configure/os/CONFIG_SITE.Common.RTEMS
index 6857dc9a9..c3eb195e0 100644
--- a/configure/os/CONFIG_SITE.Common.RTEMS
+++ b/configure/os/CONFIG_SITE.Common.RTEMS
@@ -12,11 +12,9 @@
 #    used, but for RTEMS 4.10.2 say all 3 components are required.
 #
 
-# FHI:
-#RTEMS_VERSION = 5
-#RTEMS_BASE = /home/h1/DBG/rtems
-#RTEMS_BASE = /home/ad/MVME6100/rtems/$(RTEMS_VERSION)
-#RTEMS_BASE = /opt/RTEMS/qoriq/rtems/$(RTEMS_VERSION)
+# Docu (LONG_ISLAND) 
+RTEMS_VERSION = 6
+RTEMS_BASE = /Volumes/Epics/LONG_ISLAND/RTEMS_FOR_EPICS/rtems/$(RTEMS_VERSION)
 
 # APS:
 #RTEMS_VERSION = 4.10.2
```
```
junkes@Zarquon epics-base % cat configure/CONFIG_SITE.local 
# Which target architectures to cross-compile for.
#  Definitions in configure/os/CONFIG_SITE.<host>.Common
#  may override this setting.
CROSS_COMPILER_TARGET_ARCHS=RTEMS-xilinx_zynq_a9_qemu

```

Now it's finally time to build EPICS:

```
make -j20
```

If everything went well, these files should have been build:

```
junkes@Zarquon epics-base % ls -l bin/RTEMS-xilinx_zynq_a9_qemu 
total 1123032
-r-xr-xr-x  1 junkes  staff  71442428 Jun 13 19:49 caTestHarness
-r-xr-xr-x  1 junkes  staff  37341856 Jun 13 19:46 dbTestHarness
-r-xr-xr-x  1 junkes  staff  37029604 Jun 13 19:46 filterTestHarness
-r-xr-xr-x  1 junkes  staff  37749336 Jun 13 19:44 libComTestHarness
-r-xr-xr-x  1 junkes  staff  36900052 Jun 13 19:46 linkTestHarness
-r-xr-xr-x  1 junkes  staff  69569588 Jun 13 19:51 pvDbTestHarness
-r-xr-xr-x  1 junkes  staff  66885168 Jun 13 19:49 pvaTestHarness
-r-xr-xr-x  1 junkes  staff  56490036 Jun 13 19:47 pvdTestHarness
-r-xr-xr-x  1 junkes  staff  42492076 Jun 13 19:46 recordTestHarness
-r-xr-xr-x  1 junkes  staff  41951972 Jun 13 19:45 softIoc
-r-xr-xr-x  1 junkes  staff  77118252 Jun 13 19:52 softIocPVA
```

On OS-x you have to create a virtual network first:

```
brew install socket_vmnet
brew tap homebrew/services
sudo brew services start socket_vmnet
export PATH="$(brew --prefix)/opt/socket_vmnet/bin:${PATH}"
ping 192.168.105.1
```

Run qemu:

```
#!/bin/bash

if [[ $# != 1 ]] ; then
  echo 'USAGE: startQemu  kernelFile'
  exit 0
fi
socket_vmnet_client "$(brew --prefix)/var/run/socket_vmnet" \
qemu-system-arm -M xilinx-zynq-a9 -m 256M -no-reboot \
-netdev socket,id=net0,fd=3 \
-net nic,model=cadence_gem,netdev=net0 \
-serial null -serial mon:stdio -nographic \
-kernel $1 

```

### EPICS on *MVME2500*:

You now only have to define the CPU to be used in *configure/CONFIG_SITE.local*.

```
# Which target architectures to cross-compile for.
#  Definitions in configure/os/CONFIG_SITE.<host>.Common
#  may override this setting.
CROSS_COMPILER_TARGET_ARCHS=RTEMS-qoriq_e500
```

And then just *make* in *epics-base* and then these files should have been created:

```
junkes@Zarquon epics-base % ls -l bin/RTEMS-qoriq_e500
total 1325888
-r-xr-xr-x  1 junkes  staff  78069060 Jun 14 15:39 caTestHarness
-r-xr-xr-x  1 junkes  staff   3602181 Jun 14 15:39 caTestHarness.img
-r-xr-xr-x  1 junkes  staff  44413800 Jun 14 15:36 dbTestHarness
-r-xr-xr-x  1 junkes  staff   2909146 Jun 14 15:36 dbTestHarness.img
-r-xr-xr-x  1 junkes  staff  43996400 Jun 14 15:36 filterTestHarness
-r-xr-xr-x  1 junkes  staff   2871002 Jun 14 15:36 filterTestHarness.img
-r-xr-xr-x  1 junkes  staff  42711488 Jun 14 15:34 libComTestHarness
-r-xr-xr-x  1 junkes  staff   2828122 Jun 14 15:34 libComTestHarness.img
-r-xr-xr-x  1 junkes  staff  43900348 Jun 14 15:36 linkTestHarness
-r-xr-xr-x  1 junkes  staff   2862360 Jun 14 15:36 linkTestHarness.img
-r-xr-xr-x  1 junkes  staff  75589688 Jun 14 15:41 pvDbTestHarness
-r-xr-xr-x  1 junkes  staff   3290916 Jun 14 15:41 pvDbTestHarness.img
-r-xr-xr-x  1 junkes  staff  72761140 Jun 14 15:39 pvaTestHarness
-r-xr-xr-x  1 junkes  staff   3330423 Jun 14 15:39 pvaTestHarness.img
-r-xr-xr-x  1 junkes  staff  62018472 Jun 14 15:37 pvdTestHarness
-r-xr-xr-x  1 junkes  staff   3106730 Jun 14 15:37 pvdTestHarness.img
-r-xr-xr-x  1 junkes  staff  49704560 Jun 14 15:36 recordTestHarness
-r-xr-xr-x  1 junkes  staff   3171153 Jun 14 15:36 recordTestHarness.img
-r-xr-xr-x  1 junkes  staff  47257792 Jun 14 15:36 softIoc
-r-xr-xr-x  1 junkes  staff   3163484 Jun 14 15:36 softIoc.img
-r-xr-xr-x  1 junkes  staff  83454452 Jun 14 15:42 softIocPVA
-r-xr-xr-x  1 junkes  staff   3800174 Jun 14 15:42 softIocPVA.img

```

### Teststand
We are also in the process of setting up a hardware test stand for EPICS developments. Access to this is not yet fully organised. However, it is already being used here.

( Description with network diagram to follow )


In order to execute an application, the *img* file must be transferred to an NFS share and then loaded by the CPU via tftp.

```
scp bin/RTEMS-qoriq_e500/libComTestHarness.img xxx@nfs:/srv/tftp/vmeTest.img
```

Now you can trigger a reset of the board. The image is then loaded and *Epics-rtems_init* stops for diagnostics in an RTEMS shell:

```
rtems@rtems-dev:~$ telnet moxa-vme 4001
Trying 141.14.128.77...
Connected to moxa-vme.fhi.mpg.de.
Escape character is '^]'.

U-Boot 2013.01 (Aug 23 2016 - 12:17:55)

CPU:   P2010E, Version: 2.1, (0x80eb0021)
Core:  E500, Version: 5.1, (0x80211051)
Clock Configuration:
       CPU0:800  MHz, 
       CCB:400  MHz,
       DDR:400  MHz (800 MT/s data rate) (Asynchronous), LBC:25   MHz
L1:    D-cache 32 kB enabled
       I-cache 32 kB enabled
Board: MVME2500
       Emerson Network Power, Embedded Computing
       Monitor Version: 2.8
       FPGA Seq.Ver: 2.5
       Is VME system controller
I2C:   ready
SPI:   ready
DRAM:  Initializing....    DDR: 1 GiB (DDR3, 64-bit, CL=6, ECC on)
L2:    512 KB enabled
MMC:  FSL_SDHC: 0
8192 KiB AT25DF641 at 0:0 is now current device
EEPROM: Read MAC Address
PCIe1: Root Complex of Slot 2, x1, regs @ 0xffe0a000
  01:00.0     - 10e3:8114 - Bridge device
   02:01.0    - 10e3:0148 - Bridge device
PCIe1: Bus 00 - 02
PCIe2: Root Complex of Slot 1, x1, regs @ 0xffe09000
  04:00.0     - 11ab:6121 - Mass storage controller
PCIe2: Bus 03 - 04
PCIe3: Root Complex, no link, regs @ 0xffe08000
PCIe3: Bus 05 - 05
In:    serial
Out:   serial
Err:   serial

Ser#: E113E4C
I-cache enabled. (L1CSR1: 0x00000001)
D-cache enabled. (L1CSR0: 0x00000001) (write-through)
SCSI:  SATA link 0 timeout.
SATA link 1 timeout.
AHCI 0001.0000 32 slots 3 ports 3 Gbps 0x7 impl IDE mode
flags: 64bit ncq stag led pmp slum part 
scanning bus for devices...
Found 0 device(s).
Net:   eTSEC1, eTSEC2, eTSEC3
Bootreg = a6 BootDev: SPI0   Switch: SPI0
Enable SPI WP: 
8192 KiB AT25DF641 at 0:0 is now current device
8192 KiB AT25DF641 at 0:1 is now current device
Autoboot in  3 seconds (hit 'h' to stop)
reading mvme2500.dtb
12363 bytes read in 13 ms (928.7 KiB/s)
Speed: 1000, full duplex
Using eTSEC1 device
TFTP from server 141.14.131.192; our IP address is 141.14.128.89
Filename 'vmeTest.img'.
Load address: 0x10000000
Loading: T #################################################################
	 #################################################################
	 ###############################################################
	 529.3 KiB/s
done
Bytes transferred = 2828122 (2b275a hex)
WARNING: adjusting available memory to 30000000
## Booting kernel from Legacy Image at 10000000 ...
   Image Name:   libComTestHarness
   Created:      2024-06-14  13:34:48 UTC
   Image Type:   PowerPC Linux Kernel Image (gzip compressed)
   Data Size:    2828058 Bytes = 2.7 MiB
   Load Address: 00004000
   Entry Point:  00004000
   Verifying Checksum ... OK
## Flattened Device Tree blob at 20000000
   Booting using the fdt blob at 0x20000000
   Uncompressing Kernel Image ... OK
   Loading Device Tree to 03ff9000, end 03fff04a ... OK
ntpd: RTEMS service init
Clock synchronization must be performed by the OS

 initConsole --- Info ---
stdin: fileno: 0, ttyname: /dev/ttyS0
stdout: fileno: 1, ttyname: /dev/ttyS0
stderr: fileno: 2, ttyname: /dev/ttyS0
time set to : 04/14/14 07:30:06.000003899 UTC
Startup.
epicsThreadSetPriority called by non epics thread

***** RTEMS Version: rtems-6.0.0 (PowerPC/Generic (no FPU)/qoriq_e500) *****

RTEMS Shell on /dev/console. Use 'help' to list commands.
SHLL [/] # 
```










