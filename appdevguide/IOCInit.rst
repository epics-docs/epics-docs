IOC Initialization
------------------

:audience:`developer`

.. contents:: Table of Contents
 :depth: 3

Overview - Environments requiring a main program
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a main program is required (most likely on all environments except
vxWorks and RTEMS), then initialization is performed by statements
residing in startup scripts which are executed by iocsh. An example main
program is:

.. code ::

    int main(int argc,char  *argv[])
    {
       if (argc >= 2) {
           iocsh(argv[1]);
           epicsThreadSleep(.2);
       }
       iocsh(NULL);
       epicsExit(0)
       return 0;
    }

The  first call to iocsh executes commands from the startup script  filename
which must be passed as an argument to the program. The second call to
iocsh with a NULL argument puts iocsh into interactive mode. This allows
the user to issue the commands described in the chapter on  "IOC Test
Facilities" as well as some additional commands like help.

The command  file passed is usually called the startup script, and
contains statements like these:

.. code ::

        < envPaths
        cd ${TOP}
        dbLoadDatabase "dbd/appname.dbd"
        appname_registerRecordDeviceDriver pdbbase
        dbLoadRecords "db/file.db", "macro=value"
        cd ${TOP}/iocBoot/${IOC}
        iocInit

The envPaths  file is automatically generated in the IOC's boot directory
and defines several environment variables that are useful later in the
startup script. The definitions shown below are always provided;
additional entries will be created for each support module referenced in
the application's configure/RELEASE file:

.. code ::

        epicsEnvSet("ARCH","linux-x86")
        epicsEnvSet("IOC","iocname")
        epicsEnvSet("TOP","/path/to/application")
        epicsEnvSet("EPICS_BASE","/path/to/base")

Overview - vxWorks
~~~~~~~~~~~~~~~~~~~~~~

After vxWorks is loaded at IOC boot time, commands like the following,
normally placed in the vxWorks startup script, are issued to load and
initialize the application code:

.. code ::

        # Many vxWorks board support packages need the following:
        #cd <full path to IOC boot directory>
        < cdCommands
        cd topbin
        ld 0,0, "appname.munch"

        cd top
        dbLoadDatabase "dbd/appname.dbd"
        appname_registerRecordDeviceDriver pdbbase
        dbLoadRecords "db/file.db", "macro=value"

        cd startup
        iocInit

The cdCommands script is automatically generated in the IOC boot
directory and defines several vxWorks global variables that allow cd
commands to various locations, and also sets several environment
variables. The definitions shown below are always provided; additional
entries will be created for each support module referenced in the
application's configure/RELEASE file:

.. code ::

        startup = "/path/to/application/iocBoot/iocname"
        putenv "ARCH=vxWorks-68040"
        putenv "IOC=iocname"
        top = "/path/to/application"
        putenv "TOP=/path/to/application"
        topbin = "/path/to/application/bin/vxWorks-68040"
        epics_base = "/path/to/base"
        putenv "EPICS_BASE=/path/to/base"
        epics_basebin = "/path/to/base/bin/vxWorks-68040"

The **ld** command in the startup script loads EPICS core, the record,
device and driver support the IOC needs, and any application specific
modules that have been linked into it.

**dbLoadDatabase** loads database definition files describing the
record/device/driver support used by the application..

**dbLoadRecords** loads record instance definitions.

**iocInit** initializes the various epics components and starts the IOC
running.

Overview - RTEMS
~~~~~~~~~~~~~~~~

RTEMS applications can start up in many different ways depending on the
board-support package for a particular piece of hardware. Systems which
use the Cexp package can be treated much like vxWorks. Other systems
first read initialization parameters from non-volatile memory or from a
BOOTP/DHCP server. The exact mechanism depends upon the BSP. TFTP or NFS
filesystems are then mounted and the IOC shell is used to read commands
from a startup script. The location of this startup script is specified
by a initialization parameter. This script is often similar or identical
to the one used with vxWorks. The RTEMS startup code calls

.. code ::

   epicsRtemsInitPreSetBootConfigFromNVRAM(struct rtems_bsdnet_config  *);

