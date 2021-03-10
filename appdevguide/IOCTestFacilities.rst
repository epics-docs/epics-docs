IOC Test Facilities
===================

.. contents:: Table of Contents
 :depth: 3

Overview
--------

This chapter describes a number of IOC test routines that are of
interest to both application developers and system developers. The
routines are available from either iocsh or the vxWorks shell. In both
shells the parentheses around arguments are optional. On vxWorks all
character string arguments must be enclosed in double quote characters
``""`` and all arguments must be separated by commas. For iocsh single
or double quotes must be used around string arguments that contain
spaces or commas but are otherwise optional, and arguments may be
separated by either commas or spaces. For example:

::

   dbpf("aiTest","2")
   dbpf "aiTest","2"

are both valid with both iocsh and with the vxWorks shell.

::

   dbpf aiTest 2

Is valid for iocsh but not for the vxWorks shell.

Both iosch and vxWorks shells allow output redirection, i.e. the
standard output of any command can be redirected to a file. For example

::

   dbl > dbl.lst

will send the output of the ``dbl`` command to the file ``dbl.lst``

If iocsh is being used it provides help for all commands that have been
registered. Just type

::

   help

or

::

   help pattern*

Database List, Get, Put
-----------------------

dbl
~~~

Database List:

::

   dbl("<record type>","<field list>")

Examples

::

   dbl
   dbl("ai")
   dbl("*")
   dbl("")

This command prints the names of records in the run time database. If
``<record type>`` is empty ``("")``, ``"*"``, or not specified, all
records are listed. If ``<record type>`` is specified, then only the
names of the records of that type are listed.

If ``<field list>`` is given and not empty then the values of the fields
specified are also printed.

dbgrep
~~~~~~

List Record Names That Match a Pattern:

::

   dbgrep("<pattern>")

Examples

::

   dbgrep("S0*")
   dbgrep("*gpibAi*")

Lists all record names that match a pattern. The pattern can contain any
characters that are legal in record names as well as "``*``", which
matches 0 or more characters.

dbla
~~~~

List Record Alias Names with optional pattern:

::

   dbla
   dbla("<pattern>")

Lists the names of all aliases (which match the pattern if given) and
the records they refer to. Examples:

::

   dbla
   dbla "alia*"

dba
~~~

Database Address:

::

   dba("<record_name.field_name>")

Example

::

   dba("aitest")
   dba("aitest.VAL")

This command calls ``dbNameToAddr`` and then prints the value of each
field in the ``dbAddr`` structure describing the field. If the field
name is not specified then ``VAL`` is assumed (the two examples above
are equivalent).

dbgf
~~~~

Get Field:

::

   dbgf("<record_name.field_name>")

Example:

::

   dbgf("aitest")
   dbgf("aitest.VAL")

This performs a ``dbNameToAddr`` and then a ``dbGetField``. It prints
the field type and value. If the field name is not specified then
``VAL`` is assumed (the two examples above are equivalent). Note that
``dbGetField`` locks the record lockset, so ``dbgf`` will not work on a
record with a stuck lockset; use ``dbpr`` instead in this case.

dbpf
~~~~

Put Field:

::

   dbpf("<record_name.field_name>","<value>")

Example:

::

   dbpf("aitest","5.0")

This command performs a ``dbNameToAddr`` followed by a ``dbPutField``
and ``dbgf``. If ``<field_name>`` is not specified ``VAL`` is assumed.

dbpr
~~~~

Print Record:

::

   dbpr("<record_name>",<interest level>)

Example

::

   dbpr("aitest",2)

This command prints all fields of the specified record up to and
including those with the indicated interest level. Interest level has
one of the following values:

-  0: Fields of interest to an Application developer and that can be
   changed as a result of record processing.

-  1: Fields of interest to an Application developer and that do not
   change during record processing.

-  2: Fields of major interest to a System developer.

-  3: Fields of minor interest to a System developer.

-  4: Fields of no interest.

dbtr
~~~~

Test Record:

::

   dbtr("<record_name>")

This calls ``dbNameToAddr``, then ``dbProcess`` and finally ``dbpr``
(interest level 3). Its purpose is to test record processing.

dbnr
~~~~

Print number of records:

::

   dbnr(<all_recordtypes>)

This command displays the number of records of each type and the total
number of records. If ``all_record_types`` is 0 then only record types
with record instances are displayed otherwise all record types are
displayed.

Breakpoints
-----------

