Installation using plain Windows and the Visual Studio compilers
================================================================

Install tools
-------------
There are two reasonable options.

Using Chocolatey
^^^^^^^^^^^^^^^^
Go to the `Chocolatey website <https://chocolatey.org/>`_ and follow their instructions to download and install the package manager.

Using Chocolatey, install Strawberry Perl and Gnu Make.

Manually
^^^^^^^^
Install Strawberry Perl or ActivePerl using the Windows installers available on their download pages.

Strawberry Perl contains a suitable version of GNU Make. Otherwise, you can download a Windows executable that Andrew provides at https://epics.anl.gov/download/tools/make-4.2.1-win64.zip. Unzip it into a location (path must not contain spaces or parentheses) and add it to the system environment.

Put tools in the Path
^^^^^^^^^^^^^^^^^^^^^
Make sure the tools' locations are added to the system environment variable Path. Inside a shell (command prompt) they must be callable using their simple name, e.g.::

    >perl --version

    This is perl 5, version 26, subversion 1 (v5.26.1) built for MSWin32-x64-multi-thread
    (with 1 registered patch, see perl -V for more detail)

    Copyright 1987-2017, Larry Wall

    Binary build 2601 [404865] provided by ActiveState http://www.ActiveState.com
    Built Dec 11 2017 12:23:25
    ...

    >make --version
    GNU Make 4.2.1
    Built for x86_64-w64-mingw32
    Copyright (C) 1988-2016 Free Software Foundation, Inc.
    License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
    This is free software: you are free to change and redistribute it.
    There is NO WARRANTY, to the extent permitted by law.

Install the compiler
--------------------
Download the Visual Studio Installer and install (the community edition is free). Make sure you enable the Programming Languages / C++ Development options.

In VS 2019, you also have the option to additionally install the Visual C++ 2017 compilers, if that is interesting for you.
    
Download and build EPICS Base
-----------------------------

1. Download the distribution from e.g. https://epics-controls.org/download/base/base-7.0.4.1.tar.gz.
2. Unpack it into a work directory.
3. Open a Windows command prompt and change into the directory you unpacked EPICS Base into. It is best to use a ``cmd`` command prompt for this - running ``bat`` files by e.g. ``&`` from powershell prompt does not preserve environment variables set in the bat file, such as by ``vcvarsall.bat``. If you wish to use powershell, you need to launch powershell from a cmd window after you have run the relevant bat files to set the environment. See https://stackoverflow.com/questions/49027851/setting-environment-variables-with-batch-file-lauched-by-powershell-script 

   **Note:** The complete path of the current directory mustn't contain any spaces or parentheses. If your working directory path does, you can do another cd into the same directory, replacing every path component containing spaces or parentheses with its Windows short path (that can be displayed with ``dir /x``).
4. Set the EPICS host architecture EPICS_HOST_ARCH (windows-x64 for 64bit builds, win32-x86 for 32bit builds).
5. Run the ``vcvarsall.bat`` script of your installation (the exact path depends on the type and language of installation) to set the environment for your build.
6. Run ``make`` (or ``gmake`` if using the version from Strawberry Perl).

::

    >cd base-R7.0.4.1
    >set EPICS_HOST_ARCH=windows-x64
    >"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat" amd64
    **********************************************************************
    ** Visual Studio 2019 Developer Command Prompt v16.6.2
    ** Copyright (c) 2020 Microsoft Corporation
    **********************************************************************
    [vcvarsall.bat] Environment initialized for: 'x64'

    >make

There will probably be warnings, but there should be no error. You can choose any EPICS base to install, the procedure remains the same.

Please refer to the chapter "Build Time" in :doc:`installation-windows` for ways to shorten your build.

Quick test from Windows command prompt
--------------------------------------
As long as you haven't added the location of your programs to the ``PATH`` environment variable (see :doc:`installation-windows-env`), you will have to provide the whole path to run commands or `cd` into the directory they are located in.

Open the Windows command prompt. Again, replace 'user' with the actual Windows user folder name existing in your Windows installation.

Run ``softIoc`` and, if everything is ok, you should see an EPICS prompt::

    >cd C:\Users\'user'\base-R7.0.4.1\bin\windows-x64-mingw
    >softIoc -x test
    Starting iocInit
    iocRun: All initialization complete
    dbLoadDatabase("C:\Users\'user'\base-R7.0.4.1\bin\windows-x64\..\..\dbd\softIoc.dbd")
    softIoc_registerRecordDeviceDriver(pdbbase)
    iocInit()
    ############################################################################
    ## EPICS R7.0.4.1
    ## Rev. 2020-10-21T11:57+0200
    ############################################################################
    epics>

You can exit with ctrl-c or by typing exit.

As long as you are in the location of the EPICS Base binaries, they will all work using their simple names. Try commands like ``caput``, ``caget``, ``camonitor``, ...

