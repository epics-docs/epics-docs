# Installation using plain Windows and the Visual Studio compilers

This procedure will need Administrator rights on the Windows machine.

## Install tools

There are two reasonable options.

### Using Chocolatey

Go to the [Chocolatey website](https://chocolatey.org/)
and follow their instructions to download and install the package manager.

Using the Chocolatey package manager,
install Strawberry Perl and Gnu Make.

### Manually

Install Strawberry Perl or ActivePerl using the Windows installers
available on their download pages.

Strawberry Perl contains a suitable version of GNU Make.
Otherwise, you can download a Windows executable that Andrew provides at
<https://epics.anl.gov/download/tools/make-4.2.1-win64.zip>.
Unzip it into a location (path must not contain spaces or parentheses)
and add it to the system environment.

### Put tools in the Path

Make sure the tools' locations are added to the system environment
variable Path.
Inside a shell (command prompt) they must be callable
using their simple name, e.g.:

```batch
>perl --version
```

:::{important}
**Tool Verification**

Before proceeding, ensure both `perl` and `make` (or `gmake`) are available
in your command prompt. Type `perl --version` and `make --version`
to verify. If they are not found, double-check your `Path` environment
variable settings.
:::

## Install the compiler

Download the Visual Studio Installer and install
(the community edition is free to use for open source projects).
Make sure you enable the **Desktop development with C++** workload.

:::{tip}
**Why Visual Studio?**

This tool chain is often chosen
when you need to link against vendor-provided binary libraries
(like camera SDKs or DAQ drivers)
that are only distributed as `.lib` and `.dll` files
compiled with Microsoft's Visual C++ compiler.

The MSVC compilers handle libraries created by older versions
(back to Visual Studio 2015).
Use the current version of Visual Studio.
:::

## Download and build EPICS Base

1. Download the distribution from e.g.
   <https://epics-controls.org/download/base/base-7.0.10.tar.gz>.
2. Unpack it into a work directory.
3. Open a Windows command prompt and change into the directory
   you unpacked EPICS Base into.

:::{warning}
**Spaces in Paths**

The complete path of the current directory **must not** contain
any spaces or parentheses (like `C:\Program Files`).
If your working directory path does, you use the Windows short path
(displayed with `dir /x`) to navigate there.
The full short path to the current directory
can be obtained with `for %A in (".") do @echo %~sA`.
:::

4. Set the EPICS host architecture `EPICS_HOST_ARCH`
   (typically `windows-x64` for DLL builds
   and `windows-x64-static` for static builds).
5. Run the `vcvarsall.bat` script of your installation
   to set the environment for your build.
6. Run `make` (or `gmake` if using the version from Strawberry Perl).

```batch
>cd base-7.0.10
>set EPICS_HOST_ARCH=windows-x64
>"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
**********************************************************************
** Visual Studio 2022 Developer Command Prompt v17.x
**********************************************************************
[vcvarsall.bat] Environment initialized for: 'x64'

>make
```

## Quick test from Windows command prompt

As long as you haven't added the location of your programs to the `PATH`
environment variable (see [installation-windows-env](installation-windows-env.md)),
you will have to provide the whole path to run commands
or `cd` into the directory they are located in.

Run `softIoc` and, if everything is ok, you should see an EPICS prompt:

```batch
>cd C:\Users\'user'\base-7.0.10\bin\windows-x64
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

We will create a test ioc from the existing application template in Base
using the `makeBaseApp.pl` script.

Open the command prompt.
Create a new directory `testioc`:

```batch
>mkdir testioc
>cd testioc
```

From that `testioc` folder run the following:

```batch
>makeBaseApp.pl -t ioc test
>makeBaseApp.pl -i -t ioc test
Using target architecture windows-x64 (only one available)
Application name?
```

Now create a `db` file which describes PVs for your `IOC`.
Go to `testApp\Db` and create `test.db` file:

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

In the same directory, open `Makefile` and change `#DB += xxx.db` to:

```makefile
DB += test.db
```

Go to back to root folder for IOC `testioc`. Go to `iocBoot\ioctest`.
Modify the `st.cmd` startup command file.
Change `#dbLoadRecords("db/xxx.db","user=XXX")` to:

```text
dbLoadRecords("db/test.db","user=XXX")
```

Go back to the root folder `testioc` and run `make`:

```batch
>cd %HOMEPATH%\testioc
>make
```

Go to `iocBoot\ioctest`.
Open the `envPaths` file and change the paths to full Windows paths:

```text
epicsEnvSet("IOC","ioctest")
epicsEnvSet("TOP","C:/Users/'user'/testioc")
epicsEnvSet("EPICS_BASE","C:/Users/'user'/base-7.0.10")
```

Now run the IOC:

```batch
>cd %HOMEPATH%\testioc\iocBoot\ioctest
>..\..\bin\windows-x64\test st.cmd
```

:::{tip}
**Check for Success**

If the IOC starts correctly, you will see initialization messages
and an `epics>` prompt. Type `dbl` to verify that your PVs are loaded.
:::