A breakpoint facility that allows the user to step through database
processing on a per lockset basis. This facility has been constructed in
such a way that the execution of all locksets other than ones with
breakpoints will not be interrupted. This was done by executing the
records in the context of a separate task.

The breakpoint facility records all attempts to process records in a
lockset containing breakpoints. A record that is processed through
external means, e.g.: a scan task, is called an entrypoint into that
lockset. The ``dbstat`` command described below will list all detected
entrypoints to a lockset, and at what rate they have been detected.

dbb
~~~

Set Breakpoint:

::

   dbb("<record_name>")

Sets a breakpoint in a record. Automatically spawns the ``bkptCont``, or
breakpoint continuation task (one per lockset). Further record execution
in this lockset is run within this task’s context. This task will
automatically quit if two conditions are met, all breakpoints have been
removed from records within the lockset, and all breakpoints within the
lockset have been continued.

dbd
~~~

Remove Breakpoint:

::

   dbd("<record_name>")

Removes a breakpoint from a record.

dbs
~~~

Single Step:

::

   dbs("<record_name>")

Steps through execution of records within a lockset. If this command is
called without an argument, it will automatically step starting with the
last detected breakpoint.

dbc
~~~

Continue:

::

   dbc("<record_name>")

Continues execution until another breakpoint is found. This command may
also be called without an argument.

dbp
~~~~

Print Fields Of Suspended Record:

