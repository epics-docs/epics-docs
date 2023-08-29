An EPICS-based control system contains one or more Input Output Controllers, IOCs.
Each IOC loads one or more databases.
A database is a collection of records of various types.

A Record is an object with:

- A unique name
- A behavior defined by its type
- Controllable properties (fields)
- Optional associated hardware I/O (device support)
- Links to other records

There are several different types of records available.
In addition to the record types that are included in the EPICS base software package,
it is possible
(although not recommended unless you absolutely need)
to create your own record type to perform some specific tasks.

Each record comprises a number of **fields**. 
Fields can have different functions,
typically they are used to configure how the record operates,
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
they store binary values like On/Off, Open/Closed and so on.

**Calc and Calcout** records
can access other records
and perform a calculation based on their values.
(E.g. calculate the efficiency of a motor 
y a function of the current and voltage input and output,
and converting to a percentage for the operator to read).
