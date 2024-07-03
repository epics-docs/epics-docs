# pvAccess Protocol Specification

[Back to main](protocol)

## Data Encoding

1.  [Sizes](#sizes)
2.  [User Data](#user-data)
    - [Basic Types](#basic-types)
    - [Arrays](#arrays)
    - [Strings](#strings)
    - [Bounded Strings](#bounded-strings)
    - [Structures](#structures)
    - [Arrays of Structures](#variable-size-structure-arrays)
    - [Unions](#unions)
    - [Variant Unions](#variant-unions)
    - [Encoding Example](#encoding-example)
3.  [Meta Data](#meta-data)
    - [BitSets](#bitsets)
        - [Partial Structure Serialization](#partial-structure-serialization)
    - [Status](#status)
    - [Introspection Data](#introspection-data)
        - [Example \#1](#example-1)
        - [Example \#2](#example-2)



Encoding does not align primitive types on word boundaries.

For connection-oriented communication (TCP/IP), the server MUST notify
the client what byte order to use. Each message contains an endianness
flag in order to allow all the intermediates to forward data without
requiring it to be unmarshaled (so that the intermediates can forward
requests by simply copying blocks of binary data) and in order not to
require a specific byte order for connection-less protocols (UDP/IP).

Deviation: Current peers ignore the header endian bit for messages received over TCP.
The `SET_ENDIANESS` control message is used instead.  Similarly w/ protocol version.

### Sizes

Many of the types involved in the data encoding, as well as several
protocol message components, have an associated size (or "count"). Size
values MUST always be a non-negative integer and encoded as follows:

1.  The unsigned 8-bit integer 255 indicates "null", no data.
2.  If the number of elements is less than 254, the size MUST be encoded
    as a single byte containing an unsigned 8-bit integer indicating the
    number of elements
3.  If the number of elements is less than 2^31-1, then the size MUST be
    encoded as an unsigned 8-bit integer with value 254, followed by a
    positive signed 32-bit integer indicating the number of elements
4.  Values greater than or equal to 2^31-1 are currently not implemented.
    If they were, their size MUST be encoded as an unsigned 8-bit integer with value
    254, followed by a positive signed 32-bit integer with value 2^31-1,
    followed by a positive signed 64-bit integer indicating the number
    of elements. This implies a maximum size of 2^63-1.

### User Data

#### Basic Types

The basic types MUST be encoded as shown in the Table 1. Signed integer
types (byte, short, int, long) MUST be represented as two’s complement
numbers. Floating point types (float, double) MUST use the IEEE-754
standard formats
[bib:ieee754wiki](#bib:ieee754wiki).

|    Type | Encoding                                                          |
| ------: | ----------------------------------------------------------------- |
| boolean | A single byte with value non-zero value for true, zero for false. |
|    byte | Signed 8-bit integer.                                             |
|   ubyte | Unsigned 8-bit integer.                                           |
|   short | Signed 16-bit integer.                                            |
|  ushort | Unsigned 16-bit integer.                                          |
|     int | Signed 32-bit integer.                                            |
|    uint | Unsigned 32-bit integer.                                          |
|    long | Signed 64-bit integer.                                            |
|   ulong | Unsigned 64-bit integer.                                          |
|   float | 32-bit float (IEEE-754 single-precision float).                   |
|  double | 64-bit float (IEEE-754 double-precision float).                   |

Encoding for basic types.

*Note on boolean encoding: a receiver MUST NOT assume that a boolean
value of true is represented by any special non-zero number, nor that
the same sender consistently uses the same number.*

#### Arrays

##### Variable-size Arrays

Variable-size arrays MUST be encoded as a size representing the number
of elements in the array, followed by the elements encoded as specified
for their type (as specified in these sections).

##### Bounded-size Arrays

Bounded-size arrays MUST be encoded as a size representing the number of
elements in the array, followed by the elements encoded as specified for
their type (as specified in these sections). The size MUST be less then
or equal to the array's declared bound.

##### Fixed-size Arrays

Fixed-size arrays MUST be encoded as elements encoded as specified for
their type (as specified in these sections). The number of elements
encoded MUST equal to the array's fixed size.

#### Strings

Strings are encoded as arrays of bytes. The actual content (the bytes in
the array) MUST be a valid [UTF-8](http://tools.ietf.org/html/rfc3629)
encoded string.

Particularly, this means that strings MUST be encoded as a size,
followed by the string contents in a UTF-8 format as bytes. Size gives
the number of bytes that follow it and not the number of UTF-8
characters. UTF-8 multi-byte characters MUST NOT be broken. An empty
string MUST be encoded with a size of zero.

Implementations that internally use a zero byte or a zero character to
indicate end-of-string SHOULD NOT include a terminating zero byte in the
pvAccess string encoding. 'null' strings are not supported.

#### Bounded Strings

Same as strings, just that size MUST be less than or equal to the
string's bound.

#### Structures

Structures MUST be encoded by appending the data of all comprising
fields in the order in which the fields have been defined. A structure
can contain a structure and an union (see below) for its field.

#### Variable-size Structure Arrays

An array of structures is encoded as a size representing the number
of elements in the array. For each array element, the encoding then
consists of a boolean that indicates if the array element is present or null.
A byte 0x00 indicates that the array element is null.
A byte 0x01 indicates that the array is present, followed by the structure data,
i.e. the encoding for each field of the structure.

Example array of structures, three elements, middle element null,
where each structure contains two short numbers:

    [ { 0x1111, 0x2222 }, null, { 0x3333, 0x4444 } ]

would be encoded as

    03 01 11 11 22 22 00 01 33 33 44 44

#### Unions

Unions MUST be encoded as a selector value (encoded as a size), followed
by the selected union member data. The selector chooses one member of a
union as specified in the union introspection data, so must be a value
in the range 0..N-1 where N is the number of union members. A union can
contain a structure and a union for its field.

#### Variant Unions

Variant Unions are open ended union type, also known as *any* type.
Variant Unions MUST be encoded as a introspection data (*Field*)
description of the encoded value, followed by the encoded value itself.

#### Encoding Example

Given the following structure:

    structure 
        byte[] value [1,2,3]
        byte<16> boundedSizeArray [4,5,6,7,8]
        byte[4] fixedSizeArray [9,10,11,12]
        structure timeStamp
            long secondsPastEpoch 0x1122334455667788
            int nanoSeconds 0xAABBCCDD
            int userTag 0xEEEEEEEE
        structure alarm
            int severity 0x11111111
            int status 0x22222222
            string message Allo, Allo!
        union valueUnion
            int  0x33333333
        any variantUnion
            string  String inside variant union.

The above would be serialized as illustrated below (when using
big-endian byte order, *valueUnion* selector with value 1 is selected):

    Hexdump [Serialized structure] size = 85
    03 01 02 03  05 04 05 06  07 08 09 0A  0B 0C 11 22  .... .... .... ..." 
    33 44 55 66  77 88 AA BB  CC DD EE EE  EE EE 11 11  3DUf w... .... .... 
    11 11 22 22  22 22 0B 41  6C 6C 6F 2C  20 41 6C 6C  .."" "".A llo,  All 
    6F 21 01 33  33 33 33 60  1C 53 74 72  69 6E 67 20  o!.3 333` .Str ing  
    69 6E 73 69  64 65 20 76  61 72 69 61  6E 74 20 75  insi de v aria nt u 
    6E 69 6F 6E  2E                                     nion .

### Meta Data

#### BitSets

BitSet is a data type that represents a finite sequence of bits.

BitSet is encoded as sequence of ulong and ubyte.
Zero or more ulong, and between zero and seven trailing ubytes.
Bits are serialized in groups of eight in ascending order (LSB to MSB).
Serialization SHOULD be optimized to avoid sending trailing zeros.

TODO: needs LE encoding examples.

Examples of BitSet serialization:

    Hexdump [{}] size = 1
    00                                                 .
    
    Hexdump [{0}] size = 2
    01 01                                              ..
    
    Hexdump [{1}] size = 2
    01 02                                              ..
    
    Hexdump [{7}] size = 2
    01 80                                              ..
    
    Hexdump [{8}] size = 3
    02 00 01                                           ...
    
    Hexdump [{15}] size = 3
    02 00 80                                           ...
    
    Hexdump [{55}] size = 8
    07 00 00 00  00 00 00 80                            .... .... 
    
    Hexdump [{56}] size = 9
    08 00 00 00  00 00 00 00  01                       .... .... .
    
    Hexdump [{63}] size = 9
    08 00 00 00  00 00 00 00  80                       .... .... .
    
    Hexdump [{64}] size = 10
    09 00 00 00  00 00 00 00  00 01                    .... .... ..
    
    Hexdump [{65}] size = 10
    09 00 00 00  00 00 00 00  00 02                    .... .... ..
    
    Hexdump [{0, 1, 2, 4}] size = 2
    01 17                                              ..
    
    Hexdump [{0, 1, 2, 4, 8}] size = 3
    02 17 01                                           ...
    
    Hexdump [{8, 17, 24, 25, 34, 40, 42, 49, 50}] size = 8
    07 00 01 02  03 04 05 06                            .... .... 
    
    Hexdump [{8, 17, 24, 25, 34, 40, 42, 49, 50, 56, 57, 58}] size = 9
    08 00 01 02  03 04 05 06  07                       .... .... .
    
    Hexdump [{8, 17, 24, 25, 34, 40, 42, 49, 50, 56, 57, 58, 67}] size = 10
    09 00 01 02  03 04 05 06  07 08                    .... .... ..
    
    Hexdump [{8, 17, 24, 25, 34, 40, 42, 49, 50, 56, 57, 58, 67, 72, 75}] size = 11
    0A 00 01 02  03 04 05 06  07 08 09                 .... .... ...
    
    Hexdump [{8, 17, 24, 25, 34, 40, 42, 49, 50, 56, 57, 58, 67, 72, 75, 81, 83}] size = 12
    0B 00 01 02  03 04 05 06  07 08 09 0A               .... .... .... 

##### Partial Structure Serialization

Each structure can (depending on message definition) have a BitSet
instance defining what subset of that structure's fields have been
serialized. This allows partial serialization of structures. That is,
serializing only fields that have changed rather than the entire
structure. Each node of a structure corresponds to one bit; if a bit is
set then its corresponding field has been serialized, otherwise not.
BitSet does not apply to array elements.

This example shows how bits of a BitSet are assigned to the fields of a
structure:

    bit#    field
    0    structure 
    1        structure timeStamp
    2            long secondsPastEpoch 
    3            int nanoSeconds 
    4            int userTag
    5        structure[] value 
                structure org.epics.ioc.test.testStructure
                    double value 
                    structure location
                        double x
                        double y
                structure org.epics.ioc.test.testStructure
                    double value 
                    structure location
                        double x
                        double y 
    6        string factoryRPC
    7        structure arguments
    8            int size

The structure above requires a BitSet that contains 9 bits.  
If the bit corresponding to a structure node is set, then all the fields
of that node MUST be serialized.

#### Status

pvAccess defines a structure to inform endpoints about completion
status. It is nominally defined as:

    struct Status {
        byte type;      // enum { OK = 0, WARNING = 1, ERROR = 2, FATAL = 3 }
        string message;
        string callTree;   // optional (provides more context data about the error), can be empty
    };

In practice, since the majority of Status instances would be OK with no
message and no callTree, a special definition of Status SHOULD be used
in the common case that all three of these conditions are met; if Status
is OK and no message and no callTree would be sent, then the special
type value of `-1` MAY be used, and in this case the string fields are
omitted:

    struct StatusOK {
        byte type = -1;
    };

Examples of Status serialization:

    Hexdump [Status OK] size = 1
    FF                                                 .
    
    Hexdump [WARNING, "Low memory", ""] size = 13
    01 0A 4C 6F  77 20 6D 65  6D 6F 72 79  00          ..Lo w me mory .
    
    Hexdump [ERROR, "Failed to get, due to unexpected exception", (call tree)] size = 264
    02 2A 46 61  69 6C 65 64  20 74 6F 20  67 65 74 2C  .*Fa iled  to  get, 
    20 64 75 65  20 74 6F 20  75 6E 65 78  70 65 63 74   due  to  unex pect 
    65 64 20 65  78 63 65 70  74 69 6F 6E  DB 6A 61 76  ed e xcep tion .jav 
    61 2E 6C 61  6E 67 2E 52  75 6E 74 69  6D 65 45 78  a.la ng.R unti meEx 
    63 65 70 74  69 6F 6E 0A  09 61 74 20  6F 72 67 2E  cept ion. .at  org. 
    65 70 69 63  73 2E 63 61  2E 63 6C 69  65 6E 74 2E  epic s.ca .cli ent. 
    65 78 61 6D  70 6C 65 2E  53 65 72 69  61 6C 69 7A  exam ple. Seri aliz 
    61 74 69 6F  6E 45 78 61  6D 70 6C 65  73 2E 73 74  atio nExa mple s.st 
    61 74 75 73  45 78 61 6D  70 6C 65 73  28 53 65 72  atus Exam ples (Ser 
    69 61 6C 69  7A 61 74 69  6F 6E 45 78  61 6D 70 6C  iali zati onEx ampl 
    65 73 2E 6A  61 76 61 3A  31 31 38 29  0A 09 61 74  es.j ava: 118) ..at 
    20 6F 72 67  2E 65 70 69  63 73 2E 63  61 2E 63 6C   org .epi cs.c a.cl 
    69 65 6E 74  2E 65 78 61  6D 70 6C 65  2E 53 65 72  ient .exa mple .Ser 
    69 61 6C 69  7A 61 74 69  6F 6E 45 78  61 6D 70 6C  iali zati onEx ampl 
    65 73 2E 6D  61 69 6E 28  53 65 72 69  61 6C 69 7A  es.m ain( Seri aliz 
    61 74 69 6F  6E 45 78 61  6D 70 6C 65  73 2E 6A 61  atio nExa mple s.ja 
    76 61 3A 31  32 36 29 0A                            va:1 26). 

#### Introspection Data

Introspection data describes the type of a user data item. It is not
itself user data, but rather meta data. Introspection data appears in
one of four forms: no introspection data (NULL\_TYPE\_CODE), a full type
description (FULL\_TYPE\_CODE), a type identifier
(ONLY\_ID\_TYPE\_CODE), both (FULL\_WITH\_ID\_TYPE\_CODE), according to
the table "Encoding of Introspection Data".

The sender MUST send introspection data, but is free to chose one of the
above methods. Sending FULL\_WITH\_ID\_TYPE\_CODE defines the type
identifier for subsequent sends using ONLY\_ID\_TYPE\_CODE. Therefore,
before sending ONLY\_ID\_TYPE\_CODE, the sender MUST have previously
sent at least one FULL\_WITH\_ID\_TYPE\_CODE with the same type
identifier to the same receiver.

Since user data types can be arbitrarily complex, introspection data
SHOULD be sent only once per type and receiver combination. The mapping
of dynamically assigned type identifier (ID) to introspection data MUST
be cached on the receiver side, and SHOULD be cached and re-used on the
sender side. ID MUST be encoded as short and MUST be valid only within
one connection. Moreover, IDs MUST be assigned only by the sender. The
receiver MUST keep track of the IDs and use them to identify
deserializations. Since communication is full-duplex this implies there
MUST be two introspection registries per connection. The sender MAY
override a previously assigned ID by simply assigning the ID to a new
introspection data instance. The introspection registry size MUST be
negotiated when each connection is established.

<table>
<caption>Encoding of Introspection Data (called Field for future reference).</caption>
<thead>
<tr class="header">
<th>Field Encoding</th>
<th>Name</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>0xFF</td>
<td>NULL_TYPE_CODE</td>
<td>No introspection data (also implies no data).</td>
</tr>
<tr class="even">
<td>0xFE + ID</td>
<td>ONLY_ID_TYPE_CODE</td>
<td>Serialization contains only an ID (that was assigned by one of the previous FULL_WITH_ID_TYPE_CODE or FULL_TAGGED_ID_TYPE_CODE descriptions).</td>
</tr>
<tr class="odd">
<td>0xFD + ID + FieldDesc</td>
<td>FULL_WITH_ID_TYPE_CODE</td>
<td>Serialization contains an ID (that can be used later, if cached) and full interface description. Any existing definition with the same ID is overriden.</td>
</tr>
<tr class="even">
<td>0xFC + ID + tag + FieldDesc</td>
<td>FULL_TAGGED_ID_TYPE_CODE</td>
<td>Serialization contains an ID (that can be used later, if cached), tag (of integer type) and full interface description. Any existing definition with the same ID is overriden. A tag must guarantee that the same (ID, FieldDesc) pair has the same tag and any previous definition with the same ID and different FieldDesc has a different tag. This identifies whether the definition with given ID overrides already existing one and allow receivers to skip deserialization of FieldDesc, if tags match. SHOULD be used in non-reliable transport systems only.<br />
</td>
</tr>
<tr class="odd">
<td>0xFB - 0xE0</td>
<td>RESERVED</td>
<td>Reserved for future usage, MUST NOT be used.</td>
</tr>
<tr class="even">
<td>FieldDesc<br />
(0xDF - 0x00)</td>
<td>FULL_TYPE_CODE</td>
<td>Serialization contains only full interface description.</td>
</tr>
</tbody>
</table>

Each instance of a Field introspection description (FieldDesc) MUST be
encoded as a byte. The upper 3 bits (Most Significant Bits, MSBs) are
used for the type selector, e.g. 'integer'.
The middle 2 bits distinguish between arrays and scalars.
The remaining 3 lower bits are type dependent and used for size
encoding, e.g. to select a 'short' or 'long' integer.

<table>
<caption>Type Encoding.</caption>
<thead>
<tr class="header">
<th>Bit</th>
<th>Value</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr><td rowspan="7">7-5</td><td>111</td><td>reserved (MUST never be used)</td></tr>
<tr><td>110, 101</td><td>reserved (MUST not be used)</td></tr>
<tr><td>100</td><td>complex</td></tr>
<tr><td>011</td><td>string</td></tr>
<tr><td>010</td><td>floating-point</td></tr>
<tr><td>001</td><td>integer</td></tr>
<tr><td>000</td><td>boolean</td></tr>

<tr><td rowspan="4">4-3</td><td>11</td><td>fixed-size array flag</td></tr>
<tr><td>10</td><td>bounded-size array flag</td></tr>
<tr><td>01</td><td>variable-size array flag</td></tr>
<tr><td>00</td><td>scalar flag</td></tr>

<tr><td>2-0</td><td> </td><td>type (bits 7-5) depended</td></tr>
</tbody>
</table>

<table>
<caption>Integer Type Size Encoding (type = '0b001').</caption>
<thead>
<tr class="header">
<th>Bit</th>
<th>Value</th>
<th>Type Name</th>
</tr>
</thead>
<tbody>
<tr><td rowspan="2">2</td><td>1</td><td>unsigned flag</td></tr>
<tr><td>0</td><td>signed flag</td></tr>
<tr><td rowspan="4">1-0</td><td>11</td><td>long</td></tr>
<tr><td>10</td><td>int</td></tr>
<tr><td>01</td><td>short</td></tr>
<tr><td>00</td><td>byte</td></tr>
</tbody>
</table>

<table>
<caption>Floating-Point Size Encoding (type = '0b010').</caption>
<thead>
<tr class="header">
<th>Bit</th>
<th>Value</th>
<th>Type Name</th>
<th>IEEE 754-2008 Name</th>
</tr>
</thead>
<tbody>
<tr><td rowspan="6">2-0</td><td>111, 110, 101</td><td>reserved</td><td></td></tr>
<tr><td>100</td><td>reserved</td><td>binary128 (Quadruple)</td></tr>
<tr><td>011</td><td>double</td><td>binary64 (Double)</td></tr>
<tr><td>010</td><td>float</td><td>binary32 (Single)</td></tr>
<tr><td>001</td><td>reserved</td><td>binary16 (Half)</td></tr>
<tr><td>000</td><td>reserved</td><td></td></tr>
</tbody>
</table>

<table>
<caption>Complex Type Encoding (type = '0b100').</caption>
<thead>
<tr class="header">
<th>Bit</th>
<th>Value</th>
<th>Type Name</th>
</tr>
</thead>
<tbody>
<tr><td rowspan="5">2-0</td><td>111, 110, 101, 100</td><td>reserved</td></tr>
<tr><td>011</td><td>bounded string</td></tr>
<tr><td>010</td><td>variant union</td></tr>
<tr><td>001</td><td>union</td></tr>
<tr><td>000</td><td>structure</td></tr>
</tbody>
</table>

For all other types, bits 2-0 MUST be '0b000'.

Structure, union, and bounded string (and all their arrays) REQUIRE more
description. A structure REQUIRES its identification string and a named
array of Fields - size followed by one or more (field name, FieldDesc)
pairs. Arrays of structures/unions REQUIRE an introspection data of a
structure/union defining an array element type.

<table>
<caption>FieldDesc Encoding.</caption>
<thead>
<tr class="header">
<th>FieldDesc Encoding</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr><td>0bxxx00xxx</td><td>Scalar</td></tr>
<tr><td>0bxxx01xxx</td><td>Variable-size array of scalars</td></tr>
<tr><td>0bxxx10xxx + bound (encoded as size)</td><td>Bounded-size array of scalars</td></tr>
<tr><td>0bxxx11xxx + fixed size (encoded as size)</td><td>Fixed-size array of scalars</td></tr>
<tr><td>0b10000000 + identification string + (field name, FieldDesc)[]</td><td>Structure</td></tr>
<tr><td>0b10001000 + structure FieldDesc</td><td>Array of structures.</td></tr>
<tr><td>0b10000001 + identification string + (field name, FieldDesc)[]</td><td>Union</td></tr>
<tr><td>0b10001001 + union FieldDesc</td><td>Array of unions</td></tr>
<tr><td>0b10000010</td><td>Variant union</td></tr>
<tr><td>0b10001010</td><td>Array of variant unions</td></tr>
<tr><td>0b10000110 + bound (encoded as size)</td><td>Bounded string</td></tr>
</tbody>
</table>


##### Example \#1

Given the following structure, as may be expressed by a pvData
Structure:

    timeStamp_t
        long secondsPastEpoch
        int nanoSeconds
        int userTag

The introspection description of the above structure is be encoded by
pvAccess as the following:

    Hexdump [Serialized structure IF] size = 57
    FD 00 01 80  0B 74 69 6D  65 53 74 61  6D 70 5F 74  .... .tim eSta mp_t 
    03 10 73 65  63 6F 6E 64  73 50 61 73  74 45 70 6F  ..se cond sPas tEpo 
    63 68 23 0B  6E 61 6E 6F  53 65 63 6F  6E 64 73 22  ch#. nano Seco nds" 
    07 75 73 65  72 54 61 67  22                        .use rTag "

##### Example \#2

Given the following structure, as may be expressed by a pvData
Structure:

    exampleStructure
        byte[] value
        byte<16> boundedSizeArray
        byte[4] fixedSizeArray
        time_t timeStamp
            long secondsPastEpoch
            int nanoseconds
            int userTag
        alarm_t alarm
            int severity
            int status
            string message
        union valueUnion
            string stringValue
            int intValue
            double doubleValue
        any variantUnion

The introspection description of the above structure would be encoded by
pvAccess as the following:

    Hexdump [Serialized structure IF] size = 243
    FD 00 01 80  10 65 78 61  6D 70 6C 65  53 74 72 75  .... .exa mple Stru 
    63 74 75 72  65 07 05 76  61 6C 75 65  28 10 62 6F  ctur e..v alue (.bo 
    75 6E 64 65  64 53 69 7A  65 41 72 72  61 79 30 10  unde dSiz eArr ay0. 
    0E 66 69 78  65 64 53 69  7A 65 41 72  72 61 79 38  .fix edSi zeAr ray8 
    04 09 74 69  6D 65 53 74  61 6D 70 FD  00 02 80 06  ..ti meSt amp. .... 
    74 69 6D 65  5F 74 03 10  73 65 63 6F  6E 64 73 50  time _t.. seco ndsP 
    61 73 74 45  70 6F 63 68  23 0B 6E 61  6E 6F 73 65  astE poch #.na nose 
    63 6F 6E 64  73 22 07 75  73 65 72 54  61 67 22 05  cond s".u serT ag". 
    61 6C 61 72  6D FD 00 03  80 07 61 6C  61 72 6D 5F  alar m... ..al arm_ 
    74 03 08 73  65 76 65 72  69 74 79 22  06 73 74 61  t..s ever ity" .sta 
    74 75 73 22  07 6D 65 73  73 61 67 65  60 0A 76 61  tus" .mes sage `.va 
    6C 75 65 55  6E 69 6F 6E  FD 00 04 81  00 03 0B 73  lueU nion .... ...s 
    74 72 69 6E  67 56 61 6C  75 65 60 08  69 6E 74 56  trin gVal ue`. intV 
    61 6C 75 65  22 0B 64 6F  75 62 6C 65  56 61 6C 75  alue ".do uble Valu 
    65 43 0C 76  61 72 69 61  6E 74 55 6E  69 6F 6E FD  eC.v aria ntUn ion. 
    00 05 82                                            ...
