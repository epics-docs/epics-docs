EPICS 7, pvAccess and pvData
============================

:audience:`developer, advanced`


pvAccess, pvData and other related modules have been introduced into EPICS
to add support for structured data. Let us look into the
reasons, and also at some use cases for the capabilities to handle
structured data.

EPICS has its roots in process control. In typical process control
applications, process variables are scalar data items. Transporting the
process variables efficiently has priority over
handling sophisticated constructs. Only a limited set of data is
sufficient to describe the process data: timestamp, alarm status,
display information and engineering units. This kind of simple
interfaces make it possible to build general-purpose tools for
manipulating the data, and also enables the low-level units to
interoperate without big overhead or having to customize the
applications whenever a new structure is introduced.

However, in more complex applications like data acquisition in
scientific experiments, having only scalar values and limited
metadata becomes a limiting factor. For instance, when (camera) images
are transported over the network, more complex metadata is required to
interpret and display the image;
what are the dimensions of the picture in pixels, how many data bits are
required to present a single pixel, what is the encoding, and many
other parameters.

Even further, when it is required to represent more abstract entities,
single values or primitive waveforms are not suitable for these tasks.

It is possible work around these limitations to some extent. One can
define several process variables and combine these in a higher-level
application. This has been done in many packages, for instance in
accelerator physics applications like beam steering, by building an
abstraction layer on top the simple process variables.

While workarounds are possible, they have many drawbacks. To begin with,
it is very difficult to ensure interoperability of applications that
have been built in this way. The logic gets dispersed in various layers
of the software stack and applications cannot take advantage of what has
been implemented in other parts of the system. For instance, an archiver
cannot store data entities that have been defined in a physics
application, nor can a general-purpose GUI client display them.

Also, sharing of data is difficult, even between colleagues in the same
organization or project, not even to talk about making the data useful
outside of the organization.

This situation leads to limited functionality and also every project has
to build a set of site-specific applications from scratch.

Overview of pvData implementation
=================================

pvData (Process Variable Data) is a part of the EPICS (7 and above) core
software. It is a run-time type system with serialization and
introspection for handling of structured data. It implements the data
management system to which the other related components like pvAccess,
pvDatabase, etc. interface.

pvData is conceptually somewhat similar to `Google Protocol
Buffers <http://code.google.com/apis/protocolbuffers/>`__ (PB, see [1]),
however an important difference is that pvData type and structure information
is exchanged run-time, while PB depends on precompiled stubs on each side.

pvData defines and implements an efficient way to store, access, and
communicate memory resident data structures. The following attributes
describe the design goals of pvData:

-  efficiency

   -  Small memory footprint, low CPU overhead, and concise code base.

-  simple but powerful structure concept

   -  pvData has four types of data **fields**: scalar, scalarArray,
      structure, and structureArray. A **scalar** can be one of the
      following scalar types: Boolean, Byte, Short, Int, Long,
      U(nsigned) Byte, Unsigned Short, Unsigned Int, Unsigned Long,
      Float, Double, and String. A **scalarArray** is a one-dimensional
      array with the element type being any of the scalar types. A
      **structure** is an ordered set of fields where each field has a
      name and type. A **structureArray** is an array of similar
      structures. Since a field can be a structure, complex structures
      can be created.

-  structure and data storage separation

   -  pvData defines separate introspection and data interfaces. The
      introspection interfaces provide access to immutable objects,
      which allows introspection instances to be freely shared. The
      introspection interface for a process variable can be accessed
      without requiring access to the data.

-  data transfer optimization

   -  The separation of introspection and data interfaces allows for
      efficient network data transfer. When a client connects to a PV,
      introspection information is passed from server to client so that
      each side can create a data instance. The payload data is
      transferred between these instances. The data that is transferred
      over the network does not have to be self-describing since each
      side has the introspection information.

-  data access standardization

   -  Client code can access pvData via the introspection and data
      interfaces. For "well known" data, e.g. image data, specialized
      interfaces can be provided without requiring any changes to the
      core software. There exists a separate definition of standard data
      types, called Normative Types. For example, a normative type for
      image data is called NTNDArray.

-  memory resident

   -  pvData only defines memory resident data.

pvData is intended for use by pvAccess client software, as an interface
between client and network, or network and server, as well as an
interface between server and IOC database. Since it is a system-agnostic
interface to data, it could also be used by other systems and is easy to
convert between different storage formats. A high-level physics
application can manipulate data as pvData structures, the data can made
available to network clients by a pvAccess server like *qsrv* that is
included in an EPICS IOC to serve process variables, or some
special-purpose server, serving for example calibration data from a
suitable data storage like a database.

PVData structure definition
===========================

