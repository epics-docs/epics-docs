Database Definition
===================

.. tags:: developer, advanced

Overview
--------

This chapter describes database definitions. The following definitions
are described:

-  Menu

-  Record Type

-  Device

-  Driver

-  Registrar

-  Variable

-  Function

-  Breakpoint Table

-  Record Instance

Record Instances are fundamentally different from the other definitions.
A file containing record instances should never contain any of the other
definitions and vice-versa. Thus the following convention is followed:

Database Definition File
   A file that contains any type of definition except record instances.

Record Instance File
   A file that contains only record instance definitions.

This chapter also describes utility programs which operate on these
definitions.

Any combination of definitions can appear in a single file or in a set
of files related to each other via include statements.

Summary of Database Syntax
--------------------------

The following summarizes the Database Definition syntax:

::

   path "path"
   addpath "path"
   include "filename"
   #comment
   menu(name) {
       include "filename"
       choice(choice_name, "choice_value")
       ...
   }

   recordtype(record_type) {}

   recordtype(record_type) {
       include "filename"
       field(field_name, field_type) {
           asl(asl_level)
           initial("init_value")
           promptgroup("group_name")
           prompt("prompt_value")
           special(special_value)
           pp(pp_value)
           interest(interest_level)
           base(base_type)
           size(size_value)
           extra("extra_info")
           menu(name)
           prop(yesno)
       }
       %C_declaration
       ...
   }

   device(record_type, link_type, dset_name, "choice_string")

   driver(drvet_name)

   registrar(function_name)

   variable(variable_name)

   breaktable(name) {
       raw_value eng_value
       ...
   }

The Following defines a Record Instance

::

   record(record_type, record_name) {
       include "filename"
       field(field_name, "value")
       alias(alias_name)
       info(info_name, "value")
       ...
   }
   alias(record_name,alias_name)

General Rules for Database Definition
-------------------------------------

Keywords
~~~~~~~~

The following are keywords, i.e. they may not be used as values unless
they are enclosed in quotes:

::

   path
   addpath
   include
   menu
   choice
   recordtype
   field
   device
   driver
   registrar
   function
   variable
   breaktable
   record
   grecord
   info
   alias

Unquoted Strings
~~~~~~~~~~~~~~~~

In the summary section, some values are shown as quoted strings and some
unquoted. The actual rule is that any string consisting of only the
following characters does not need to be quoted unless it contains one
of the above keywords:

::

   a-z A-Z 0-9 _ + - : . [ ] < > ;

These are all legal characters for process variable names, although
``.`` is not allowed in a record name since it separates the record from
the field name in a PV name. Thus in many cases quotes are not needed
around record or field names in database files. Any string containing a
macro does need to be quoted though.

Quoted Strings
~~~~~~~~~~~~~~

A quoted string can contain any ascii character except the quote
character ``"``. The quote character itself can given by using a
back-slash (``\``) as an escape character. For example ``"\""`` is a
quoted string containing a single double-quote character.

Macro Substitution
~~~~~~~~~~~~~~~~~~

Macro substitutions are permitted inside quoted strings. Macro instances
take the form:

::

   $(name)

or

::

   ${name}

There is no distinction between the use of parentheses or braces for
delimiters, although the opening and closing characters must match for
each macro instance. A macro name can be constructed using other macros,
for example:

::

   $(name_$(sel))

A macro instance can also provide a default value that is used when no
macro with the given name has been defined. The default value can itself
be defined in terms of other macros if desired, but may not contain any
unescaped comma characters. The syntax for specifying a default value is
as follows:

::

   $(name=default)

Finally macro instances can also set the values of other macros which
may (temporarily) override any existing values for those macros, but the
new values are in scope only for the duration of the expansion of this
particular macro instance. These definitions consist of ``name=value``
sequences separated by commas, for example:

::

   $(abcd=$(a)$(b)$(c)$(d),a=A,b=B,c=C,d=D)

.. _subsec:Escape Sequences:

Escape Sequences
~~~~~~~~~~~~~~~~

The database routines translate standard C escape sequences inside
database field value strings only. The standard C escape sequences
supported are:

::

   \a \b \f \n \r \t \v \\ \' \" \ooo \xhh

``\ooo`` represents an octal number with 1, 2, or 3 digits. ``\xhh``
represents a hexadecimal number which may have any number of hex digits,
although only the last 2 will be represented in the character generated.

Comments
~~~~~~~~

The comment symbol is “#”. Whenever the comment symbol appears outside
of a quoted string, it and all subsequent characters through the end of
the line will be ignored.

Define before referencing
~~~~~~~~~~~~~~~~~~~~~~~~~

In general items cannot be referenced until they have been defined. For
example a ``device`` definition cannot appear until the ``recordtype``
that it references has been defined or at least declared. Another
example is that a record instance cannot appear until its associated
record type has been defined.

One notable exception to this rule is that within a ``recordtype``
definition a menu field may reference a menu that has not been included
directly by the record’s ``.dbd`` file.

Multiple Definitions
~~~~~~~~~~~~~~~~~~~~

If a menu, device, driver, or breakpoint table is defined more than
once, then only the first instance will be used. Subsequent definitions
may be compared to the first one and an error reported if they are
different (the ``dbdExpand.pl`` program does this, the IOC currently
does not). Record type definitions may only be loaded once; duplicates
will cause an error even if the later definitions are identical to the
first. However a record type declaration may be used in place of the
record type definition in ``.dbd`` files that define device support for
that type.

Record instance definitions are (normally) cumulative, so multiple
instances of the same record may be loaded and each time a field value
is encountered it replaces the previous value.

Filename Extensions
~~~~~~~~~~~~~~~~~~~

By convention:

-  Record instances files have the extension “``.db``” or “``.vdb``” if
   the file also contains visual layout information

-  Database definition files have the extension “``.dbd``”

Database Definition Statements
------------------------------

``path addpath`` – Path Definition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Format
^^^^^^

::

   path "dir:dir...:dir"
   addpath "dir:dir...:dir"

The path string follows the standard convention for the operating
system, i.e. directory names are separated by a colon “``:``” on Unix
and a semicolon “``;``” on Windows.

The ``path`` statement specifies the current search path for use when
loading database and database definition files. The ``addpath``
statement appends directories to the current path. The path is used to
locate the initial database file and included files. An empty path
component at the beginning, middle, or end of a non-empty path string
means search the current directory. For example:

::

   nnn::mmm    # Current directory is between nnn and mmm
   :nnn        # Current directory is first
   nnn:        # Current directory is last

Utilities which load database files (``dbExpand``, ``dbLoadDatabase``,
etc.) allow the user to specify an initial path. The ``path`` and
``addpath`` commands can be used to change or extend that initial path.

The initial path is determined as follows:

#. If path is provided with the command, it is used. Else:

#. If the environment variable ``EPICS_DB_INCLUDE_PATH`` is defined, it
   is used. Else:

#. the path is “``.``”, i.e. the current directory.

The search path is not used at all if the filename being searched for
contains a ``/`` or ``\`` character. The first instance of the specified
filename is used.

``include`` – Include Statement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _format-1:

Format
^^^^^^

::

   include "filename"

An include statement can appear at any place shown in the summary. It
uses the search path as described above to locate the named file.

``menu`` – Menu Definition
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _format-2:

Format
^^^^^^

::

   menu(name) {
       choice(choice_name, "choice_string")
       ...
   }

Definitions
^^^^^^^^^^^

name
   Name for menu. This is the unique name identifying the menu. If
   duplicate definitions are specified, only the first is used.

choice_name
   The name used in the ``enum`` generated by ``dbdToMenuH.pl`` or
   ``dbdToRecordtypeH.pl``. This must be a legal C/C++ identifier.

choice_string
   The text string associated with this particular choice.

Example
^^^^^^^

::

   menu(menuYesNo) {
       choice(menuYesNoNO, "NO")
       choice(menuYesNoYES, "YES")
   }

``recordtype`` – Record Type Definition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _format-3:

Format
^^^^^^

::

   recordtype(record_type) {}

   recordtype(record_type) {
       field(field_name, field_type) {
           asl(as_level)
           initial("init_value")
           promptgroup("group_name")
           prompt("prompt_value")
           special(special_value)
           pp(pp_value)
           interest(interest_level)
           base(base_type)
           size(size_value)
           extra("extra_info")
           menu(name)
           prop(yesno)
       }
       %C_declaration
       ...
   }

A record type statement that provides no field descriptions is a
declaration, analagous to a function declaration (prototype) or forward
definition in C. It allows the given record type name to be used in
circumstances where the full record type definition is not needed.

Field Descriptor Rules
^^^^^^^^^^^^^^^^^^^^^^

asl
   Sets the Access Security Level for the field. Access Security is
   discussed in chapter `[Access Security] <#Access Security>`__.

initial
   Provides an initial (default) value for the field.

promptgroup
   The group to which the field belongs, for database configuration
   tools.

prompt
   A prompt string for database configuration tools. Optional if
   ``promptgroup`` is not defined.

special
   If specified, special processing is required for this field at run
   time.

pp
   Whether a passive record should be processed when Channel Access
   writes to this field.

interest
   Interest level for the field.

base
   For integer fields, the number base to use when converting the field
   value to a string.

size
   Must be specified for ``DBF_STRING`` fields.

extra
   Must be specified for ``DBF_NOACCESS`` fields.

menu
   Must be specified for ``DBF_MENU`` fields. It is the name of the
   associated menu.

prop
   Must be ``YES`` or ``NO`` (default). Indicates that the field holds
   Channel Access meta-data.

.. _definitions-1:

Definitions
^^^^^^^^^^^

record_type
   The unique name of the record type. Duplicate definitions are not
   allowed and will be rejected.

field_name
   The field name, which must be a valid C and C++ identifier. When
   include files are generated, the field name is converted to lower
   case for use as the record structure member name. If the lower-case
   version of the field name is a C or C++ keyword, the original name
   will be used for the structure member name instead. Previous versions
   of EPICS required the field name be a maximum of four all upper-case
   characters, but these restrictions no longer apply.

field_type
   This must be one of the following values:

   -  ``DBF_STRING``

   -  ``DBF_CHAR``, ``DBF_UCHAR``

   -  ``DBF_SHORT``, ``DBF_USHORT``

   -  ``DBF_LONG``, ``DBF_ULONG``

   -  ``DBF_FLOAT``, ``DBF_DOUBLE``

   -  ``DBF_ENUM``, ``DBF_MENU``, ``DBF_DEVICE``

   -  ``DBF_INLINK``, ``DBF_OUTLINK``, ``DBF_FWDLINK``

   -  ``DBF_NOACCESS``

as_level
   This must be one of the following values:

   -  ``ASL0``

   -  ``ASL1`` (default value)

   Fields which operators normally change are assigned ``ASL0``. Other
   fields are assigned ``ASL1``. For example, the ``VAL`` field of an
   analog output record is assigned ``ASL0`` and all other fields
   ``ASL1``. This is because only the ``VAL`` field should be modified
   during normal operations.

init_value
   A legal value for data type.

prompt_value
   A prompt value for database configuration tools.

group_name
   A string used by database configuration tools (DCTs) to group related
   fields together.

   A ``promptgroup`` should only be set for fields that can sensibly be
   configured in a record instance file.

   The set of group names is no longer fixed. In earlier versions of
   Base the predefined set of choices beginning ``GUI_`` were the only
   group names permitted. Now the group name strings found in the
   database definition file are collected and stored in a global list.
   The strings given for group names must match exactly for fields to be
   grouped together.

   To support sorting and handling of groups, the names used in Base
   have the following conventions:

   -  Names start with a two-digit number followed by a space-dash-space
      sequence.

   -  Names are designed to be presented in ascending numerical order.

   -  The group name (or possibly just the part following the dash) may
      be displayed by the tool as a title for the group.

   -  In many-of-the-same-kind cases (e.g. 21 similar inputs) fields are
      distributed over multiple groups. Once-only fields appear in
      groups numbered in multiples of 5 or 10. The groups with the
      multiple instances follow in +1 increments. This allows more
      sophisticated treatment, e.g. showing the first group open and the
      other groups collapsed.

   Record types may define their own group names. However, to improve
   consistency, records should use the following names from Base where
   possible. (This set also demonstrates that the group names used in
   different record types may share the same number.)

   -  General fields that are common to all or many record types

   -  Scanning mechanism, priority and related properties

   -  Record type specific behavior and processing action

   -  Links and related properties

   -  Input links and properties

   -  Output links and properties

   -  Conversion between raw and engineering values

   -  Alarm related properties, severities and thresholds

   -  Client related configuration, strings, deadbands

   -  Simulation mode related properties

   NOTE: Older versions of Base contained a header file ``guigroup.h``
   defining a fixed set of group names and their matching index numbers.
   That header file has been removed. The static database access library
   now provides functions to convert between group index keys and the
   associated group name strings. See
   `[subsec:Get Field Prompt] <#subsec:Get Field Prompt>`__ for details.

