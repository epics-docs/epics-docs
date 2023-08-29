This chapter covers the general functionality that is found in all
database records.
The topics covered are I/O scanning,
I/O address
specification,
data conversions,
alarms,
database monitoring,
and continuous control:

-  [Scanning Specification](#Scanning_Specification) describes the various conditions under which
   a record is processed.

-  [Address Specification](#Address_Specification) explains the source of inputs and the
   destination of outputs.

-  [Conversion Specification](#Conversion_Specification) covers data conversions from transducer
   interfaces to engineering units.

-  [Alarm Specification](#Alarm_Specification) presents the many alarm detection mechanisms
   available in the database.

-  [Monitor Specification](Monitor_Specification) details the mechanism, which notifies
   operators about database value changes.

-  [Control Specification](#Control_Specification) explains the features available for achieving
   continuous control in the database.

These concepts are essential in order to understand how
the database interfaces with the process.

The EPICS databases can be created by manual creation of a database
"myDatabase.db" text file
or using visual tools (VDCT, CapFast).
Visual Database Configuration Tool (VDCT),
a java application from Cosylab,
is a tool for database creation/editing
that runs on Linux, Windows, and Sun.
The illustrations in this document have been created with VDCT.