This section describes pvData structures in a metalanguage. The
metalanguage is used for documentation; there are no parsers or a strict
formal description. The metalanguage is used to describe both
introspection interfaces and data interfaces.

Definitions
~~~~~~~~~~~

PVData supports structured data. All data appears via top-level
structures. A structure has an ordered set of fields where each field is
defined as follows:

**type** fieldName *value* // comment

where *value* is present for data objects and // indicates that the the
rest of the line is a comment.

**type** is one of **scalar**, **scalarArray**, **structure**, or
**structureArray**. These types are defined in more details in the
following paragraphs.

scalar
~~~~~~

A scalar field can be of any of the following primitive types:

   **boolean**

   Has the value “true” or “false”.

   **byte**

   An 8 bit signed integer.

   **short**

   An 16 bit signed integer.

   **int**

   An 32 bit signed integer.

   **long**

   An 64 bit signed integer.

   **ubyte**

   An 8 bit unsigned integer.

   **ushort**

   An 16 bit unsigned integer.

   **uint**

   An 32 bit unsigned integer.

   **ulong**

   An 64 bit unsigned integer.

   **float**

   A IEEE float.

   **double**

   A IEEE double.

   **string**

   An immutable string.

scalarArray
~~~~~~~~~~~

A scalarArray field is an array of any of the scalar types.

   **boolean[]**

   **byte[]**

   **short[]**

   **int[]**

   **long[]**

   **ubyte[]**

   **ushort[]**

   **uint[]**

   **ulong[]**

   **float[]**

   **double[]**

   **string[]**

structure
~~~~~~~~~

A structure field has the definition:

**structure** *fieldName*

*fieldDef*

...

or

**xxx_t** *fieldName*

// if data object then following appears

*fieldDef*

...

For structure fieldName each *fieldDef* must have a unique fieldName
within the structure.

For "xxx_t fieldName", xxx_t must be a previously defined structure of
the form:

**structure** *xxx_t* ...

structureArray
~~~~~~~~~~~~~~

A structureArray field has the definition:

**structure[]** *fieldName* structureDef ...

or

**xxx_t[] fieldName**

Thus a structure array is an array where each element is a structure but
all elements of the array have the same structure and also the same
introspection interface. For introspection the structureDef appears once
without any data values.

The above is used to describe introspection objects. Data objects are
described in a similar way but each scalar field and each array field
has data values. The definition of the data values depends on the type.
For scalars the data value is whatever is valid for the type.

**boolean**

The value must be true or false

**byte,...ulong**

Any valid integer or hex value, e.g. 3 and 0x0ff are valid values

**float,double**

Any valid integer or real e.g. 3, 3.0, and 3e0 are valid values

**string**

The value can be an alphanumeric value or any set of characters enclosed
in "" Within quotes a quote is expressed as \\" Examples are aValue "a
value" "a\" xxx" are valid values.

For scalar arrays the syntax is:

= [value,...,value]

where each value is a valid scalar data value depending on the type.
Thus it is a comma separated set of values enclosed in square brackets:
[] White space is permitted surrounding each comma.

**Examples**

Having defined the following base structure:

.. code::

  structure  timeStamp_t
    long secondsPastEpoch
    int nanoSeconds
    int userTag

it can be used to define further structures:

.. code::

  structure  scalarDoubleExample // introspection object
    double value
    timeStamp_t timeStamp

which would correspond to:

.. code::

  structure scalarDoubleExample
    double value
    structure timeStamp
      long secondsPastEpoch
      int nanoSeconds
      int userTag

The following corresponding **data** object can then be defined:

.. code::

  structure scalarDoubleExample // data object
    double value 1.0
    timeStamp_t timeStamp
      long secondsPastEpoch 1531389047
      int nanoSeconds 247000000

Also, if the following interface is defined:

.. code::

  structure point_t
    double x
    double y

the following uses become possible (among others):

.. code::

  structure lineExample
    point_t begin
    point_t end

  structure pointArrayExample
    point_t[] points

filling in the details, they look like:

.. code::

  structure lineExample
    structure begin
      double x
      double y
    structure end
      double x
      double y

and

.. code::

  structure pointArrayExample
    structure[] points
      structure point
        double x
        double y

And the corresponding **data** objects could look like this:

.. code::

  structure lineExample
    point_t begin
      double x 0.0
      double y 0.0
    point_t end
      double x 10.0
      double y 10.0

  structure pointArrayExample
    point_t[] value
      structure point
        double x 0.0
        double y 0.0
      structure point
        double x 10.0
        double y 10.0

References:

1. Google Protocol Buffers: http://code.google.com/apis/protocolbuffers/

2. Normative Types Specification