Quick test from MSYS2 Bash
--------------------------
Obviously, if you have an installation of MSYS2, you can run the same verification from the MSYS2 Bash shell::

    $ cd /c/Users/'user'/base-R7.0.4.1/bin/windows-x64
    $ ./softIoc -x test
    Starting iocInit
    iocRun: All initialization complete
    dbLoadDatabase("C:\Users\'user'\base-R7.0.4.1\bin\windows-x64\..\..\dbd\softIoc.dbd")
    softIoc_registerRecordDeviceDriver(pdbbase)
    iocInit()
    ############################################################################
    ## EPICS R7.0.4.1
    ## Rev. 2020-10-21T11:57+0200
    ############################################################################
    epics>

You can exit with ctrl-c or by typing exit.

As long as you are in the location of the EPICS Base binaries, you can run them by prefixing ``./``. Try commands like ``./caput``, ``./caget``, ``./camonitor``, ...


Create a demo/test IOC
----------------------
Although the ``softIoc`` binary can be used with multiple instances with different db files, you will need to create your own IOC at some point. We will create a test ioc from the existing application template in Base using the ``makeBaseApp.pl`` script.

Let's create one IOC, which takes the values of 2 process variables (PVs), adds them and stores the result in 3rd PV.

We will use the Windows command prompt for building the IOC. Open the command prompt. Create a new directory ``testioc``::

    >mkdir testioc
    >cd testioc
    
From that ``testioc`` folder run the following::

    >makeBaseApp.pl -t ioc test
    >makeBaseApp.pl -i -t ioc test
    Using target architecture windows-x64 (only one available)
    The following applications are available:
        test
    What application should the IOC(s) boot?
    The default uses the IOC's name, even if not listed above.
    Application name?
    
Accept the default name and press enter. That should generate a skeleton for your ``testioc``.

You can find the full details of the application structure in the "Application Developer's Guide", chapter `Example IOC Application <https://epics.anl.gov/base/R3-16/2-docs/AppDevGuide/AppDevGuide.html>`_.

::

    >dir /b
    configure
    iocBoot
    Makefile
    testApp
    
Now create a ``db`` file which describes PVs for your ``IOC``. Go to ``testApp\Db`` and create ``test.db`` file with following record details::

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

Go to back to root folder for IOC ``testioc``. Go to ``iocBoot\ioctest``. Modify the ``st.cmd`` startup command file.

Change::

    #dbLoadRecords("db/xxx.db","user=XXX")

to::

    dbLoadRecords("db/test.db","user=XXX")

Save all the files and go back to the MSYS2 Bash terminal. Make sure the environment is set up correctly (see :doc:`installation-windows-env`).::

    >echo $EPICS_HOST_ARCH
    windows-x64
    >cl
    Microsoft (R) C/C++ Optimizing Compiler Version 19.27.29112 for x64
    Copyright (C) Microsoft Corporation.  All rights reserved.

Change into the testioc folder and run ``make`` (or ``gmake`` when using the make from Strawberry Perl)::

    >cd %HOMEPATH%\testioc
    >make

This should build the executable and create all files for the test IOC::
    
    >dir /b
    bin
    configure
    db
    dbd
    iocBoot
    lib
    Makefile
    testApp

At this point, you can run the IOC from either an MSYS2 Bash shell or from a Windows command prompt, by changing into the IOC directory and running the test.exe binary with your startup command script as parameter.

In the Windows command prompt::

    >cd %HOMEPATH%\testioc\iocBoot\ioctest    
    >..\..\bin\windows-x64\test st.cmd

Or - if you have an installation - in the MSYS2 shell::

    $ cd ~/testioc/iocBoot/ioctest    
    $ ../../bin/windows-x64/test st.cmd


In both cases, the IOC should start like this::

    Starting iocInit
    #!../../bin/windows-x64/test
    < envPaths
    epicsEnvSet("IOC","ioctest")
    epicsEnvSet("TOP","C:/Users/'user'/testioc")
    epicsEnvSet("EPICS_BASE","C:/Users/'user'/base-R7.0.4.1")
    cd "C:/Users/'user'/testioc"
    ## Register all support components
    dbLoadDatabase "dbd/test.dbd"
    test_registerRecordDeviceDriver pdbbase
    ## Load record instances
    dbLoadRecords("db/test.db","user='user'")
    cd "C:/Users/'user'/testioc/iocBoot/ioctest"
    iocInit
    ############################################################################
    ## EPICS R7.0.4.1
    ## Rev. 2020-10-21T11:57+0200
    ############################################################################
    iocRun: All initialization complete
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

    >camonitor test:add
    test:add                       2020-10-23 13:39:14.795006 100

That terminal will monitor the PV ``test:add`` continuously. If any value change is detected, it will be updated in this terminal. Keep it open to observe the behaviour.

Open a third shell. Using caput, modify the values of  ``test:pv1`` and ``test:pv2`` as we have done in the temperature example above. You will see changes of their sum in the second terminal accordingly.

At this point, you have one IOC ``testioc`` running, which loaded the database ``test.db`` with 3 records. From other processes, you can connect to these records using Channel Access. If you add more process variable in ``test.db``, you will have to ``make`` the `testioc` application again and restart the IOC to load the new version of the database.

You can also create and run IOCs like this in parallel with their own databases and process variables. Just keep in mind that each record instance has to have a unique name for Channel Access to work properly.