special_value
   Must be one of the following:

   -  ``SPC_MOD`` – Notify record support when modified. The record
      support ``special`` routine will be called whenever the field is
      modified by the database access routines.

   -  ``SPC_NOMOD`` – No external modifications allowed. This value
      disables external writes to the field, so it can only be set by
      the record or device support module.

   -  ``SPC_DBADDR`` – Use this if the record support’s ``cvt_dbaddr``
      routine should be called to adjust the field description when code
      outside of the record or device support makes a connection to the
      field.

      The following values are for database common fields. They must
      *not* be used for record specific fields:

   -  ``SPC_SCAN`` – Scan related field.

   -  ``SPC_ALARMACK`` – Alarm acknowledgment field.

   -  ``SPC_AS`` – Access security field.

      The following values are deprecated, use ``SPC_MOD`` instead:

   -  An integer value greater than 103.

   -  ``SPC_RESET`` – a reset field is being modified.

   -  ``SPC_LINCONV`` – A linear conversion field is being modified.

   -  ``SPC_CALC`` – A calc field is being modified.

pp_value
   Should a passive record be processed when Channel Access writes to
   this field? The allowed values are:

   -  ``FALSE`` (default)

   -  ``TRUE``

interest_level
   An interest level for the ``dbpr`` command.

base
   For integer type fields, the default base. The legal values are:

   -  ``DECIMAL`` (Default)

   -  ``HEX``

size_value
   The number of characters for a ``DBF_STRING`` field.

extra_info
   For ``DBF_NOACCESS`` fields, this is the C language definition for
   the field. The definition must end with the fieldname in lower case.

%C_declaration
   A percent sign ``%`` inside the record body introduces a line of code
   that is to be included in the generated C header file.

.. _example-1:

Example
^^^^^^^

The following is the definition of the event record type:

::

   recordtype(event) {
       include "dbCommon.dbd" 
       field(VAL,DBF_STRING) {
           prompt("Event Name To Post")
           promptgroup("40 - Input")
           special(SPC_MOD)
           asl(ASL0)
           size(40)
       }
       field(EPVT, DBF_NOACCESS) {
           prompt("Event private")
           special(SPC_NOMOD)
           interest(4)
           extra("EVENTPVT epvt")
       }
       field(INP,DBF_INLINK) {
           prompt("Input Specification")
           promptgroup("40 - Input")
           interest(1)
       }
       field(SIOL,DBF_INLINK) {
           prompt("Sim Input Specifctn")
           promptgroup("90 - Simulate")
           interest(1)
       }
       field(SVAL,DBF_STRING) {
           prompt("Simulation Value")
           size(40)
       }
       field(SIML,DBF_INLINK) {
           prompt("Sim Mode Location")
           promptgroup("90 - Simulate")
           interest(1)
       }
       field(SIMM,DBF_MENU) {
           prompt("Simulation Mode")
           interest(1)
           menu(menuYesNo)
       }
       field(SIMS,DBF_MENU) {
           prompt("Sim mode Alarm Svrty")
           promptgroup("90 - Simulate")
           interest(2)
           menu(menuAlarmSevr)
       }
   }

``device`` – Device Support Declaration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _format-4:

Format
^^^^^^

::

   device(record_type, link_type, dset_name, "choice_string")

.. _definitions-2:

Definitions
^^^^^^^^^^^

record_type
   Record type. The combination of ``record_type`` and ``choice_string``
   must be unique. If the same combination appears more than once, only
   the first definition is used.

link_type
   Link type. This must be one of the following:

   -  ``CONSTANT``

   -  ``PV_LINK``

   -  ``VME_IO``

   -  ``CAMAC_IO``

   -  ``AB_IO``

   -  ``GPIB_IO``

   -  ``BITBUS_IO``

   -  ``INST_IO``

   -  ``BBGPIB_IO``

   -  ``RF_IO``

   -  ``VXI_IO``

dset_name
   The name of the device support entry table for this device support.

choice_string
   The ``DTYP`` choice string for this device support. A
   ``choice_string`` value may be reused for different record types, but
   must be unique for each specific record type.

Examples
^^^^^^^^

::

   device(ai,CONSTANT,devAiSoft,"Soft Channel")
   device(ai,VME_IO,devAiXy566Se,"XYCOM-566 SE Scanned")

``driver`` – Driver Declaration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _format-5:

Format
^^^^^^

::

   driver(drvet_name)

.. _definitions-3:

Definitions
^^^^^^^^^^^

drvet_name
   If duplicates are defined, only the first is used.

.. _examples-1:

Examples
^^^^^^^^

::

   driver(drvVxi)
   driver(drvXy210)

``registrar`` – Registrar Declaration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _format-6:

Format
^^^^^^

::

   registrar(function_name)

.. _definitions-4:

Definitions
^^^^^^^^^^^

function_name
   The name of an C function that accepts no arguments, returns ``void``
   and has been marked in its source file with an
   ``epicsExportRegistrar`` declaration, e.g.

.. code:: c

   static void myRegistrar(void);
   epicsExportRegistrar(myRegistrar);

This can be used to register functions for use by subroutine records or
that can be invoked from iocsh. The example application described in
Section `[Example IOC Application] <#Example IOC Application>`__,
“Example IOC Application” gives an example of how to register functions
for subroutine records.

.. _example-2:

Example
^^^^^^^

::

   registrar(myRegistrar)

.. _dbd-variable:

``variable`` – Variable Declaration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _format-7:

Format
^^^^^^

::

   variable(variable_name[, type])

.. _definitions-5:

Definitions
^^^^^^^^^^^

variable_name
   The name of a C variable which has been marked in its source file
   with an ``epicsExportAddress`` declaration.

