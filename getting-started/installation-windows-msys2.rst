Installation using MSYS2 and the MinGW Compilers
================================================
MSYS2 has all the required tools available through an easy-to-use package manager, and its bash shell looks and feels like working on Linux. Most Bash commands are similar to their Linux versions. MSYS2 is available for Windows 7 and up only. The following procedure is verified on Windows 8.1 (64 bit) and Windows 10 (64 bit).

Install tools
-------------
MSYS2 provides a Bash shell, Autotools, revision control systems and other tools for building native Windows applications using MinGW-w64 toolchains. It can be installed from its official `website <https://www.msys2.org>`_. Download and run the installer - "x86_64" for 64-bit, "i686" for 32-bit Windows. The installation procedure is well explained on the website. These instructions assume you are running on 64-bit Windows.

The default location of the MSYS2 installation is ``C:\msys64``. If you don't have Administrator rights, you can install MSYS2 in any location you have access to, e.g. ``C:\Users\'user'\msys64`` (with 'user' being your Windows user directory name). We will assume the default location in this document.

Once installation is complete, you have three options available for starting a shell. The difference between these options is the preset of the environment variables that select the compiler toolchain to use.
Launch the "MSYS MinGW 64-bit" option to use the MinGW 64bit toolchain, producing 64bit binaries that run on 64bit Windows systems. The "MSYS MinGW 32-bit" option will use the MinGW 32bit toolchain, producing 32bit binaries that will run on 32bit and 64bit Windows systems. Do not use the "MSYS2 MSYS" window as this will not build EPICS.

Again: you have a single installation of MSYS2, these different shells are just setups to use different compilers. Installation and update of your MSYS2 system only has to be done once - you can use any of the shell options for that.

Update MSYS2 with following command::

    $ pacman -Syu

After this finishes (let it close the bash shell), open bash again and run the same command again to finish the updates. The same procedure is used for regular updates of the MSYS2 installation. An up-to-date system shows::

    $ pacman -Syu
    :: Synchronizing package databases...
     mingw32 is up to date
     mingw64 is up to date
     msys is up to date
    :: Starting core system upgrade...
     there is nothing to do
    :: Starting full system upgrade...
     there is nothing to do

Install the necessary tools (perl is already part of the base system)::

    $ pacman -S tar make

Packages with such "simple" names are part of the MSYS2 environment and work for all compilers/toolchains that you may install on top on MSYS2.

Install compiler toolchains
---------------------------
Packages that are part of a MinGW toolchain start with the prefix "mingw-w64-x86_64-" for the 64bit toolchain or "mingw-w64-i686-" for the 32bit toolchain.
(The "w64" part identifies the host system will be different when using a 32bit MSYS2 environment, e.g. on a 32bit Windows host.)

Install the MinGW 32bit and/or MinGW 64bit toolchains::

    $ pacman -S mingw-w64-x86_64-toolchain
    $ pacman -S mingw-w64-i686-toolchain

Each complete toolchain needs about 900MB of disk space.
If you want to cut down the needed disk space (to about 50%), instead of hitting return when asked which packages of the group to install, you can select the minimal set of packages required for compiling EPICS Base: ``binutils``, ``gcc`` and ``gcc-libs``.

If you are not sure, check your set of tools is complete and everything is installed properly::

    $ pacman -Q
    ...
    make 4.3-1
    perl 5.32.0-2
    mingw-w64-x86_64-...
    mingw-w64-i686-...
    ...

Update your installation regularly
----------------------------------
As mentioned above, you can update your complete installation (including all tools and compiler toolchains) at any time using::

    $ pacman -Syu

You should do this in regular intervals.

Check Setup
-----------

From your build window type

    $ gcc -v

You should see something like::

    COLLECT_GCC=C:\msys64\mingw64\bin\gcc.exe
    COLLECT_LTO_WRAPPER=C:/msys64/mingw64/bin/../lib/gcc/x86_64-w64-mingw32/14.2.0/lto-wrapper.exe
    Target: x86_64-w64-mingw32

If you however see::

    COLLECT_GCC=gcc
    COLLECT_LTO_WRAPPER=/usr/lib/gcc/x86_64-pc-msys/13.3.0/lto-wrapper.exe
    Target: x86_64-pc-msys

Then your shell has picked up the MSYS rather than MinGW64 environment and the build will not work