just before setting the initialization parameters from non-volatile
memory, and

.. code ::

   epicsRtemsInitPostSetBootConfigFromNVRAM(struct rtems_bsdnet_config  *);

just after setting the initialization parameters. An application may
provide either or both of these routines to perform any custom
initialization required. These function prototypes and some useful
external variable declarations can be found in the header file
epicsRtemsInitHooks.h

IOC Initialization
~~~~~~~~~~~~~~~~~~

An IOC is normally started with the **iocInit** command as shown in the
startup scripts above, which is actually implemented in two distinct
parts. The first part can be run separately as the iocBuild command,
which puts the IOC into a quiescent state without allowing the various
internal threads it starts to actually run. From this state the second
command iocRun can be used to bring it online very quickly. A running
IOC can be quiesced using the iocPause command, which freezes all
internal operations; at this point the iocRun command can restart it
from where it left off, or the IOC can be shut down (exit the program, or
reboot on vxWorks/RTEMS). Most device support and drivers have not yet
been written with the possibility of pausing an IOC in mind though, so
this feature may not be safe to use on an IOC which talks to external
devices or software.

IOC initialization using the iocBuild and iocRun commands then consists
of the following steps:

Configure Main Thread
^^^^^^^^^^^^^^^^^^^^^

Provided the IOC has not already been initialized, initHookAtIocBuild
is announced first.

The main thread's epicsThreadIsOkToBlock flag is set, the message
"Starting iocInit" is logged and epicsSignalInstallSigHupIgnore called,
which on Unix architectures prevents the process from shutting down if
it later receives a HUP signal.

At this point, initHookAtBeginning is announced.

General Purpose Modules
^^^^^^^^^^^^^^^^^^^^^^^

Calls coreRelease which prints a message showing which version of iocCore
is being run.

Calls taskwdInit to start the task watchdog. This accepts requests to
watch other tasks. It runs periodically and checks to see if any of the
tasks is suspended. If so it issues an error message, and can also
invoke callback routines registered by the task itself or by other
software that is interested in the state of the IOC. See "Task Watchdog"
for details.

Starts the general purpose callback tasks by calling callbackInit. Three
tasks are started at different scheduling priorities.

initHookAfterCallbackInit is announced.

Channel Access Links
^^^^^^^^^^^^^^^^^^^^

Calls dbCaLinkInit. The initializes the module that handles database
channel access links, but does not allow its task to run yet.

initHookAfterCaLinkInit is announced.

Driver Support
^^^^^^^^^^^^^^

initDrvSup locates each device driver entry table and calls the init
routine of each driver.

initHookAfterInitDrvSup is announced.

Record Support
^^^^^^^^^^^^^^

initRecSup locates each record support entry table and calls the init
routine for each record type.

initHookAfterInitRecSup is announced.

Device Support
^^^^^^^^^^^^^^

initDevSup locates each device support entry table and calls its init
routine specifying that this is the initial call.

initHookAfterInitDevSup is announced.

Database Records
^^^^^^^^^^^^^^^^

initDatabase is called which makes three passes over the database
performing the following functions:

#. Initializes the fields RSET, RDES, MLOK, MLIS, PACT and DSET for each
   record.

   Calls record support's init_record (first pass).

#. Convert each PV_LINK into a DB_LINK or CA_LINK

   Calls any extended device support's add_record routine.

#. Calls record support's init_record (second pass).

Finally it registers an epicsAtExit routine to shut down the database
when the IOC application exits.

Next dbLockInitRecords is called to create the lock sets.

Then dbBkptInit is run to initialize the database debugging module.

initHookAfterInitDatabase is announced.

Device Support again
^^^^^^^^^^^^^^^^^^^^

initDevSup locates each device support entry table and calls its init
routine specifying that this is the final call.

initHookAfterFinishDevSup is announced.

Scanning and Access Security
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The periodic, event, and I/O event scanners are initialized by calling
scanInit, but the scan threads created are not allowed to process any
records yet.

A call to asInit initailizes access security. If this reports failure,
the IOC initialization is aborted.

dbProcessNotifyInit initializes support for process notification.