type
   The C variable’s type. If not present, ``int`` is assumed. Currently
   only ``int`` and ``double`` variables are supported.

This registers a diagnostic/configuration variable for device or driver
support or a subroutine record subroutine. This variable can be read and
set with the iocsh ``var`` command (see Section
`[Utility Commands] <#Utility Commands>`__. The example application
described in Section
`[Example IOC Application] <#Example IOC Application>`__ shows how to
register a debug variable for use in a subroutine record.

.. _example-3:

Example
^^^^^^^

In an application C source file:

.. code:: c

   #include <epicsExport.h>

   static double myParameter;
   epicsExportAddress(double, myParameter);

In an application database definition file:

::

   variable(myParameter, double)

``function`` – Function Declaration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _format-8:

Format
^^^^^^

::

   function(function_name)

.. _definitions-6:

Definitions
^^^^^^^^^^^

function_name
   The name of a C function which has been exported from its source file
   with an ``epicsRegisterFunction`` declaration.

This registers a function so that it can be found in the function
registry for use by record types such as sub or aSub which refer to the
function by name. The example application described in Section
`[Example IOC Application] <#Example IOC Application>`__ shows how to
register functions for a subroutine record.

.. _example-4:

Example
^^^^^^^

In an application C source file:

.. code:: c

   #include <registryFunction.h>
   #include <epicsExport.h>

   static long myFunction(void *argp) {
       /* my code ... */
   }
   epicsRegisterFunction(myFunction);

In an application database definition file:

::

   function(myFunction)

``breaktable`` – Breakpoint Table
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _format-9:

Format
^^^^^^

::

   breaktable(name) {
       raw_value eng_value
       ...
   }

.. _definitions-7:

Definitions
^^^^^^^^^^^

name
   Name, which must be alpha-numeric, of the breakpoint table. If
   duplicates are specified the first is used.

raw_value
   The raw value, i.e. the actual ADC value associated with the
   beginning of the interval.

eng_value
   The engineering value associated with the beginning of the interval.

.. _example-5:

Example
^^^^^^^

::

   breaktable(typeJdegC) {
       0.000000 0.000000
       365.023224 67.000000
       1000.046448 178.000000
       3007.255859 524.000000
       3543.383789 613.000000
       4042.988281 692.000000
       4101.488281 701.000000
   }

``record`` – Record Instance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _format-10:

Format
^^^^^^

::

   record(record_type, record_name) {
       alias(alias_name)
       field(field_name, "field_value")
       info(info_name, "info_value")
       ...
   }
   alias(record_name, alias_name)

.. _definitions-8:

Definitions
^^^^^^^^^^^

record_type
   The record type, or ``"*"`` and ``"#"`` (see discussion under
   record_name below).

record_name
   The record name. This must be composed out of only the following
   characters:

   ::

      a-z A-Z 0-9 _ - + : [ ] < > ;

   NOTE: If macro substitutions are used the name must be quoted.

   Duplicate definitions are normally allowed for a record as long as
   the record type is the same. The last value given for each field is
   the value used. If the duplicate definitions are being used and the
   record has already been loaded, subsequent definitions may use
   ``"*"`` in place of the record type in the record instance.

   Previously defined record can be removed from the database using
   ``"#"`` in place of the record type in the record instance. This
   is useful when previously loaded records are not required or desired.

   The variable ``dbRecordsOnceOnly`` can be set to any non-zero value
   using the iocsh ``var`` command to make loading duplicate record
   definitions into the IOC illegal.

alias_name
   An alternate name for the record, following the same rules as the
   record name.

field_name
   A field name.

field_value
   A value for the named field, appropriate for its particular field
   type. When given inside double quotes the field value string may
   contain escaped characters which will be translated appropriately
   when loading the database. See section
   `1.3.5 <#subsec:Escape Sequences>`__ for the list of escaped
   characters supported. Permitted values for the various field types
   are as follows:

   -  | ``DBF_STRING``
      | Any ASCII string. If it exceeds the field length, it will be
        truncated.

   -  | ``DBF_CHAR``, ``DBF_UCHAR``, ``DBF_SHORT``, ``DBF_USHORT``,
        ``DBF_LONG``, ``DBF_ULONG``
      | A string that represents a valid integer. The standard C
        conventions are applied, i.e. a leading 0 means the value is
        given in octal and a leading 0x means that value is given in
        hex.

   -  | ``DBF_FLOAT``, ``DBF_DOUBLE``
      | The string must represent a valid floating point number.
        Infinities or NaN are also allowed.

   -  | ``DBF_MENU``
      | The string must be one of the valid choices for the associated
        menu.

   -  | ``DBF_DEVICE``
      | The string must be one of the valid device choice strings.

   -  | ``DBF_INLINK``, ``DBF_OUTLINK``, ``DBF_FWDLINK``
      | NOTES:

      -  If the field name is ``INP`` or ``OUT`` then this field is
         associated with ``DTYP``, and the permitted values are
         determined by the link type of the device support selected by
         the current ``DTYP`` choice string. Other ``DBF_INLINK`` and
         ``DBF_OUTLINK`` fields must be either ``CONSTANT`` or
         ``PV_LINK``\ s.

      -  A device support that specifies a link type of ``CONSTANT`` can
         be given either a constant or a ``PV_LINK``.

      The allowed values for the field depend on the device support’s
      link type as follows:

      -  | ``CONSTANT``
         | A numeric literal, valid for the field type it is to be read
           into.

      -  | ``PV_LINK``
         | A value of the form:

         ::

            record.field process maximize

         ``record`` is the name of a record that exists in this or
         another IOC.

         The ``.field``, ``process``, and ``maximize`` parts are all
         optional.

         The default value for ``.field`` is ``.VAL``.

         ``process`` can have one of the following values:

         -  ``NPP`` – No Process Passive (Default)

         -  ``PP`` – Process Passive

         -  ``CA`` – Force link to be a channel access link

         -  ``CP`` – CA and process on monitor

         -  ``CPP`` – CA and process on monitor if record is passive

            NOTES:

            ``CP`` and ``CPP`` are valid only for ``DBF_INLINK`` fields.

            ``DBF_FWDLINK`` fields can use ``PP`` or ``CA``. If a
            ``DBF_FWDLINK`` is a channel access link it must reference
            the target record’s ``PROC`` field.

         ``maximize`` can have one of the following values:

         -  ``NMS`` – No Maximize Severity (Default)

         -  ``MS`` – Maximize Severity

         -  ``MSS`` – Maximize Severity and Status

         -  ``MSI`` – Maximize Severity if Invalid

      -  | ``VME_IO``
         | ``#Ccard Ssignal @parm``

         | ``card`` – the card number of associated hardware module
         | ``signal`` – signal on card
         | ``parm`` – An arbitrary character string of up to 31
           characters. This field is optional and is device specific.

      -  | ``CAMAC_IO``
         | ``#Bbranch Ccrate Nstation Asubaddress Ffunction @parm``

         ``branch``, ``crate``, ``station``, ``subaddress``, and
         ``function`` should be obvious to ``camac`` users.
         ``subaddress`` and ``function`` are optional (0 if not given).
         ``parm`` is also optional and is device specific (25 characters
         max).

      -  | ``AB_IO``
         | ``#Llink Aadapter Ccard Ssignal @parm``

         | ``link`` – Scanner, i.e. vme scanner number
         | ``adapter`` – Adapter. Allen Bradley also calls this rack
         | ``card`` – Card within Allen Bradley Chassis
         | ``signal`` – signal on card
         | ``parm`` – optional device-specific character string (27 char
           max)

      -  | ``GPIB_IO``
         | ``#Llink Aaddr @parm``

         | ``link`` – gpib link, i.e. interface
         | ``addr`` – GPIB address
         | ``parm`` – device-specific character string (31 char max)

      -  | ``BITBUS_IO``
         | ``#Llink Nnode Pport Ssignal @parm``

         | ``link`` – link, i.e. vme bitbus interface
         | ``node`` – bitbus node
         | ``port`` – port on the node
         | ``signal`` – signal on port
         | ``parm`` – device specific-character string (31 char max)

      -  ``INST_IO`` ``@parm``

         ``parm`` – Device dependent character string

      -  | ``BBGPIB_IO``
         | ``#Llink Bbbaddr Ggpibaddr @parm``

         | ``link`` – link, i.e. vme bitbus interface
         | ``bbadddr`` – bitbus address
         | ``gpibaddr`` – gpib address
         | ``parm`` – optional device-specific character string (31 char
           max)

      -  | ``RF_IO``
         | ``#Rcryo Mmicro Ddataset Eelement``

      -  | ``VXI_IO``
         | ``#Vframe Cslot Ssignal @parm`` (Dynamic addressing)
         | or
         | ``#Vla Signal @parm`` (Static Addressing)

         | ``frame`` – VXI frame number
         | ``slot`` – Slot within VXI frame
         | ``la`` – Logical Address
         | ``signal`` – Signal Number
         | ``parm`` – device specific character string(25 char max)

info_name
   The name of an Information Item related to this record. See section
   `1.5 <#Record Information Item>`__ below for more on Information
   Items.

info_value
   Any ASCII string. IOC applications using this information item may
   place additional restrictions on the contents of the string.

.. _examples-2:

Examples
^^^^^^^^

::

   record(ai,STS_AbAiMaS0) {
       field(SCAN,".1 second")
       field(DTYP,"AB-1771IFE-4to20MA")
       field(INP,"#L0 A2 C0 S0 F0 @")
       field(PREC,"4")
       field(LINR,"LINEAR")
       field(EGUF,"20")
       field(EGUL,"4")
       field(EGU,"MilliAmps")
       field(HOPR,"20")
       field(LOPR,"4")
   }
   record(ao,STS_AbAoMaC1S0) {
       field(DTYP,"AB-1771OFE")
       field(OUT,"#L0 A2 C1 S0 F0 @")
       field(LINR,"LINEAR")
       field(EGUF,"20")
       field(EGUL,"4")
       field(EGU,"MilliAmp")
       field(DRVH,"20")
       field(DRVL,"4")
       field(HOPR,"20")
       field(LOPR,"4")
       info(autosaveFields,"VAL")
   }
   record(bi,STS_AbDiA0C0S0) {
       field(SCAN,"I/O Intr")
       field(DTYP,"AB-Binary Input")
       field(INP,"#L0 A0 C0 S0 F0 @")
       field(ZNAM,"Off")
       field(ONAM,"On")
   }

.. _Record Information Item:

Record Information Item
-----------------------

Information items provide a way to attach named string values to
individual record instances that are loaded at the same time as the
record definition. They can be attached to any record without having to
modify the record type, and can be retrieved by programs running on the
IOC (they are not visible via Channel Access at all). Each item attached
to a single record must have a unique name by which it is addressed, and
database access provides routines to allow a record’s info items to be
scanned, searched for, retrieved and set. At runtime a ``void*`` pointer
can also be associated with each item, although only the string value
can be initialized from the record definition when the database is
loaded.

Record Attributes
-----------------

Each record type can have any number of record attributes. Each
attribute is a psuedo field that can be accessed via database and
channel access. Each attribute has a name that acts like a field name
but returns the same value for all instances of the record type. Two
attributes are generated automatically for each record type: ``RTYP``
and ``VERS``. The value for ``RTYP`` is the record type name. The
default value for ``VERS`` is “none specified”, which can be changed by
record support. Record support can call the following routine to create
new attributes or change existing attributes:

.. code:: c

   long dbPutAttribute(char *rtype, char *name, char *value);

The arguments are:

``rtype`` – The name of recordtype.

``name`` – The attribute name, i.e. the psuedo field name.

``value`` – The value assigned to the attribute.

Breakpoint Tables – Discussion
------------------------------

The menu ``menuConvert`` is used for field ``LINR`` of the ``ai`` and
``ao`` records. These records allow raw data to be converted to/from
engineering units via one of the following:

#. No Conversion.

#. Slope Conversion.

#. Linear Conversion.

#. Breakpoint table.

Other record types can also use this feature. The first choice specifies
no conversion; the second and third are both linear conversions, the
difference being that for Slope conversion the user specifies the
conversion slope and offset values directly, whereas for Linear
conversions these are calculated by the device support from the
requested Engineering Units range and the device support’s knowledge of
the hardware conversion range. The remaining choices are assumed to be
the names of breakpoint tables. If a breakpoint table is chosen, the
record support modules calls ``cvtRawToEngBpt`` or ``cvtEngToRawBpt``.
You can look at the ``ai`` and ``ao`` record support modules for
details.

If a user wants to add additional breakpoint tables, then the following
should be done:

-  Copy the ``menuConvert.dbd`` file from EPICS ``base/src/ioc/bpt``

-  Add definitions for new breakpoint tables to the end

-  Make sure modified ``menuConvert.dbd`` is loaded into the IOC instead
   of EPICS version.

It is only necessary to load a breakpoint file if a record instance
actually chooses it. It should also be mentioned that the Allen Bradley
IXE device support misuses the ``LINR`` field. If you use this module,
it is very important that you do not change any of the EPICS supplied
definitions in ``menuConvert.dbd``. Just add your definitions at the
end.

If a breakpoint table is chosen, then the corresponding breakpoint file
must be loaded into the IOC before ``iocInit`` is called.

Normally, it is desirable to directly create the breakpoint tables.
However, sometimes it is desirable to create a breakpoint table from a
table of raw values representing equally spaced engineering units. A
good example is the Thermocouple tables in the OMEGA Engineering, INC
Temperature Measurement Handbook. A tool ``makeBpt`` is provided to
convert such data to a breakpoint table.

The format for generating a breakpoint table from a data table of raw
values corresponding to equally spaced engineering values is:

::

   !comment line
   <header line>
   <data table>

The header line contains the following information:

Name
   An alphanumeric ascii string specifying the breakpoint table name

Low Value Eng
   Engineering Units Value for first breakpoint table entry

Low Value Raw
   Raw value for first breakpoint table entry

High Value Eng
   Engineering Units: Highest Value desired

High Value Raw
   Raw Value for High Value Eng

Error
   Allowed error (Engineering Units)

First Table
   Engineering units corresponding to first data table entry

Last Table
   Engineering units corresponding to last data table entry

Delta Table
   Change in engineering units per data table entry

An example definition is:

::

   "TypeKdegF" 32 0 1832 4095 1.0 -454 2500 1
   <data table>

The breakpoint table can be generated by executing

.. code:: sh

   makeBpt bptXXX.data

The input file must have the extension of data. The output filename is
the same as the input filename with the extension of ``.dbd``.

Another way to create the breakpoint table is to include the following
definition in a ``Makefile``:

.. code:: makefile

   BPTS += bptXXX.dbd

NOTE: This requires the naming convention that all data tables are of
the form ``bpt<name>.data`` and a breakpoint table ``bpt<name>.dbd``.

Menu and Record Type Include File Generation.
---------------------------------------------

Introduction
~~~~~~~~~~~~

Given a file containing menu definitions, the program ``dbdToMenuH.pl``
generates a C/C++ header file for use by code which needs those menus.
Given a file containing any combination of menu definitions and record
type definitions, the program ``dbdToRecordtypeH.pl`` generates a C/C++
header file for use by any code which needs those menus and record type.

EPICS Base uses the following conventions for managing menu and
recordtype definitions. Users generating local record types are
encouraged to follow these.

-  Each menu that is used by fields in database common (for example
   ``menuScan``) or is of global use (for example ``menuYesNo``) should
   be defined in its own file. The name of the file is the same as the
   menu name, with an extension of ``.dbd``. The name of the generated
   include file is the menu name, with an extension of ``.h``. Thus
   ``menuScan`` is defined in a file ``menuScan.dbd`` and the generated
   include file is named ``menuScan.h``

-  Each record type is defined in its own file. This file should also
   contain any menu definitions that are used only by that record type.
   Menus that are specific to one particular record type should use that
   record type name as a prefix to the menu name. The name of the file
   is the same as the record type, followed by ``Record.dbd``. The name
   of the generated include file is the same as the ``.dbd`` file but
   with an extension of ``.h``. Thus the record type ``ao`` is defined
   in a file ``aoRecord.dbd`` and the generated include file is named
   ``aoRecord.h``. Since ``aoRecord`` has a private menu called
   ``aoOIF``, the ``dbd`` file and the generated include file will have
   definitions for this menu. Thus for each record type, there are two
   source files (``xxxRecord.dbd`` and ``xxxRecord.c``) and one
   generated file (``xxxRecord.h``).

Note that developers don’t normally execute the ``dbdToMenuH.pl`` or
``dbdToRecordtypeH.pl`` programs manually. If the proper naming
conventions are used, it is only necessary to add definitions to the
appropriate ``Makefile``. Consult the chapter on the EPICS Build
Facility for details.

dbdToMenuH.pl
~~~~~~~~~~~~~

This tool is executed as follows:

.. code:: sh

   dbdToMenuH.pl [-D] [-I dir] [-o menu.h] menu.dbd [menu.h]

It reads in the input file ``menu.dbd`` and generates a C/C++ header
file containing enumerated type definitions for the menus found in the
input file.

Multiple ``-I`` options can be provided to specify directories that must
be searched when looking for included files. If no output filename is
specified with the ``-o menu.h`` option or as a final command-line
parameter, then the output filename will be constructed from the input
filename, replacing ``.dbd`` with ``.h``.

The ``-D`` option causes the program to output Makefile dependency
information for the output file to standard output, instead of actually
performing the functions describe above.

For example ``menuPriority.dbd``, which contains the definitions for
processing priority contains:

::

   menu(menuPriority) {
       choice(menuPriorityLOW,"LOW")
       choice(menuPriorityMEDIUM,"MEDIUM")
       choice(menuPriorityHIGH,"HIGH")
   }

The include file ``menuPriority.h`` that is generated contains:

.. code:: c

   /* menuPriority.h generated from menuPriority.dbd */

   #ifndef INC_menuPriority_H
   #define INC_menuPriority_H

   typedef enum {
       menuPriorityLOW                 /* LOW */,
       menuPriorityMEDIUM              /* MEDIUM */,
       menuPriorityHIGH                /* HIGH */,
       menuPriority_NUM_CHOICES
   } menuPriority;

   #endif /* INC_menuPriority_H */

Any code that needs the priority menu values should include this file
and make use of these definitions.

dbdToRecordtypeH.pl
~~~~~~~~~~~~~~~~~~~

This tool is executed as follows:

.. code:: sh

   dbdTorecordtypeH.pl [-D] [-I dir] [-o xRecord.h] xRecord.dbd [xRecord.h]

It reads in the input file ``xRecord.dhd`` and generates a C/C++ header
file which defines the in-memory structure of the given record type and
provides other associated information for the compiler. If the input
file contains any menu definitions, they will also be converted into
enumerated type definitions in the output file.

Multiple ``-I`` options can be provided to specify directories that must
be searched when looking for included files. If no output filename is
specified with the ``-o xRecord.h`` option or as a final command-line
parameter then the output filename will be constructed from the input
filename, replacing ``.dbd`` with ``.h``.

The ``-D`` option causes the program to output Makefile dependency
information for the output file to standard output, instead of actually
performing the functions describe above.

For example ``aoRecord.dbd``, which contains the definitions for the
analog output record contains:

::

   menu(aoOIF) {
       choice(aoOIF_Full,"Full")
       choice(aoOIF_Incremental,"Incremental")
   }
   recordtype(ao) {
       include "dbCommon.dbd" 
       field(VAL,DBF_DOUBLE) {
           prompt("Desired Output")
           promptgroup("50 - Output")
           asl(ASL0)
           pp(TRUE)
       }
       field(OVAL,DBF_DOUBLE) {
           prompt("Output Value")
       }
       ... many more field definitions
   }

The include file ``aoRecord.h`` that is generated contains:

.. code:: c

   /* aoRecord.h generated from aoRecord.dbd */

   #ifndef INC_aoRecord_H
   #define INC_aoRecord_H

   #include "epicsTypes.h"
   #include "link.h"
   #include "epicsMutex.h"
   #include "ellLib.h"
   #include "epicsTime.h"

   typedef enum {
       aoOIF_Full                      /* Full */,
       aoOIF_Incremental               /* Incremental */,
       aoOIF_NUM_CHOICES
   } aoOIF;

   typedef struct aoRecord {
       char                name[61];   /* Record Name */
       ... define remaining fields from database common
       epicsFloat64        val;        /* Desired Output */
       epicsFloat64        oval;       /* Output Value */
       ... define remaining record specific fields
   } aoRecord;

   typedef enum {
       aoRecordNAME = 0,
       aoRecordDESC = 1,
       ... indices for remaining fields in database common
       aoRecordVAL = 43,
       aoRecordOVAL = 44,
       ... indices for remaining record specific fields
   } aoFieldIndex;

   #ifdef GEN_SIZE_OFFSET

   #ifdef __cplusplus
   extern "C" {
   #endif
   #include <epicsExport.h>
   static int aoRecordSizeOffset(dbRecordType *prt)
   {
       aoRecord *prec = 0;
       prt->papFldDes[aoRecordNAME]->size = sizeof(prec->name);
       ... code to compute size for remaining fields
       prt->papFldDes[aoRecordNAME]->offset = (char *)&prec->name - (char *)prec;
       ... code to compute offset for remaining fields
       prt->rec_size = sizeof(*prec);
       return 0;
   }
   epicsExportRegistrar(aoRecordSizeOffset);

   #ifdef __cplusplus
   }
   #endif
   #endif /* GEN_SIZE_OFFSET */

   #endif /* INC_aoRecord_H */

The analog output record support module and all associated device
support modules should include this file. No other code should use it.

Let’s discuss the various parts of the file:

-  The ``enum`` generated from the menu definition should be used to
   provide values for the field associated with that menu.

-  The ``typedef struct`` defining the record are used by record support
   and device support to access the fields in an analog output record.

-  The next ``enum`` defines an index number for each field within the
   record. This is useful for the record support routines that are
   passed a pointer to a ``DBADDR`` structure. They can have code like
   the following:

.. code:: c

   switch (dbGetFieldIndex(pdbAddr)) {
       case aoRecordVAL :
           ...
           break;
       case aoRecordXXX:
           ...
           break;
       default:
           ...
   }

The generated routine ``aoRecordSizeOffset`` is executed when the record
type gets registered with an IOC. The routine is compiled with the
record type code, and is marked static so it will not be visible outside
of that file. The associate record support source code MUST include the
generated header file only after defining the ``GEN_SIZE_OFFSET`` macro
like this:

.. code:: c

   #define GEN_SIZE_OFFSET
   #include "aoRecord.h"
   #undef GEN_SIZE_OFFSET

This convention ensures that the routine is defined exactly once. The
``epicsExportRegistrar`` statement ensures that the record registration
code can find and call the routine.

dbdExpand.pl
------------

.. code:: sh

   dbdExpand.pl [-D] [-I dir] [-S mac=sub] [-o out.dbd] in.dbd ...

This program reads and combines the database definition from all the
input files, then writes a single output file containing all information
from the input files. The output content differs from the input in that
comment lines are removed, and all defined macros and include files are
expanded. Unlike the previous ``dbExpand`` program, this program does
not understand database instances and cannot be used with ``.db`` or
``.vdb`` files.

Multiple ``-I`` options can be provided to specify directories that must
be searched when looking for included files. Multiple ``-S`` options are
allowed for macro substitution, or multiple macros can be specified
within a single option. If no output filename is specified with the
``-o out.dbd`` option then the output will go to stdout.

The ``-D`` option causes the program to output Makefile dependency
information for the output file to standard output, instead of actually
performing the functions describe above.

dbLoadDatabase
--------------

::

   dbLoadDatabase(char *dbdfile, char *path, char *substitutions)

This IOC command loads a database file which may contain any of the
Database Definitions described in this chapter. The ``dbdfile`` string
may contain environment variable macros of the form ``${MOTOR}`` which
will be expanded before the file is opened. Both the ``path`` and
``substitutions`` parameters can be null or empty, and are usually
ommitted. Note that ``dbLoadDatabase`` should only used to load Database
Definition (``.dbd``) files, although it is currently possible to use it
for loading Record Instance (``.db``) files as well.

As each line of the file is read, the substitutions specified in
``substitutions`` are performed. Substitutions are specified as follows:

::

   "var1=sub1,var2=sub3,..."

Variables are used in the file with the syntax ``$(var)`` or ``${var}``.
If the substitution string

::

   "a=1,b=2,c=\"this is a test\""

were used, any variables ``$(a)``, ``$(b)``, ``$(c)`` in the database
file would have the appropriate values substituted during parsing.

dbLoadRecords
-------------

::

   dbLoadRecords(char* dbfile, char* substitutions)

This IOC command loads a file containing record instances, record
aliases and/or breakpoint tables. The ``dbfile`` string may contain
environment variable macros of the form ``${MOTOR}`` which will be
expanded before the file is opened. The ``substitutions`` parameter can
be null or empty, and is often ommitted. Note that ``dbLoadRecords``
should only used to load Record Instance (``.db``) files, although it is
currently possible to use it for loading Database Definition (``.dbd``)
files as well.

.. _example-6:

Example
~~~~~~~

For example, let the file ``test.db`` contain:

::

   record(ai, "$(pre)testrec1")
   record(ai, "$(pre)testrec2")
   record(stringout, "$(pre)testrec3") {
       field(VAL, "$(STR)")
       field(SCAN, "$(SCAN)")
   }

Then issuing the command:

::

   dbLoadRecords("test.db", "pre=TEST,STR=test,SCAN=Passive")

gives the same results as loading:

::

   record(ai, "TESTtestrec1")
   record(ai, "TESTtestrec2")
   record(stringout, "TESTtestrec3") {
       field(VAL, "test")
       field(SCAN, "Passive")
   }

dbLoadTemplate
--------------

::

   dbLoadTemplate(char *subfile, char *substitutions)

This IOC command reads a template substitutions file which provides
instructions for loading database instance files and gives values for
the ``$(xxx)`` macros they may contain. This command performs those
substitutions while loading the database instances requested.

The ``subfile`` parameter gives the name of the template substitution
file to be used. The optional ``substitutions`` parameter may contain
additional global macro values, which can be overridden by values given
within the substitution file.

The MSI program can be used to expand templates at build-time instead of
using this command at run-time; both understand the same substitution
file syntax.

Template File Syntax
~~~~~~~~~~~~~~~~~~~~

The template substitution file syntax is described in the following
Extended Backus-Naur Form grammar:

::

   substitution-file ::= ( global-defs | template-subs )+

   global-defs ::= 'global' '{' variable-defs? '}'

   template-subs ::= template-filename '{' subs? '}'
   template-filename ::= 'file' file-name
   subs ::= pattern-subs | variable-subs

   pattern-subs ::= 'pattern' '{' pattern-names? '}' pattern-defs?
   pattern-names ::= ( variable-name ','? )+
   pattern-defs ::= ( global-defs | ( '{' pattern-values? '}' ) )+
   pattern-values ::= ( value ','? )+

   variable-subs ::= ( global-defs | ( '{' variable-defs? '}' ) )+
   variable-defs ::= ( variable-def ','? )+
   variable-def ::= variable-name '=' value

   variable-name ::= variable-name-start variable-name-char*
   file-name ::= file-name-char+ | double-quoted-str | single-quoted-str
   value ::= value-char+ | double-quoted-str | single-quoted-str

   double-quoted-str ::= '"' (double-quoted-char | escaped-char)* '"'
   single-quoted-str ::= "'" (single-quoted-char | escaped-char)* "'"
   double-quoted-char ::= [^"\]
   single-quoted-char ::= [^'\]
   escaped-char ::= '\' .

   value-char ::= [a-zA-Z0-9_+:;./\<>[] | '-' | ']'
   variable-name-start ::= [a-zA-Z_]
   variable-name-char ::= [a-zA-Z0-9_]
   file-name-char ::= [a-zA-Z0-9_+:;./\] | '-'

Note that the current implementation may accept a wider range of
characters for the last three definitions than those listed here, but
future releases may restrict the characters to those given above.

Any record instance file names must appear inside quotation marks if the
name contains any environment variable macros of the form
``${ENV_VAR_NAME}``, which will be expanded before the named file is
opened.

Template File Formats
~~~~~~~~~~~~~~~~~~~~~

Two different template formats are supported by the syntax rules given
above. The format is either:

::

   file name.template {
       { var1=sub1_for_set1, var2=sub2_for_set1, var3=sub3_for_set1, ... }
       { var1=sub1_for_set2, var2=sub2_for_set2, var3=sub3_for_set2, ... }
       { var1=sub1_for_set3, var2=sub2_for_set3, var3=sub3_for_set3, ... }
   }

or:

::

   file name.template {
   pattern { var1, var2, var3, ... }
       { sub1_for_set1, sub2_for_set1, sub3_for_set1, ... }
       { sub1_for_set2, sub2_for_set2, sub3_for_set2, ... }
       { sub1_for_set3, sub2_for_set3, sub3_for_set3, ... }
   }

The first line (``file name.template``) specifies the record instance
input file. The file name may appear inside double quotation marks;
these are required if the name contains any characters that are not in
the following set, or if it contains environment variable macros of the
form ``${VAR_NAME}`` which must be expanded to generate the file name:

::

   a-z A-Z 0-9 _ + - . / \ : ; [ ] < >

Each set of definitions enclosed in ``{}`` is variable substitution for
the input file. The input file has each set applied to it to produce one
composite file with all the completed substitutions in it. Version 1
should be obvious. In version 2, the variables are listed in the
``pattern{}`` line, which must precede the braced substitution lines.
The braced substitution lines contains sets which match up with the
``pattern{}`` line.

.. _example-7:

Example
~~~~~~~

Two simple template file examples are shown below. The examples specify
the same substitutions to perform: ``this=sub1`` and ``that=sub2`` for a
first set, and ``this=sub3`` and ``that=sub4`` for a second set.

::

   file test.template {
       { this=sub1,that=sub2 }
       { this=sub3,that=sub4 }
   }

   file test.template {
       pattern{this,that}
       {sub1,sub2}
       {sub3,sub4 }
   }

Assume that the file ``test.template`` contains:

::

   record(ai,"$(this)record") {
       field(DESC,"this = $(this)")
   }
   record(ai,"$(that)record") {
       field(DESC,"this = $(that)")
   }

Using ``dbLoadTemplate`` with either input is the same as defining the
records:

::

   record(ai,"sub1record") {
       field(DESC,"this = sub1")
   }
   record(ai,"sub2record") {
       field(DESC,"this = sub2")
   }

   record(ai,"sub3record") {
       field(DESC,"this = sub3")
   }
   record(ai,"sub4record") {
       field(DESC,"this = sub4")
   }