::

   dbp("<record_name>,<interest_level>)

Prints out the fields of the last record whose execution was suspended.

dbap
~~~~

Auto Print:

::

   dbap("<record_name>")

Toggles the automatic record printing feature. If this feature is
enabled for a given record, it will automatically be printed after the
record is processed.

dbstat
~~~~~~

Status:

::

   dbstat

Prints out the status of all locksets that are suspended or contain
breakpoints. This lists all the records with breakpoints set, what
records have the autoprint feature set (by ``dbap``), and what
entrypoints have been detected. It also displays the vxWorks task ID of
the breakpoint continuation task for the lockset. Here is an example
output from this call:

::

   LSet: 00009  Stopped at: so#B: 00001   T: 0x23cafac
                Entrypoint: so#C: 00001   C/S:     0.1
                Breakpoint: so(ap)
   LSet: 00008#B: 00001   T: 0x22fee4c
                Breakpoint: output

The above indicates that two locksets contain breakpoints. One lockset
is stopped at record “\ ``so``." The other is not currently stopped, but
contains a breakpoint at record “\ ``output``." “\ ``LSet:``" is the
lockset number that is being considered. "``#B:``" is the number of
breakpoints set in records within that lockset. “\ ``T:``" is the
vxWorks task ID of the continuation task. “\ ``C:``" is the total number
of calls to the entrypoint that have been detected. “\ ``C/S:``" is the
number of those calls that have been detected per second. ``(ap)``
indicates that the autoprint feature has been turned on for record
“\ ``so``."

Trace Processing
----------------

The user should also be aware of the field ``TPRO``, which is present in
every database record. If it is set ``TRUE`` then a message is printed
each time its record is processed and a message is printed for each
record processed as a result of it being processed.

Error Logging
-------------

eltc
~~~~

Display error log messages on console:

::

   eltc(int noYes)

This determines if error messages are displayed on the IOC console. 0
means no and any other value means yes.

errlogInit, errlogInit2
~~~~~~~~~~~~~~~~~~~~~~~

Initialize error log client buffering

::

   errlogInit(int bufSize)
   errlogInit2(int bufSize, int maxMsgSize)

The error log client maintains a circular buffer of messages that are
waiting to be sent to the log server. If not set using one or other of
these routines the default value for bufSize is 1280 bytes and for
maxMsgSize is 256 bytes.

errlog
~~~~~~

Send a message to the log server

::

   errlog("<message>")

This command is provided for use from the ioc shell only. It sends its
string argument and a new-line to the log server, without displaying it
on the IOC console. Note that the iocsh will have expanded any
environment variable macros in the string (if it was double-quoted)
before passing it to errlog.

Hardware Reports
----------------

dbior
~~~~~

I/O Report:

::

   dbior ("<driver_name>",<interest level>)

This command calls the report entry of the indicated driver. If
``<driver_name>`` is ““ or \*, then a report for all drivers is
generated. The command also calls the report entry of all device support
modules. Interest level is one of the following:

-  0: Print a short report for each module.

-  1: Print additional information.

-  2: Print even more info. The user may be prompted for options.

dbhcr
~~~~~

Hardware Configuration Report:

::

   dbhcr()

This command produces a report of all hardware links. To use it on the
IOC, issue the command:

::

   dbhcr > report

The report will probably not be in the sort order desired. The Unix
command:

::

   sort report > report.sort

should produce the sort order you desire.

Scan Reports
------------

scanppl
~~~~~~~

Print Periodic Lists:

::

   scanppl(double rate)

This routine prints a list of all records in the periodic scan list of
the specified rate. If rate is 0.0 all period lists are shown.

scanpel
~~~~~~~

Print Event Lists:

::

   scanpel(int event_number)

This routine prints a list of all records in the event scan list for the
specified event nunber. If event_number is 0 all event scan lists are
shown.

scanpiol
~~~~~~~~

Print I/O Event Lists:

::

   scanpiol

This routine prints a list of all records in the I/O event scan lists.

General Time
------------

The built-in time providers depend on the IOC’s target architecture, so
some of the specific subsystem report commands listed below are only
available on the architectures that use that particular provider.

generalTimeReport
~~~~~~~~~~~~~~~~~

Format:

::

   generalTimeReport(int level)

This routine displays the time providers and their priority levels that
have registered with the General Time subsystem for both current and
event times. At level 1 it also shows the current time as obtained from
each provider.

installLastResortEventProvider
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Format:

::

   installLastResortEventProvider

Installs the optional Last Resort event provider at priority 999, which
returns the current time for every event number.

NTPTime_Report
~~~~~~~~~~~~~~

Format:

::

   NTPTime_Report(int level)

Only vxWorks and RTEMS targets use this time provider. The report
displays the provider’s synchronization state, and at interest level 1
it also gives the synchronization interval, when it last synchronized,
the nominal and measured system tick rates, and on vxWorks the NTP
server address.

NTPTime_Shutdown
~~~~~~~~~~~~~~~~

Format:

::

   NTPTime_Shutdown

On vxWorks and RTEMS this command shuts down the NTP time
synchronization thread. With the thread shut down, the driver will no
longer act as a current time provider.

ClockTime_Report
~~~~~~~~~~~~~~~~

Format:

::

   ClockTime_Report(int level)

This time provider is used on several target architectures, registered
as the time provider of last resort. On vxWorks and RTEMS the report
displays the synchronization state, when it last synchronized the system
time with a higher priority provider, and the synchronization interval.
On workstation operating systems the synchronization task is not started
on the assumption that some other process is taking care of synchronzing
the OS clock as appropriate, so the report is minimal.

ClockTime_Shutdown
~~~~~~~~~~~~~~~~~~

Format:

::

   ClockTime_Shutdown

Some sites may prefer to provide their own implementation of a system
clock time provider to replace the built-in one. On vxWorks and RTEMS
this command stops the OS Clock synchronization thread, allowing the OS
clock to free-run. The time provider *will* continue to return the
current system time after this command is used however.

Access Security Commands
------------------------

asSetSubstitutions
~~~~~~~~~~~~~~~~~~

Format:

::

   asSetSubstitutions("substitutions")

Specifies macro substitutions used when access security is initialized.

asSetFilename
~~~~~~~~~~~~~

Format:

::

   asSetFilename("<filename>")

This command defines a new access security file.

asInit
~~~~~~

Format:

::

   asInit

This command reinitializes the access security system. It rereads the
access security file in order to create the new access security
database. This command is useful either because the ``asSetFilename``
command was used to change the file or because the file itself was
modified. Note that it is also possible to reinitialize the access
security via a subroutine record. See the access security document for
details.

asdbdump
~~~~~~~~

Format:

::

   asdbdump

This provides a complete dump of the access security database.

aspuag
~~~~~~

Format:

::

   aspuag("<user access group>")

Print the members of the user access group. If no user access group is
specified then the members of all user access groups are displayed.

asphag
~~~~~~

Format:

::

   asphag("<host access group>")

Print the members of the host access group. If no host access group is
specified then the members of all host access groups are displayed.

asprules
~~~~~~~~

Format:

::

   asprules("<access security group>")

Print the rules for the specified access security group or if no group
is specified for all groups.

aspmem
~~~~~~

Format:

::

   aspmem("<access security group>", <print clients>)

Print the members (records) that belong to the specified access security
group, for all groups if no group is specified. If ``<print clients>``
is (0, 1) then Channel Access clients attached to each member (are not,
are) shown.

Channel Access Reports
----------------------

casr
~~~~

Channel Access Server Report

::

   casr(<level>)

Level can have one of the following values:

0

Prints server’s protocol version level and a one line summary for each
client attached. The summary lines contain the client’s login name,
client’s host name, client’s protocol version number, and the number of
channel created within the server by the client.

1

Level one provides all information in level 0 and adds the task id used
by the server for each client, the client’s IP protocol type, the file
number used by the server for the client, the number of seconds elapsed
since the last request was received from the client, the number of
seconds elapsed since the last response was sent to the client, the
number of unprocessed request bytes from the client, the number of
response bytes which have not been flushed to the client, the client’s
IP address, the client’s port number, and the client’s state.

2

Level two provides all information in levels 0 and 1 and adds the number
of bytes allocated by each client and a list of channel names used by
each client. Level 2 also provides information about the number of bytes
in the server’s free memory pool, the distribution of entries in the
server’s resource hash table, and the list of IP addresses to which the
server is sending beacons. The channel names are shown in the form:

<name>(nrw)

where

n is number of ca_add_events the client has on this channel

r is (-,R) if client (does not, does) have read access to the channel.

w is(-, W) if client (does not, does) have write access to the channel.

dbel
~~~~

Format:

::

   dbel("<record_name>")

This routine prints the Channel Access event list for the specified
record.

dbcar
~~~~~

Database to Channel Access Report - See “Record Link Reports"

ascar
~~~~~

Format:

::

   ascar(level)

Prints a report of the channel access links for the INP fields of the
access security rules. Level 0 produces a summary report. Level 1
produces a summary report plus details on any unconnect channels. Level
2 produces the summary nreport plus a detail report on each channel.

Interrupt Vectors
-----------------

veclist
~~~~~~~

Format:

::

   veclist

NOTE: This routine is only available on vxWorks. On PowerPC CPUs it
requires BSP support to work, and even then it cannot display chained
interrupts using the same vector.

Print Interrupt Vector List

Miscellaneous
-------------

epicsParamShow
~~~~~~~~~~~~~~

Format:

::

   epicsParamShow

or

::

   epicsPrtEnvParams

Print the environment variables that are created with epicsEnvSet. These
are defined in <base>/config/CONFIG_ENV and
<base>/config/CONFIG_SITE_ENV or else by user applications calling
``epicsEnvSet``.

epicsEnvShow
~~~~~~~~~~~~

Format:

::

   epicsEnvShow("<name>")

Show Environment variables. On vxWorks it shows the variables created
via calls to ``putenv``.

coreRelease
~~~~~~~~~~~

Format:

::

   coreRelease

Print release information for iocCore.

Database System Test Routines
-----------------------------

These routines are normally only of interest to EPICS system developers
NOT to Application Developers.

dbtgf
~~~~~

Test Get Field:

::

   dbtgf("<record_name.field_name>")

Example:

::

   dbtgf("aitest")
   dbtgf("aitest.VAL")

This performs a ``dbNameToAddr`` and then calls ``dbGetField`` with all
possible request types and options. It prints the results of each call.
This routine is of most interest to system developers for testing
database access.

dbtpf
~~~~~

Test Put Field:

::

   dbtpf("<record_name.field_name>","<value>")

Example:

::

   dbtpf("aitest","5.0")

This command performs a ``dbNameToAddr``, then calls ``dbPutField``,
followed by ``dbgf`` for each possible request type. This routine is of
interest to system developers for testing database access.

dbtpn
~~~~~

Test Process Notify:

::

   dbtpn("<record_name.field_name>")
   dbtpn("<record_name.field_name>","<value>")

Example:

::

   dbtpn("aitest")
   dbtpn("aitest","5.0")

This command performs a ``dbProcessNotify`` request. If a non-null value
argument string is provided it issues a ``putProcessRequest`` to the
named record; if no value is provided it issues a ``processGetRequest``.
This routine is mainly of interest to system developers for testing
database access.

Record Link Reports
-------------------

dblsr
~~~~~

Lock Set Report:

::

   dblsr(<recordname>,<level>)

This command generates a report showing the lock set to which each
record belongs. If ``recordname`` is 0, ``""``, or ``"*"`` all records
are shown, otherwise only records in the same lock set as ``recordname``
are shown.

``level`` can have the following values:

0 - Show lock set information only.

1 - Show each record in the lock set.

2 - Show each record and all database links in the lock set.

dbLockShowLocked
~~~~~~~~~~~~~~~~

Show locked locksets:

::

   dbLockShowLocked(<level>)

This command generates a report showing all locked locksets, the records
they contain, the lockset state and the thread that currently owns the
lockset. The ``level`` argument is passed to ``epicsMutexShow`` to
adjust the information reported about each locked epicsMutex.

.. _dbcar-1:

dbcar
~~~~~

Database to channel access report

::

   dbcar(<recordname>,<level>)

This command generates a report showing database channel access links.
If ``recordname`` is “\*“ then information about all records is shown
otherwise only information about the specified record.

``level`` can have the following values:

0 - Show summary information only.

1 - Show summary and each CA link that is not connected.

2 - Show summary and status of each CA link.

.. _dbhcr-1:

dbhcr
~~~~~

Report hardware links. See “Hardware Reports".

Old Database Access Testing
---------------------------

These routines are of interest to EPICS system developers. They are used
to test the old database access interface, which is still used by
Channel Access.

gft
~~~

Get Field Test:

::

   gft("<record_name.field_name>")

Example:

::

   gft("aitest")
   gft("aitest.VAL")

This performs a ``db_name_to_addr`` and then calls ``db_get_field`` with
all possible request types. It prints the results of each call. This
routine is of interest to system developers for testing database access.

pft
~~~

Put Field Test:

::

   pft("<record_name.field_name>","<value>")

Example:

::

   pft("aitest","5.0")

This command performs a ``db_name_to_addr``, ``db_put_field``,
``db_get_field`` and prints the result for each possible request type.
This routine is of interest to system developers for testing database
access.

tpn
~~~

Test Process Notify:

::

   tpn("<record_name.field_name>","<value>")

Example:

::

   tpn("aitest","5.0")

This routine tests the ``dbProcessNotify`` API when used via the old
database access interface. It only supports issuing a
``putProcessRequest`` to the named record.

Routines to dump database information
-------------------------------------

dbDumpPath
~~~~~~~~~~

Dump Path:

::

   dbDumpPath(pdbbase)

Example:

::

   dbDumpPath(pdbbase)

The current path for database includes is displayed.

dbDumpMenu
~~~~~~~~~~

Dump Menu:

::

   dbDumpMenu(pdbbase,"<menu>")

Example:

::

   dbDumpMenu(pdbbase,"menuScan")

If the second argument is 0 then all menus are displayed.

dbDumpRecordType
~~~~~~~~~~~~~~~~

Dump Record Description:

::

   dbDumpRecordType(pdbbase,"<record type>")

Example:

::

   dbDumpRecordType(pdbbase,"ai")

If the second argument is 0 then all descriptions of all records are
displayed.

dbDumpField
~~~~~~~~~~~

Dump Field Description:

::

   dbDumpField(pdbbase,"<record type>","<field name>")

Example:

::

   dbDumpField(pdbbase,"ai","VAL")

If the second argument is 0 then the field descriptions of all records
are displayed. If the third argument is 0 then the description of all
fields are displayed.

dbDumpDevice
~~~~~~~~~~~~

Dump Device Support:

::

   dbDumpDevice(pdbbase,"<record type>")

Example:

::

   dbDumpDevice(pdbbase,"ai")

If the second argument is 0 then the device support for all record types
is displayed.

dbDumpDriver
~~~~~~~~~~~~

Dump Driver Support:

::

   dbDumpDriver(pdbbase)

Example:

::

   dbDumpDriver(pdbbase)

dbDumpRecord
~~~~~~~~~~~~

Dump Record Instances:

::

   dbDumpRecord(pdbbase,"<record type>",level)

Example:

::

   dbDumpRecords(pdbbase,"ai")

If the second argument is 0 then the record instances for all record
types are displayed. The third argument determines which fields are
displayed just like for the command ``dbpr``.

dbDumpBreaktable
~~~~~~~~~~~~~~~~

Dump breakpoint table

::

   dbDumpBreaktable(pdbbase,name)

Example:

::

   dbDumpBreaktable(pdbbase,"typeKdegF")

This command dumps a breakpoint table. If the second argument is 0 all
breakpoint tables are dumped.

dbPvdDump
~~~~~~~~~

Dump the Process variable Directory:

::

   dbPvdDump(pdbbase,verbose)

Example:

::

   dbPvdDump(pdbbase,0)

This command shows how many records are mapped to each hash table entry
of the process variable directory. If verbose is not 0 then the command
also displays the names which hash to each hash table entry.
