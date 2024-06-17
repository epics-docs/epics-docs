Installation on Linux / MacOS
=============================

Scope of these instructions
---------------------------
Starting from scratch, we get to the point where we have a working server,
offering some PVs for reading (caget or pvget) and writing (caput or pvput).
We read and write on them from another terminal,
either on the same machine or on another one in the same network.

If you are using two different machines, both of them need to have access
to the same EPICS installation.

Prepare your system
-------------------

You need ``make``, ``c++`` and ``libreadline`` to compile from source. On macOS these
dependencies can be installed by using e.g. ``homebrew``. On Linux you
can use ``apt-get install``.  The :doc:`linux-packages` document lists all 
of the packages required to build EPICS base, the sequencer, synApps modules, and areaDetector.

Install EPICS
-------------

The recommended way to start working with EPICS is to download one of the release packages.
The released versions of EPICS have been fully tested to work as documented.
Choose the release that you want and download:

::

    mkdir $HOME/EPICS
    cd $HOME/EPICS
    wget https://epics-controls.org/download/base/base-7.0.8.1.tar.gz
    tar -xvf base-7.0.8.1.tar.gz
    cd base-7.0.8.1
    make

After compiling you should put the path into ``$HOME/.profile`` or into ``$HOME/.bashrc`` 
by adding the following to either one of those files:

::

    export EPICS_BASE=${HOME}/EPICS/epics-base
    export EPICS_HOST_ARCH=$(${EPICS_BASE}/startup/EpicsHostArch)
    export PATH=${EPICS_BASE}/bin/${EPICS_HOST_ARCH}:${PATH}

EpicsHostArch is a program provided by EPICS that returns the architecture 
of your system. 
Thus the code above should be fine for every architecture.

Test EPICS
----------
Now log out and log in again, so that your new path is set correctly.
Alternatively, you can execute the three lines above beginning with export 
directly from the terminal.

Run ``softIoc`` and, if everything is ok, you should see an EPICS prompt.

::

    softIoc
    epics>

You can exit with ctrl-c or by typing exit.

Voilà.

Ok, that is not very impressive, but at least you know that EPICS is
installed correctly. So now let us try something more complex, which will
hopefully suggest how EPICS works.

In whatever directory you like, prepare a file test.db that
reads like

::

    record(ai, "temperature:water")
    {
        field(DESC, "Water temperature in the fish tank")
    }

This file defines a record instance called temperature:water, which
is an analog input (ai) record. As you can imagine DESC stays for
Description. Now we start softIoc again, but this time using this
record database.

::

    softIoc -d test.db

Now, from your EPICS prompt, you can list the available records with the
dbl command and you will see something like

::

    epics> dbl
    temperature:water
    epics>

Open a new terminal (we call it nr. 2) and try the command line tools
caget and caput. You will see something like
::

    your prompt> caget temperature:water
    temperature:water              0
    your prompt> caget temperature:water.DESC
    temperature:water.DESC         Water temperature in the fish tank
    your prompt> caput temperature:water 21
    Old : temperature:water              0
    New : temperature:water              21
    your prompt> caput temperature:water 24
    Old : temperature:water              21
    New : temperature:water              24
    your prompt> caget temperature:water 
    temperature:water              24
     ... etc.

Now open yet another terminal (nr. 3) and try ``camonitor`` as

::

    camonitor temperature:water

First, have a look at what happens when you change the temperature:water
value from terminal nr. 2 using caput. Then, try to change the
value by some tiny amounts, like 15.500001, 15.500002, 15.500003… You will
see that camonitor reacts but the readings do not change. If you
wanted to see more digits, you could run

::

    camonitor -g8 temperature:water

For further details on the Channel Access protocol, including documentation
on the ``caput``, ``caget``, ``camonitor``... command line tools, please refer to the
`Channel Access Reference Manual <https://epics.anl.gov/base/R3-15/7-docs/CAref.html#CommandTools>`_.

In real life, however, it is unlikely that the 8 digits returned by your
thermometer (in this example) are all significant. We should thus limit the
traffic to changes of the order of, say, a hundredth of a degree. To do this,
we add one line to the file ``test.db``, so that it reads

::

    record(ai, "temperature:water")
    {
        field(DESC, "Water temperature in Lab 10")
        field(MDEL, ".01")
    }

MDEL stands for Monitor Deadband. If you now run

::

    softIoc -d test.db

with the new ``test.db`` file, you will see that
``camonitor`` reacts only to changes that are larger than 0.01.

This was just a simple example. Please refer to a recent
`Record Reference Manual <https://epics.anl.gov/base/R3-15/7-docs/RecordReference.html>`_
for further information.

Create a demo/test ioc to test ca and pva
-----------------------------------------

