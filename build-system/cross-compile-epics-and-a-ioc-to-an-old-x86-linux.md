# How To cross compile EPICS and a IOC to an old x86 Linux system

```{tags} developer, advanced
```

## Introduction

I was given the task of developing a IOC which should run in a x86 PC with an old Linux distribution.
My development machine was a x86_64 PC running Ubuntu 12.04.
EPICS does a great job cross compiling from a 64-bits host to a 32-bits target if both have compatible versions of glibc,
binutils,
kernel,
etc.
In my case,
however,
my target had much older versions. I considered two different solutions:

1.  Create a Virtual Machine and install the target's Linux distribution. From the Virtual Machine,
compile EPICS and my IOC,
and then run the IOC in the target
2.  Build a toolchain configured for my target and use that toolchain to compile both EPICS and the IOC.

The first approach is the easiest,
but compiling from inside a VM can be slow and the distribution was not very user friendly.
So I took the second path,
which I'll describe in this document.

## Overview

I'm assuming you, like me, are running Ubuntu 64 bits. I'm also assuming you already have EPICS base downloaded and compiled. We will go through the steps of downloading, configuring and compiling [Crosstool-NG](http://crosstool-ng.org/), which will be used to generate our toolchain. Then we will download and compile a couple of libraries needed by EPICS (namely [readline](https://www.gnu.org/software/readline/) and [ncurses](https://www.gnu.org/software/ncurses/)). Finally, we will compile EPICS base and an example IOC to our target using the newly built toolchain.

## Crosstool-NG

### Downloading and extracting

First we get the tarball containing the source code and extract it.

``` bash
wget http://crosstool-ng.org/download/crosstool-ng/crosstool-ng-1.9.3.tar.bz2
tar -xvf crosstool-ng-1.9.3.tar.bz2
```

Crosstool-NG has a lot of dependencies, you might want to get them before compiling:

``` bash
sudo apt-get install gawk bison flex texinfo automake libtool cvs libcurses5-dev build-essential
```

### Compiling

In order to compile:

``` bash
cd crosstool-ng-1.9.3
./configure --local
make
```

### Configuring

Before configuring Crosstool-NG, I gathered information about my target system:

Kernel Version:

``` console
$ uname -r
2.6.27.27
```

GCC Version:

``` console
$ gcc --version
gcc (GCC) 4.2.4
```

glibc version:

``` console 
$ /lib/libc.so.6
GNU C Library stable release version 2.7, by Roland McGrath et al.
```

binutils version:

``` console
$ ld --version
GNU ld (Linux/GNU Binutils) 2.18.50.0.9.20080822
```

Based on this information, and on a lot of trial and error, I configured Crosstool-NG as follows (everything else set as default):

``` console
$ ./ct-ng menuconfig

PATHS AND MISC OPTIONS
   [*] Use obsolete features
   
TARGET OPTIONS
   Target architecture (x86)
   Bitness: (32-bit)
   (i686) Architecture Level
   
OPERATING SYSTEM
   Target OS (linux)
   Linux kernel version (2.6.27.55)
   
BINARY UTILITIES
   Binutils version (2.17)
   
C-COMPILER
   GCC version (4.2.4)
   [*] C++
   
C-LIBRARY
   glibc version (2.6.1)
   
```

I tried other configurations, but they crashed the compilation process.

### Compiling the toolchain

Now we can compile the toolchain:

``` bash
./ct-ng build
```

This will take a while. Go get some coffee or watch a cat video on Youtube.

Once built, the toolchain will be in `$HOME/x-tools/i686-unknown-linux-gnu/`

It's a good idea (I think) to put the cross-compiler binaries on your path. Add this to the end of your ~/.bashrc:

``` bash
PATH=$PATH:$HOME/x-tools/i686-unknown-linux-gnu/bin
```

Then source your .bashrc, so the changes take effect.

``` bash
. ~/.bashrc
```

## EPICS dependencies

In order to properly build epics-base to our target system, we have to take care of EPICS dependencies first. Namely, the libraries 'readline' and 'ncurses'.

They will be installed in our toolchain directory. We have to make it writable:

``` bash
chmod -R +w $HOME/x-tools/i686-unknown-linux-gnu/i686-unknown-linux-gnu/sys-root/usr
```

Now we can download, configure, compile and install the libraries.

### readline

``` bash
wget ftp://ftp.cwru.edu/pub/bash/readline-6.2.tar.gz
tar -xvf readline-6.2.tar.gz
cd readline-6.2
./configure --prefix=$HOME/x-tools/i686-unknown-linux-gnu/i686-unknown-linux-gnu/sys-root/usr --host=i686-unknown-linux-gnu
make
make install
```

### ncurses

``` bash
wget ftp://ftp.gnu.org/pub/gnu/ncurses/ncurses-5.9.tar.gz
tar -xvf ncurses-5.9.tar.gz
cd ncurses-5.9
./configure --prefix=$HOME/x-tools/i686-unknown-linux-gnu/i686-unknown-linux-gnu/sys-root/usr --host=i686-unknown-linux-gnu
make
make install
```

## Configure cross-compilation in EPICS

We're almost done. Back to the epics-base directory, open the file: `$EPICS_BASE/configure/CONFIG_SITE`

Change the line:

``` makefile
CROSS_COMPILER_TARGET_ARCHS=
```

To:

``` makefile
CROSS_COMPILER_TARGET_ARCHS=linux-686
```

This tells EPICS base to be compiled both for the host system and for the linux-686 target.

Save and close. Now we will create our own target configuration file, based on a existing file.

``` bash
cd $EPICS_BASE/configure/os
cp CONFIG_SITE.Common.linux-x86 CONFIG_SITE.Common.linux-686
```

Open `CONFIG_SITE.Common.linux-686` and edit it. Comment out the line:

``` makefile
#COMMANDLINE_LIBRARY = READLINE
```

And uncomment:

``` makefile
COMMANDLINE_LIBRARY = READLINE_NCURSES
```

At the end of the file, add the lines:

``` makefile
GNU_DIR=$HOME/x-tools/i686-unknown-linux-gnu
GNU_TARGET=i686-unknown-linux-gnu
```

This tells EPICS to search for both readline and ncurses libraries during compilation. The last two lines indicate the location of the toolchain and its prefix. Save and close. Last file to edit: CONFIG.Common.linux-686

Change the line that says

``` makefile
VALID_BUILDS = Ioc
```

To

``` makefile
VALID_BUILDS = Host Ioc
```

This is needed in order to get caRepeater compiled, according to [this source](https://epics.anl.gov/tech-talk/2012/msg01102.php).

### Recompile EPICS base

Now, we recompile EPICS base:

``` bash
make clean uninstall
make
```

Hopefully, we have everything in place to start developing our IOC's.

## Example IOC

Let's create a working directory for our programs. I decided to call it 'apps':

``` bash
mkdir ~/apps
```

### Creating

To create an example IOC, we use a Perl script provided by EPICS:

``` bash
cd ~/apps
mkdir myexample
cd myexample
makeBaseApp.pl -t example myexample
```

The last command tells the script to create an application named 'myexample' using the template (option -t) 'example'. Now we make our IOC bootable

``` bash
makeBaseApp.pl -i -t example myexample
```

It will ask you what the target is. We went to all this trouble to be able to select:

``` bash
linux-686
```

For the Application Name, just hit enter.

### Configuring

Add this line to the file `~/apps/myexample/configure/CONFIG_SITE`

``` makefile
STATIC_BUILD=YES
```

This will statically link EPICS libraries into our executable.

Now, let's consider that you will put your IOC in the folder /home of your target system. Edit the file ~/apps/myexample/iocBoot/iocmyexample/envPaths, so it will be:

``` csh
epicsEnvSet("ARCH","linux-686")
epicsEnvSet("IOC","iocskel")
epicsEnvSet("TOP","/home/myexample")
epicsEnvSet("EPICS_BASE","/home/myexample")
```

Note that we set EPICS base to coincide with the <top> folder of our IOC. I did it because the IOC depends on the caRepeater program, which would be present in an EPICS base if we had one in our target. Because we don't, I'll simply copy the caRepeater generated by the host to the the /bin folder of our IOC <top> folder:

``` bash
cp $EPICS_BASE/bin/linux-686/caRepeater ~/apps/myexample/bin/linux-686/
```

### Compiling

Compile the IOC and prepare it for execution.

``` bash
make
chmod +x iocBoot/iocmyexample/st.cmd
```

Note that you won't be able to run the IOC in your host system, given that it was compiled to our target system. You won't be able to run it in your target system neither, as your target lacks three libraries: two needed by caRepeater and one needed by the IOC.

First, take care of the libraries needed by caRepeater:

``` bash
mkdir ~/apps/myexample/lib
mkdir ~/apps/myexample/lib/linux-686/
cp $EPICS_BASE/lib/linux-686/libca.so.3.14 ~/apps/myexample/lib/linux-686
cp $EPICS_BASE/lib/linux-686/libCom.so.3.14 ~/apps/myexample/lib/linux-686
```

Then copy libreadline from your host's folder:

``` bash
~/x-tools/i686-unknown-linux-gnu/i686-unknown-linux-gnu/sys-root/usr/lib/libreadline.so.6.2
```

To your target's folder:

``` bash
/lib/libreadline.so.6
```

Please note the change in the filename.

### Executing

After copying your myexample folder to your target's /home folder, you can run your IOC:

``` bash
cd /home/myexample/iocBoot/iocmyexample
./st.cmd
```

If everything goes as expected, you will have an epics prompt:

``` console
epics>
```

Try listing the records:

``` console
epics> dbl
bruno:ai1
bruno:ai2
bruno:ai3
bruno:aiExample
bruno:aiExample1
bruno:aiExample2
bruno:aiExample3
bruno:aSubExample
bruno:calc1
bruno:calc2
bruno:calc3
bruno:calcExample
bruno:calcExample1
bruno:calcExample2
bruno:calcExample3
bruno:compressExample
bruno:subExample
bruno:xxxExample
```

