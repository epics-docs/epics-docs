# Installation using MSYS2/MinGW

MSYS2 has all the required tools available
through an easy-to-use package manager,
and its bash shell looks and feels like working on Linux.
Most Bash commands are similar to their Linux versions.
MSYS2 is available for Windows 7 and up only.
The following procedure is verified on Windows 10 and 11 (64 bit).

## Install MSYS2 and tools

MSYS2 provides a Bash shell, Autotools, revision control systems
and other tools for building native Windows applications
using MinGW-w64 toolchains.
It can be installed from its official [website](https://www.msys2.org).
Download and run the installer - "x86_64" for 64-bit Windows.
The installation procedure is well explained on the website.

The default location of the MSYS2 installation is `C:\msys64`.
If you don't have Administrator rights,
you can install MSYS2 in any location you have access to,
e.g. `C:\Users\'user'\msys64` (with 'user' being your Windows
user directory name).
We will assume the default location in this document.

MSYS2 uses a *layered* approach.
Its *MSYS* component provides the foundation:
a POSIX compliance layer and common shared tools:
shells, git, make, tar, autotools, ...
On top of it, different *compiler toolchains*
add their specific tools: compilers, linkers, debuggers,...

To help the user with that complex setup,
each component adds its own *shell* shortcut,
which sets the environment for using the specific toolchain.

::::{important}
**Selecting the Right Shell**

Once installation is complete, you will have several options for starting
a shell in your Start Menu (e.g., "MSYS2 MSYS", "MSYS2 MinGW 64-bit",
"MSYS2 UCRT64", etc.).

* **MSYS2 MSYS**: Use this **only** for system maintenance (like `pacman`).
  It uses a POSIX emulation layer that you generally do **not** want
  for EPICS.
* **MSYS2 MinGW 64-bit**: Use this for building and running EPICS.
  It provides the native Windows compiler toolchain.

:::{warning}
**Crucial:** Always double-check which shell you have opened.
Mixing them up is a common cause of build failures.
:::
::::

Update MSYS2 with following command:

```bash
$ pacman -Syu
```

After this finishes (let it close the bash shell),
open bash again and run the same command again to finish the updates.
The same procedure is used for regular updates of the MSYS2 installation.
An up-to-date system shows something like:

```bash
$ pacman -Syu
:: Synchronizing package databases...
 clangarm64 is up to date
 mingw32 is up to date
 mingw64 is up to date
 ucrt64 is up to date
 clang64 is up to date
 msys is up to date
:: Starting core system upgrade...
 there is nothing to do
:: Starting full system upgrade...
 there is nothing to do
```

Install the necessary tools (perl is already part of the base system):

```bash
$ pacman -S tar make
```

Packages with such "simple" names are part of the MSYS2 environment
and work for all compilers/toolchains that you may install on top on MSYS2.

## Install compiler toolchains

Packages that are part of a MinGW toolchain start with the prefix
"mingw-w64-x86_64-" for the 64bit toolchain or "mingw-w64-i686-"
for the 32bit toolchain.

Install the MinGW 64bit toolchain:

```bash
$ pacman -S mingw-w64-x86_64-toolchain
```

Each complete toolchain needs about 900MB of disk space.
If you want to cut down the needed disk space (to about 50%),
instead of hitting return when asked which packages of the group to install,
you can select the minimal set of packages required for compiling EPICS Base:
`binutils`, `gcc` and `gcc-libs`.

If you are not sure, check your set of tools is complete
and everything is installed properly:

```bash
$ pacman -Q
...
make 4.3-1
perl 5.32.0-2
mingw-w64-x86_64-...
...
```

## Update your installation regularly

As mentioned above, you can update your complete installation
(including all tools and compiler toolchains) at any time using:

```bash
$ pacman -Syu
```

You should do this regularly.

## Download and build EPICS Base

Start the **MSYS2 MinGW 64-bit** shell and do:

```bash
$ cd $HOME
$ wget https://epics-controls.org/download/base/base-7.0.10.tar.gz
$ tar -xvf base-7.0.10.tar.gz
$ cd base-7.0.10
$ export EPICS_HOST_ARCH=windows-x64-mingw
$ make -j<n>
```

The `-j` option enables parallel make: adapt `<n>` to the number of CPU cores on your system.

:::{tip}
If you are connecting to your MSYS2 system through ssh,
you need to set and allow an environment variable to use the environment
presets for the MinGW compilers.
In the MSYS2 configuration of the ssh daemon (`/etc/ssh/sshd_config`),
add the line `AcceptEnv MSYSTEM`,
and on your (local) client configuration (`~/.ssh/config`) add the line
`SetEnv MSYSTEM=MINGW64`.
:::

During the compilation, there will probably be warnings,
but there should be no error.

## Quick test from MSYS2 Bash

As long as you haven't added the location of your programs
to the `PATH` environment variable
(see [installation-windows-env](installation-windows-env.md)),
you will have to provide the whole path to run commands
or `cd` into the directory they are located in
and prefix the command with `./`.

Run `softIoc` and, if everything is ok, you should see an EPICS prompt:

```bash
$ cd /home/'user'/base-7.0.10/bin/windows-x64-mingw
$ ./softIoc -x test
Starting iocInit
############################################################################
## EPICS R7.0.10
## Rev. 2026-06-25T10:56+0200
## Rev. Date build date/time:
############################################################################
iocRun: All initialization complete
epics>
```

You can exit with ctrl-d or by typing exit.

## Quick test from Windows command prompt

Open the Windows command prompt.

If you built EPICS Base with dynamic (DLL) linking,
you need to add the location of the C++ libraries to the `PATH` variable
for them to be found.

```batch
>set "PATH=%PATH%;C:\msys64\mingw64\bin;"
>cd C:\msys64\home\'user'\base-7.0.10\bin\windows-x64-mingw
>softIoc -x test
Starting iocInit
############################################################################
## EPICS R7.0.10
## Rev. 2026-06-25T10:56+0200
## Rev. Date build date/time:
############################################################################
iocRun: All initialization complete
epics>
```

## Create a demo/test IOC

We will create a test ioc from the existing application template
in Base using the `makeBaseApp.pl` script.

Open the **MSYS2 Mingw 64-bit** shell.
Make sure the environment is set up correctly
(see [installation-windows-env](installation-windows-env.md)).
Use the `-use-full-path` argument to inherit your Windows path settings.

Create a new directory `testioc`:

```bash
$ mkdir testioc
$ cd testioc
```

From that `testioc` folder run the following:

```bash
$ makeBaseApp.pl -t ioc test
$ makeBaseApp.pl -i -t ioc test
Using target architecture windows-x64-mingw (only one available)
The following applications are available:
    test
What application should the IOC(s) boot?
The default uses the IOC's name, even if not listed above.
Application name?
```

Accept the default name and press enter.

Now create a `db` file which describes PVs for your `IOC`.
Go to `testApp/Db` and create `test.db` file:

```text
record(ai, "test:pv1")
{
    field(VAL, 49)
}
record(ai, "test:pv2")
{
    field(VAL, 51)
}
record(calc,"test:add")
{
    field(SCAN,"1 second")
    field(INPA, "test:pv1")
    field(INPB, "test:pv2")
    field("CALC", "A + B")
}
```

In the same directory,
open `Makefile` and change the line `#DB += xxx.db` to:

```makefile
DB += test.db
```

Go back to the `iocBoot/ioctest` folder.
Modify the `st.cmd` startup command file.
Change `#dbLoadRecords("db/xxx.db","user=XXX")` to:

```text
dbLoadRecords("db/test.db","user=XXX")
```

Go back to the root folder `~/testioc` and run `make`:

```bash
$ cd ~/testioc
$ make
```

Go to `iocBoot/ioctest`.
Open the `envPaths` file and change the MSYS2 relative paths
to full Windows paths.
Change any back slashes that you might have copied from Windows
to forward slashes.

```text
epicsEnvSet("IOC","ioctest")
epicsEnvSet("TOP","C:/msys64/home/'user'/testioc")
epicsEnvSet("EPICS_BASE","C:/msys64/home/'user'/base-7.0.10")
```

Now run the IOC:

```bash
$ cd ~/testioc/iocBoot/ioctest
$ ../../bin/windows-x64-mingw/test st.cmd
```

:::{tip}
**Check for Success**

If the IOC starts correctly, you will see initialization messages
and an `epics>` prompt. Type `dbl` to verify that your PVs are loaded.
:::