::

    mkdir -p $HOME/EPICS/TEST/testIoc
    cd $HOME/EPICS/TEST/testIoc
    makeBaseApp.pl -t example testIoc
    makeBaseApp.pl -i -t example testIoc
    make
    cd iocBoot/ioctestIoc
    chmod u+x st.cmd
    ioctestIoc> ./st.cmd
    #!../../bin/darwin-x86/testIoc
    < envPaths 
    epicsEnvSet("IOC","ioctestIoc") 
    epicsEnvSet("TOP","/Users/maradona/EPICS/TEST/testIoc") 
    epicsEnvSet("EPICS_BASE","/Users/maradona/EPICS/epics-base") 
    cd "/Users/maradona/EPICS/TEST/testIoc" 
    ## Register all support components 
    dbLoadDatabase "dbd/testIoc.dbd" 
    testIoc_registerRecordDeviceDriver pdbbase 
    ## Load record instances dbLoadTemplate "db/user.substitutions" 
    dbLoadRecords "db/testIocVersion.db", "user=junkes" 
    dbLoadRecords "db/dbSubExample.db", "user=junkes" 
    #var mySubDebug 1 
    #traceIocInit 
    cd "/Users/maradona/EPICS/TEST/testIoc/iocBoot/ioctestIoc" 
    iocInit 
    Starting iocInit 
    ############################################################################ 
    ## EPICS R7.0.1.2-DEV 
    ## EPICS Base built Mar 8 2018 
    ############################################################################ 
    iocRun: All initialization complete 
    2018-03-09T13:07:02.475 Using dynamically assigned TCP port 52908. 
    ## Start any sequence programs 
    #seq sncExample, "user=maradona"
    epics> dbl
    maradona:circle:tick
    maradona:compressExample
    maradona:line:b
    maradona:aiExample
    maradona:aiExample1
    maradona:ai1
    maradona:aiExample2
    ... etc. ...
    epics>

Now in another terminal, one can try command line tools like

::

    caget, caput, camonitor, cainfo (Channel Access)
    pvget, pvput, pvlist, eget, ... (PVAccess)

Add the asyn package
--------------------
::

    cd $HOME/EPICS
    mkdir support
    cd support
    git clone https://github.com/epics-modules/asyn.git
    cd asyn

Edit ``$HOME/EPICS/support/asyn/configure/RELEASE`` and set
``EPICS_BASE`` like

::

    EPICS_BASE=${HOME}/EPICS/epics-base

Comment ``IPAC=...`` and ``SNCSEQ=...``, as they are not
needed for the moment. The whole file should read:

::

    #RELEASE Location of external products
    HOME=/Users/maradona
    SUPPORT=$(HOME)/EPICS/support
    -include $(TOP)/../configure/SUPPORT.$(EPICS_HOST_ARCH)
    # IPAC is only necessary if support for Greensprings IP488 is required
    # IPAC release V2-7 or later is required.
    #IPAC=$(SUPPORT)/ipac-2-14
    # SEQ is required for testIPServer
    #SNCSEQ=$(SUPPORT)/seq-2-2-5
    # EPICS_BASE 3.14.6 or later is required
    EPICS_BASE=$(HOME)/EPICS/epics-base
    -include $(TOP)/../configure/EPICS_BASE.$(EPICS_HOST_ARCH)

Now, run
::

    make

If the build fails due to implicit declaration of ``xdr_*`` functions it is likely that asyn should build against libtirpc. To do so, you can uncomment ``# TIRPC=YES`` in ``configure/CONFIG_SITE`` of asyn, such that it states:

::

    # Some linux systems moved RPC related symbols to libtirpc
    # To enable linking against this library, uncomment the following line
    TIRPC=YES



Install StreamDevice (by Dirk Zimoch, PSI)
------------------------------------------
::

    cd $HOME/EPICS/support
    git clone https://github.com/paulscherrerinstitute/StreamDevice.git
    cd StreamDevice/
    rm GNUmakefile

Edit ``$HOME/EPICS/support/StreamDevice/configure/RELEASE`` to specify the install location of EPICS base and of additional software modules, for example:
::

    EPICS_BASE=${HOME}/EPICS/epics-base
    SUPPORT=${HOME}/EPICS/support
    ASYN=$(SUPPORT)/asyn

Remember that ``$(NAME)`` works if it is defined within the same
file, but ``${NAME}`` with curly brackets must be used if a shell
variable is meant. It is possible that the compiler does not like some of the
substitutions. In that case, replace the ``${NAME}`` variables with
full paths, like ``/Users/maradona/EPICS...``.

The sCalcout record is part of synApps. If streamDevice should be built with support for this record, you have to install at least the calc module from SynApps first. For now let's just comment out that line with ``#`` for it to be ignored.

::
    #CALC=${HOME}/EPICS/support/synApps/calc

If you want to enable regular expression matching, you need the PCRE package. For most Linux systems, it is already installed. In that case tell StreamDevice the locations of the PCRE header file and library. However, the pre-installed package can only by used for the host architecture. Thus, add them not to RELEASE but to RELEASE.Common.linux-x86 (if linux-x86 is your EPICS_HOST_ARCH). Be aware that different Linux distributions may locate the files in different directories.
::

    PCRE_INCLUDE=/usr/include/pcre
    PCRE_LIB=/usr/lib

For 64 bit installations, the path to the library may be different:
::

    PCRE_INCLUDE=/usr/include/pcre
    PCRE_LIB=/usr/lib64

Again, if you're not interested in support for reular expression matching at this time then you can comment out any lines referring to PCRE in the ``configure/RELEASE`` file using a ``#``. It can always be added later. 

Finally run ``make`` (we are in the directory ``...EPICS/support/StreamDevice``)
