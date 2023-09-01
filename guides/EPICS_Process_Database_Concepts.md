# Epics Process Database Concepts

An EPICS-based control system contains one or more Input Output Controller (IOC).
Each IOC loads one or more databases.
A database is a collection of records of various types.

A Record is an object with:

- A unique name
- A behavior defined by its type
- Controllable properties (fields)
- Optional associated hardware I/O (device support)
- Links to other records

Several different types of record are available.
In addition to the record types that are included in the EPICS base software package,
it's possible to create your own record type to perform some specific tasks.
It isn't recommended to do this unless you absolutely need to.

Each record comprises a number of **fields**. 
Fields can have different functions,
typically they're used to configure how the record operates,
or to store data items.

Below are short descriptions for the most commonly used record types:

**Analog Input and Output (AI and AO)** records
can store an analog value,
and are typically used for things like set-points,
temperatures, pressure, flow rates, etc. 
The records perform number of functions like
data conversions, alarm processing, filtering, etc.

**Binary Input and Output (BI and BO)** records
are generally used for commands and statuses to and from equipment.
As the name indicates,
they store binary values like On/Off, Open/Closed, etc.

**Calc and Calcout** records
can access other records
and perform a calculation based on their values.
For example, calculate the efficiency of a motor 
by a function of the current and voltage input and output,
and converting to a percentage for the operator to read).

## Database functionality specification

This Section covers the general functionality that's found in all database records.
The topics covered are I/O scanning, I/O address specification,
data conversions, alarms, database monitoring, and continuous control:



-  [*Scanning Specification*](Scanning_Specification.md) describes the various conditions under which a record is processed.

-  [*Address Specification*](Address_Specification.md) explains the source of inputs and the destination of outputs.

-  [*Conversion Specification*](Conversion_Specification.md) covers data conversions from transducer interfaces to engineering units.

-  *Alarm Specification* presents the many alarm detection mechanisms available in the database.

-  *Monitor Specification* details the mechanism, which notifies operators about database value changes.

-  *Control Specification* explains the features available for achieving continuous control in the database.

These concepts are essential to understand how the database interfaces with the process.

The EPICS databases can be created by manual creation of a database "myDatabase.db" text file
or using visual tools (VDCT, CapFast).
Visual Database Configuration Tool (VDCT), a java application from Cosylab,
is a tool for database creation/editing that runs on Linux, Windows, and Sun.
The illustrations in this document have been created with VDCT.