Download and build EPICS Base
-----------------------------
Start the "MSYS MinGW 64-bit" shell and do::

    $ cd $HOME
    $ wget https://epics-controls.org/download/base/base-7.0.4.1.tar.gz
    $ tar -xvf base-7.0.4.1.tar.gz
    $ cd base-R7.0.4.1
    $ export EPICS_HOST_ARCH=windows-x64-mingw
    $ make

When using the MinGW 32bit toolchain, the "MSYS MinGW 32-bit" shell must be used and EPICS_HOST ARCH must be set to "win32-x86-mingw".

Note: If you are connecting to your MSYS2 system through ssh, you need to set and allow an environment variable to use the environment presets for the MinGW compilers. In the MSYS2 configuration of the ssh daemon (``/etc/ssh/sshd_config``), add the line

::

    AcceptEnv MSYSTEM

and on your (local) client configuration (``~/.ssh/config``) add the line

::

    SetEnv MSYSTEM=MINGW64

to use the MinGW 64-bit compiler chain (``MINGW32`` to use a 32-bit installation).

During the compilation, there will probably be warnings, but there should be no error. You can choose any EPICS Base version to build, the procedure remains the same.

Please refer to the chapter "Build Time" in :doc:`installation-windows` for ways to shorten your build.

Quick test from MSYS2 Bash
--------------------------
As long as you haven't added the location of your programs to the ``PATH`` environment variable (see below), you will have to provide the whole path to run commands or `cd` into the directory they are located in and prefix the command with ``./``.

Replace 'user' with the actual Windows user folder name existing in your Windows installation - MSYS2 creates your home directory using that name. In the examples, we assume the default location for MSYS2 (``C:\msys64``).

Run ``softIoc`` and, if everything is ok, you should see an EPICS prompt::

    $ cd /home/'user'/base-R7.0.4.1/bin/windows-x64-mingw
    $ ./softIoc -x test
    Starting iocInit
    iocRun: All initialization complete
    dbLoadDatabase("C:\msys64\home\'user'\base-R7.0.4.1\bin\windows-x64-mingw\..\..\dbd\softIoc.dbd")
    softIoc_registerRecordDeviceDriver(pdbbase)
    iocInit()
    ############################################################################
    ## EPICS R7.0.4.1
    ## Rev. 2020-10-21T11:57+0200
    ############################################################################
    epics>

You can exit with ctrl-c or by typing exit.

As long as you are in the location of the EPICS Base binaries, you can run them by prefixing with ``./``. Try commands like ``./caput``, ``./caget``, ``./camonitor``, ...

Quick test from Windows command prompt
--------------------------------------
Open the Windows command prompt. Again, 'user' is the Windows user folder name.
The MSYS2 home folders are inside the MSYS2 installation.

If you built EPICS Base with dynamic (DLL) linking, you need to add the location of the C++ libraries to the `PATH` variable for them to be found. (Again, assuming a 64bit MSYS2 installation with default paths and the MinGW 64bit toolchain.)

::

    >set "PATH=%PATH%C:\msys64\mingw64\bin;"
    >cd C:\msys64\home\'user'\base-R7.0.4.1\bin\windows-x64-mingw
    >softIoc -x test
    Starting iocInit
    ############################################################################
    ## EPICS R7.0.4.1
    ## Rev. 2020-10-21T11:57+0200
    ############################################################################
    iocRun: All initialization complete
    epics>

You can exit with ctrl-c or by typing exit.

As long as you are in the location of the EPICS Base binaries, they will all work using their simple names. Try commands like ``caput``, ``caget``, ``camonitor``, ...

Create a demo/test IOC
----------------------
Although the ``softIoc`` binary can be used with multiple instances with different db files, you will need to create your own IOC at some point. We will create a test ioc from the existing application template in Base using the ``makeBaseApp.pl`` script.

Let's create one IOC, which takes the values of 2 process variables (PVs), adds them and stores the result in 3rd PV.

We will use ``MSYS2`` for building the IOC. Open the ``MSYS2 Mingw 64-bit`` shell. Make sure the environment is set up correctly (see :doc:`installation-windows-env`).

Create a new directory ``testioc``::

    $ mkdir testioc
    $ cd testioc

From that ``testioc`` folder run the following::

    $ makeBaseApp.pl -t ioc test
    $ makeBaseApp.pl -i -t ioc test
    Using target architecture windows-x64-mingw (only one available)
    The following applications are available:
        test
    What application should the IOC(s) boot?
    The default uses the IOC's name, even if not listed above.
    Application name?

Accept the default name and press enter. That should generate a skeleton for your ``testioc``.

