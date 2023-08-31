# Address Specification


Address parameters specify where an input record obtains input,
where an output record obtains its desired output values,
and where an output record writes its output.
These are used to identify links between records,
and to specify the location of hardware devices.
The most common link fields are OUT, an output link,
INP, an input link,
and DOL (desired output location), also an input link.

Three basic types of address specifications can appear in these fields:
hardware addresses, database addresses, and constants.
Note that not all links support all three types, though some do.
This doesn't hold true for algorithmic records,
which can't specify hardware addresses.
Algorithm records are records like the Calculation, PID, and Select records.
These records are used to process values retrieved from other records.
Consult the documentation for each record.

## Hardware addresses

The interface between EPICS process database logic and hardware drivers
is indicated in two fields of records that support hardware interfaces:
DTYP and INP/OUT.
The DTYP field is the name of the device support entry table
that's used to interface to the device.
The address specification is dictated by the device support.
Some conventions exist for several buses that are listed below.
Lately, more devices have just opted to use a string
that's then parsed by the device support as desired.
This specification type is called INST I/O.
The other conventions listed here include:
VME, Allen-Bradley, CAMAC, GPIB, BITBUS, VXI, and RF.
The input specification for each of these is different.
The specification of these strings must be acquired
from the device support code or document.

### INST


The INST I/O specification is a string that's parsed by the device
support. The format of this string is determined by the device support.

@*parm*
>For INST I/O 
>>@ precedes optional string *parm*

### VME bus

The VME address specification format differs between the various devices.
In all these specifications the '#' character designates a hardware address.
The three formats are:

#C*x* S*y* @*parm*

> For analog in, analog out, and timer
>>- C precedes the card number *x*
>>- S precedes the signal number *y*
>>- @ precedes optional string *parm*

The card number in the VME addresses refers to the logical card number.
Card numbers are assigned by address convention;
their position in the backplane is of no consequence.
The addresses are assigned by the technician who populates the backplane,
with the logical numbers well documented.
The logical card numbers start with 0 as do the signal numbers.
*parm* refers to an arbitrary string of up to 31 characters
and is device specific.

### Allen-Bradley bus

The Allen-Bradley address specification is a bit more complicated
as it has several more fields.
The '#' designates a hardware address.
The format is:

#L*a* A*b* C*c* S*d* @*parm'*
> All record types
>>- L precedes the serial link number *a* and is optional - default 0
>>- A precedes the adapter number *b* and is optional - default 0
>>- C precedes the card number *c*
>>- S precedes the signal number *d*
>>- @ precedes optional string *parm*

The card number for Allen-Bradley I/O refers to the physical slot number,
where 0 is the slot directly to the right of the adapter card.
The AllenBradley I/O has 12 slots available for I/O cards numbered 0through 11.
Allen-Bradley I/O may use double slot addresses
which means that slots 0,2,4,6,8, and 10 are used for input modules
and slots 1,3,5,7,9 and 11 are used for output modules.
It's required to use the double slot addressing mode
when the 1771IL card is used as it only works in double slot addressing mode.
This card is required as it provides Kilovolt isolation.

### Camac Bus

The CAMAC address specification is similar to the Allen-Bradley address
specification. The '#' signifies a hardware address. The format is:

#B*a* C*b* N*c* A*d* F*e* @*parm*
>For waveform digitizers
>>- B precedes the branch number *a* C precedes the crate number *b*
>>- N precedes the station number *c*
>>- A precedes the subaddress *d* (optional)
>>- F precedes the function *e* (optional)
>>- @ precedes optional string *parm*

The waveform digitizer supported is only one channel per card;
no channel was necessary.

### Others

The GPIB, BITBUS, RF, and VXI card-types
have been added to the supported I/O cards.
A brief description of the address format for each follow.
For a further explanation, see the specific documentation on each card.

#L*a* A*b* @*parm*
>For GPIB I/O
>>- L precedes the link number *a*
>>- A precedes the GPIB address *b*
>>- @ precedes optional string *parm*

---

#L*a* N*b* P*c* S*d* @*parm*
>>For BITBUS I/O
>>- L precedes the link *a*, that is, the VME bitbus interface
>>- N precedes the bitbus node *b*
>>- P precedes the port on node *c*
>>- S precedes the signal on port *d*
>>-@ precedes optional string *parm*

---

#V*a* C*b* S*c* @*parm*
>For VXI I/O, dynamic addressing
>>-V precedes the VXI frame number *a*
>>- C precedes the slot within VXI frame *b*
>>- S precedes the signal number *c*
>>- @ precedes optional string *parm*

---

#V*a* S*b* @*parm*
>For VXI I/O, static addressing
>>- V precedes the logical address *a*
>>- S precedes the signal number *b*
>>- @ precedes optional string *parm*

## Database Addresses

Database addresses are used to specify input links,
desired output links, output links, and forward processing links.
The format in each case is the same:

`<RecordName>.<FieldName>`

where RecordName is the name of the record being referenced,
'.' is the separator between the record name and the field name,
and FieldName is the name of the field within the record.

The record name and field name specification are case-sensitive.
The record name can be a mix of the following:

`a-z A-Z 0-9 _ - : . [ ] < > ;.`

The field name is always upper case.
If no field name is specified as part of an address,
the value field (VAL) of the record is assumed.
Forward processing links don't need to include the field name
because no value is returned when a forward processing link is used;
therefore, a forward processing link need only specify a record name.

Basic typecast conversions are made automatically
when a value is retrieved from another record -
integers are converted to floating point numbers
and floating point numbers are converted to integers.
For example, a calculation record which uses the value field of a binary input
will get a floating point 1 or 0 to use in the calculation,
because a calculation record's value fields are floating point numbers.
If the value of the calculation record
is used as the desired output of a multi-bit binary output,
the floating point result is converted to an integer,
because multi-bit binary outputs use integers.

Records that use soft device support routines
or have no hardware device support routines are called *soft records*.
See the chapter on each record
for information about that record's device support.

### Constants

Input link fields and desired output location fields can specify a constant
instead of a hardware or database address.
A constant, which isn't really an address,
can be an integer value in whatever format
(hex, decimal, etc.) or a floating-point value.
The value field is initialized to the constant when the database is initialized,
and at run-time the value field can be changed by a database access routine.
For instance, a constant may be used in an input link of a calculation record.
For non-constant links,
the calc record retrieves the values from the input links,
and places them in a corresponding value field.
For constant links,
the value fields are initialized with the constant,
and the values can be changed by modifying the value field, not the link field.
Thus, because the calc record uses its value fields
as the operands of its expression, the constant becomes part of the calculation.

When nothing is specified in a link field, it's a NULL link.
Before Release 3.13, the value fields associated with the NULL link
were initialized with the value of zero.
From Release 3.13 onward,
the value fields associated with the links aren't initialized.

A constant may also be used in the desired output location
or `DOL` field of an output record.
In such a case, the initial desired output value (`VAL`) will be that constant.
Any specified conversions are performed on the value
before it's written as long as the device support module supports conversions
(the Soft Channel device support routine doesn't perform conversions).
The desired output value can be changed by an operator at run-time
by writing to the value field.

A constant can be used in an output link field,
but no output will be written if this is the case.
Be aware that this isn't considered an error
by the database checking utilities.