After a short delay to allow settling, initHookAfterScanInit is
announced.

Initial Processing
^^^^^^^^^^^^^^^^^^

initialProcess processes all records that have PINI set to YES.

initHookAfterInitialProcess is announced.

Channel Access Server
^^^^^^^^^^^^^^^^^^^^^

The Channel Access server is started by calling rsrv_init, but its tasks
are not allowed to run so it does not announce its presence to the
network yet.

initHookAfterCaServerInit is announced.

At this point, the IOC has been fully initialized but is still
quiescent. initHookAfterIocBuilt is announced. If started using iocBuild
this command completes here.

Enable Record Processing
^^^^^^^^^^^^^^^^^^^^^^^^

If the iocRun command is used to bring the IOC out of its initial
quiescent state, it starts here.

initHookAtIocRun is announced.

The routines scanRun and dbCaRun are called in turn to enable their
associated tasks and set the global variable interruptAccept to TRUE
(this now happens inside scanRun). Until this is set all I/O interrupts
should have been ignored.

initHookAfterDatabaseRunning is announced. If the iocRun command (or
iocInit) is being executed for the first time,
initHookAfterInterruptAccept is announced.

Enable CA Server
^^^^^^^^^^^^^^^^

The Channel Access server tasks are allowed to run by calling rsrv_run.

initHookAfterCaServerRunning is announced. If the IOC is starting for
the first time, initHookAtEnd is announced.

A command completion message is logged, and initHookAfterIocRunning is
announced.

Pausing an IOC
~~~~~~~~~~~~~~

The command iocPause brings a running IOC to a quiescent state with all
record processing frozen (other than possibly the completion of
asynchronous I/O operations). A paused IOC may be able to be restarted
using the iocRun command, but whether it will fully recover or not can
depend on how long it has been quiescent and the status of any device
drivers which have been running. The operations which make up the pause
operation are as follows:

#. initHookAtIocPause is announced.
#. The Channel Access Server tasks are paused by calling rsrv_pause
#. initHookAfterCaServerPaused is announced.
#. The routines dbCaPause and scanPause are called to pause their
   associated tasks and set the global variable interruptAccept to
   FALSE.
#. initHookAfterDatabasePaused is announced.
#. After logging a pause message, initHookAfterIocPaused is announced.

Changing iocCore fixed limits
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following commands can be issued after iocCore is loaded to change
iocCore fixed limits. The commands should be given before any
dbLoadDatabase commands.

.. code ::

        callbackSetQueueSize(size)
        dbPvdTableSize(size)
        scanOnceSetQueueSize(size)
        errlogInit(buffersize)
        errlogInit2(buffersize, maxMessageSize)

callbackSetQueueSize
^^^^^^^^^^^^^^^^^^^^

Requests for the general purpose callback tasks are placed in a ring
buffer. This command can be used to set the size for the ring buffers. The
default is 2000. A message is issued when a ring buffer overflows. It
should rarely be necessary to override this default. Normally the ring
buffer overflow messages appear when a callback task fails.

dbPvdTableSize
^^^^^^^^^^^^^^

Record instance names are stored in a process variable directory, which
is a hash table. The default number of hash entries is 512.
dbPvdTableSize can be called to change the size. It must be called
before any dbLoad commands and must be a power of 2 between 256 and
65536. If an IOC contains very large databases (several thousand
records) then a larger hash table size speeds up searches for records.

scanOnceSetQueueSize
^^^^^^^^^^^^^^^^^^^^

scanOnce requests are placed in a ring buffer. This command can be used
to set the size for the ring buffer. The default is 1000. It should
rarely be necessary to override this default. Normally the ring buffer
overflow messages appear when the scanOnce task fails.

errlogInit or errlogInit2
^^^^^^^^^^^^^^^^^^^^^^^^^

These commands can increase (but not decrease) the default buffer and
maximum message sizes for the errlog message queue. The default buffer
size is 1280 bytes, the maximum message size defaults to 256 bytes.

initHooks
~~~~~~~~~

The inithooks facility allows application functions to be called at
various states during ioc initialization. The states are defined in
initHooks.h, which contains the following definitions:

.. code ::

   typedef enum {
       initHookAtIocBuild = 0,         / * Start of iocBuild/iocInit commands  */
       initHookAtBeginning,
       initHookAfterCallbackInit,
       initHookAfterCaLinkInit,
       initHookAfterInitDrvSup,
       initHookAfterInitRecSup,
       initHookAfterInitDevSup,
       initHookAfterInitDatabase,
       initHookAfterFinishDevSup,
       initHookAfterScanInit,
       initHookAfterInitialProcess,
       initHookAfterCaServerInit,
       initHookAfterIocBuilt,          / * End of iocBuild command  */

       initHookAtIocRun,               / * Start of iocRun command  */
       initHookAfterDatabaseRunning,
       initHookAfterCaServerRunning,
       initHookAfterIocRunning,        / * End of iocRun/iocInit commands  */

       initHookAtIocPause,             / * Start of iocPause command  */
       initHookAfterCaServerPaused,
       initHookAfterDatabasePaused,
       initHookAfterIocPaused,         / * End of iocPause command  */

   / * Deprecated states, provided for backwards compatibility.
     * These states are announced at the same point they were before,
     * but will not be repeated if the IOC gets paused and restarted.
     */
       initHookAfterInterruptAccept,   / * After initHookAfterDatabaseRunning  */
       initHookAtEnd,                  / * Before initHookAfterIocRunning  */
   }initHookState;

   typedef void ( *initHookFunction)(initHookState state);
   int initHookRegister(initHookFunction func);
   const char  *initHookName(int state);

Any functions that are registered before iocInit reaches the desired
state will be called when it reaches that state. The initHookName
function returns a static string representation of the state passed into
it which is intended for printing. The following skeleton code shows how
to use this facility:

.. code ::

   static initHookFunction myHookFunction;

   int myHookInit(void)
   {
     return(initHookRegister(myHookFunction));
   }

   static void myHookFunction(initHookState state)
   {
     switch(state) {
       case initHookAfterInitRecSup:
         ...
         break;
       case initHookAfterInterruptAccept:
         ...
         break;
       default:
         break;
     }
   }

An arbitrary number of functions can be registered.

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

Various environment variables are used by iocCore:

.. code ::

        EPICS_CA_ADDR_LIST
        EPICS_CA_AUTO_ADDR_LIST
        EPICS_CA_CONN_TMO
        EPICS_CAS_BEACON_PERIOD
        EPICS_CA_REPEATER_PORT
        EPICS_CA_SERVER_PORT
        EPICS_CA_MAX_ARRAY_BYTES
        EPICS_TS_NTP_INET
        EPICS_IOC_LOG_PORT
        EPICS_IOC_LOG_INET

For an explanation of the EPICS_CA\_... and EPICS_CAS\_... variables see
the EPICS Channel Access Reference Manual. For an explanation of the
EPICS_IOC_LOG\_... variables see "iocLogClient" (To be added).
EPICS_TS_NTP_INET is used only on vxWorks and RTEMS, where it sets the
address of the Network Time Protocol server. If it is not defined the IOC
uses the boot server as its NTP server.

These variables can be set through iocsh via the epicsEnvSet command, or
on vxWorks using putenv. For example:

.. code ::

        epicsEnvSet("EPICS_CA_CONN_TMO,"10")

All epicsEnvSet commands should be issued after iocCore is loaded and
before any dbLoad commands.

The following commands can be issued to iocsh:

**epicsPrtEnvParams** - This shows just the environment variables used by
iocCore.

**epicsEnvShow** - This shows all environment variables on your system.

Initialize Logging
~~~~~~~~~~~~~~~~~~~~~~

Initialize the logging system. See the chapter on "IOC Error Logging"
for details. The following can be used to direct the log client to use a
specific host log server.

.. code ::

        epicsEnvSet("EPICS_IOC_LOG_PORT", "<port>")
        epicsEnvSet("EPICS_IOC_LOG_INET", "<inet addr>")

These command must be given immediately after iocCore is loaded.

To start logging you must issue the command:

.. code ::

        iocLogInit