You can find the full details of the application structure in the "Application Developer's Guide", chapter `Example IOC Application <https://epics.anl.gov/base/R3-16/2-docs/AppDevGuide/GettingStarted.html#x3-60002.2>`_.

::

    $ ls
    configure  iocBoot  Makefile  testApp

Now create a ``db`` file which describes PVs for your ``IOC``. Go to ``testApp/Db`` and create ``test.db`` file with following record details::

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
        field(SCAN, "1 second")
        field(INPA, "test:pv1")
        field(INPB, "test:pv2")
        field(CALC, "A + B")
    }

Open ``Makefile`` and navigate to

::

    #DB += xxx.db

Remove # and change this to ``test.db``::

    DB += test.db

Go to back to root folder for IOC ``testioc``. Go to ``iocBoot/ioctest``. Modify the ``st.cmd`` startup command file.

Change::

    #dbLoadRecords("db/xxx.db","user=XXX")

to::

    dbLoadRecords("db/test.db","user=XXX")

Save all the files and go back to the MSYS2 Bash terminal. Make sure the architecture is set correctly::

    $ echo $EPICS_HOST_ARCH
    windows-x64-mingw

Change into the testioc folder and run ``make``::

    $ cd ~/testioc
    $ make

This should create all the files for the test IOC.

::
    
    $ ls
    bin  configure  db  dbd  iocBoot  lib  Makefile  testApp

Go to ``iocBoot/ioctest`` . Open the ``envPaths`` file and change the MSYS2 relative paths to full Windows paths::

    epicsEnvSet("IOC","ioctest")
    epicsEnvSet("TOP","C:/msys64/home/'user'/testioc")
    epicsEnvSet("EPICS_BASE","C:/msys64/home/'user'/base-7.0.4.1")

**Note:** You can use Linux style forward slash characters in path specifications inside this file or double backslashes (``\\``).

At this point, you can run the IOC from either an MSYS2 Bash shell or from a Windows command prompt, by changing into the IOC directory and running the test.exe binary with your startup command script as parameter.

In the Windows command prompt::

    >cd C:\msys64\home\'user'\testioc\iocBoot\ioctest    
    >..\..\bin\windows-x64-mingw\test st.cmd

In the MSYS2 shell::

    $ cd ~/testioc/iocBoot/ioctest    
    $ ../../bin/windows-x64-mingw/test st.cmd


In both cases, the IOC should start like this::

    Starting iocInit
    iocRun: All initialization complete
    #!../../bin/windows-x64-mingw/test
    < envPaths
    epicsEnvSet("IOC","ioctest")
    epicsEnvSet("TOP","C:/msys64/home/'user'/testioc")
    epicsEnvSet("EPICS_BASE","C:/msys64/home/'user'/base-R7.0.4.1")
    cd "C:/msys64/home/'user'/testioc"
    ## Register all support components
    dbLoadDatabase "dbd/test.dbd"
    test_registerRecordDeviceDriver pdbbase
    Warning: IOC is booting with TOP = "C:/msys64/home/'user'/testioc"
              but was built with TOP = "/home/'user'/testioc"
    ## Load record instances
    dbLoadRecords("db/test.db","user='user'")
    cd "C:/msys64/home/'user'/testioc/iocBoot/ioctest"
    iocInit
    ############################################################################
    ## EPICS R7.0.4.1
    ## Rev. 2020-10-21T11:57+0200
    ############################################################################
    ## Start any sequence programs
    #seq sncxxx,"user='user'"
    epics>

Check if the database ``test.db`` you created is loaded correctly::

    epics> dbl
    test:pv1
    test:pv2
    test:add

As you can see 3 process variable is loaded and available. Keep this terminal open and running. Test this process variable using another terminals.

Open another shell for monitoring ``test:add``::

    $ camonitor test:add
    test:add                       2020-10-23 13:39:14.795006 100

That terminal will monitor the PV ``test:add`` continuously. If any value change is detected, it will be updated in this terminal. Keep it open to observe the behaviour.

Open a third shell. Using caput, modify the values of  ``test:pv1`` and ``test:pv2`` as we have done in the temperature example above. You will see changes of their sum in the second terminal accordingly.

At this point, you have one IOC ``testioc`` running, which loaded the database ``test.db`` with 3 records. From other processes, you can connect to these records using Channel Access. If you add more process variable in ``test.db``, you will have to ``make`` the `testioc` application again and restart the IOC to load the new version of the database.

You can also create and run IOCs like this in parallel with their own databases and process variables. Just keep in mind that each record instance has to have a unique name for Channel Access to work properly.
