Creation of an Input/Output Controller (IOC)
============================================

An IOC allows to talk to devices e.g. via ethernet. Create a directory for
the IOCs. For example ``$HOME/EPICS/IOCs``

::

    cd $HOME/EPICS
    mkdir IOCs
    cd IOCs

Create a top for an IOC called ``sampleIOC``

::

    mkdir sampleIOC; cd sampleIOC
    makeBaseApp.pl -t example sampleIOC
    makeBaseApp.pl -i -t example sampleIOC
    Using target architecture darwin-x86 (only one available)
    The following applications are available:
    sampleIOC
    What application should the IOC(s) boot?
    The default uses the IOC's name, even if not listed above.
    Application name? (just return)

Now, by running ``make``, a sample IOC like the demo/test IOC is
built. Next, we want to add asyn and StreamDevice to the IOC. For this, we add
the stream and asyn libraries to the Makefile. Edit
``sampleIOCApp/src/Makefile`` and add the block

::

    #add asyn and streamDevice to this IOC production libs
    sampleIOC_LIBS += stream
    sampleIOC_LIBS += asyn

The application must also load ``asyn.dbd`` and
``stream.dbd`` to use StreamDevice. This can be put into a generated
dbd, e.g into ``xxxSupport.dbd`` which already gets included by the
Makefile. So the ``xxxSupport.dbd`` now reads:

::

    cat sampleIOCApp/src/xxxSupport.dbd
    include "xxxRecord.dbd"
    device(xxx,CONSTANT,devXxxSoft,"SoftChannel")
    #
    include "stream.dbd"
    include "asyn.dbd"
    registrar(drvAsynIPPortRegisterCommands)
    registrar(drvAsynSerialPortRegisterCommands)
    registrar(vxi11RegisterCommands)

To find the dbd files, you have to add the paths to these files in
``configure/RELEASE``:

::

    ...
    # Build variables that are NOT used in paths should be set in
    # the CONFIG_SITE file.
    # Variables and paths to dependent modules:
    SUPPORT = ${HOME}/EPICS/support
    ASYN=$(SUPPORT)/asyn
    STREAM=$(SUPPORT)/stream
    # If using the sequencer, point SNCSEQ at its top directory:
    #SNCSEQ = $(MODULES)/seq-ver
    ...

If ``make`` was done before, ``make distclean`` is
probably required. Anyway, then ``make``. The newly created IOC can be
run with:

::

    cd iocBoot/iocsampleIOC/
    chmod u+x st.cmd
    ./st.cmd

Not very interesting yet, because there is no database file nor a protocol
file.

::

    ls -la sampleIOCApp/Db/
    total 56
    drwxr-xr-x 11 maradona  staff   374  Jun  1  16:47  .
    drwxr-xr-x  5 maradona  staff   170  Jun  1  12:46  ..
    -rw-r--r--  1 maradona  staff   523  Jun  1  12:46  Makefile
    drwxr-xr-x  2 maradona  staff    68  Jun  1  16:47  O.Common
    drwxr-xr-x  3 maradona  staff   102  Jun  1  16:47  O.darwin-x86
    -rw-r--r--  1 maradona  staff  1761  Jun  1  12:46  circle.db
    -rw-r--r--  1 maradona  staff  1274  Jun  1  12:46  dbExample1.db
    -rw-r--r--  1 maradona  staff   921  Jun  1  12:46  dbExample2.db
    -rw-r--r--  1 maradona  staff   286  Jun  1  12:46  dbSubExample.db
    -rw-r--r--  1 maradona  staff   170  Jun  1  12:46  sampleIOCVersion.db
    -rw-r--r--  1 maradona  staff   307  Jun  1  12:46  user.substitutions

Note that this is a ``Db`` directory and not the ``db``
directory that is in ``./sampleIOC``. For MDOxxxx scopes by Tektronix, the
database (``.db``) and protocol (``.proto``) file can look
something like

::

    cat MDO.db
    record(stringin, $(P)$(R)idn){
        field(DESC, "Asks for info blabla")
        field(DTYP, "stream")
        field(INP, "@MDO.proto getStr(*IDN,99) $(PORT) $(A)")
        field(PINI, "YES")
    }

    cat MDO.proto
    Terminator = LF;
    getStr{
        out "$1?";
        in "%s";
        @replytimeout {out "$1?"; in "%s";}
    }

Now, we add to ``sampleIOCApp/Db/Makefile`` the information that
these files must be included in the compilation. So

::

    cat sampleIOCApp/Db/Makefile
    TOP=../..
    include $(TOP)/configure/CONFIG
    #----------------------------------------
    # ADD MACRO DEFINITIONS BELOW HERE
    # Install databases, templates & substitutions like this
    DB += circle.db
    DB += dbExample1.db
    DB += dbExample2.db
    DB += sampleIOCVersion.db
    DB += dbSubExample.db
    DB += user.substitutions
    DB += MDO.db
    DB += MDO.proto
    # If .db template is not named *.template add
    # _TEMPLATE = 
    include $(TOP)/configure/RULES
    #----------------------------------------
    # ADD EXTRA GNUMAKE RULES BELOW HERE

Again, ``make`` in directory sampleIOC. Finally, we add IP port
configuration, setting the Stream path and loading the database to the
``st.cmd`` file. The ``st.cmd`` should read:

::

    cat st.cmd

    #!../../bin/darwin-x86/sampleIOC

    #- You may have to change sampleIOC to something else
    #- everywhere it appears in this file

    < envPaths

    epicsEnvSet ("STREAM_PROTOCOL_PATH","$(TOP)/db")

    cd "${TOP}"

    ## Register all support components
    dbLoadDatabase "dbd/sampleIOC.dbd"
    sampleIOC_registerRecordDeviceDriver pdbbase

    ## Load record instances
    dbLoadTemplate "db/user.substitutions"
    dbLoadRecords "db/sampleIOCVersion.db", "user=UUUUUU"
    dbLoadRecords "db/dbSubExample.db", "user=UUUUUU"

    #IF if the user also defines EPICS_CAS_INTF_ADDR_LIST then beacon address
    #list automatic configuration is constrained to the network interfaces specified
    #therein, and therefore only the broadcast addresses of the specified LAN interfaces,
    #and the destination addresses of all specified point-to-point links, will be automatically configured.
    #epicsEnvSet ("EPICS_CAS_INTF_ADDR_LIST","aaa.aaa.aaa.aaa")

    # connect to the device ... IP-Address ! Port 2025 used by textronix, see manual
    drvAsynIPPortConfigure("L0","bbb.bbb.bbb.bbb:pppp",0,0,0)

    ## Load record instances
    dbLoadRecords("db/MDO.db", "P=UUUUUU:,PORT=L0,R=MDO:,L=0,A=0")

    #- Set this to see messages from mySub
    #var mySubDebug 1

    #- Run this to trace the stages of iocInit
    #traceIocInit

    cd "${TOP}/iocBoot/${IOC}"
    iocInit

    ## Start any sequence programs
    #seq sncExample, "user=UUUUUU"

In here, you have to replace *UUUUUU* with the user name that runs
the EPICS IOC (you?). *bbb.bbb.bbb.bbb* is the IP of the device (e.g.
the scope) and *pppp* the port on which it listens.
*EPICS_CAS_INTF_ADDR_LIST* can be used if there are two network
interfaces (e.g. wlan and eth0).

The following commands might be necessary with multiple network
interfaces:

::

    export EPICS_CA_ADDR_LIST=ccc.ccc.ccc.ccc << Broadcast address of the network
    export EPICS_CA_AUTO_ADDR_LIST=NO