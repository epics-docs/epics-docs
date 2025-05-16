# Device Support

See {doc}`epics-base:devSup_h` for up-to-date API information.

##  Overview

In addition to a record support module, each record type can have an arbitrary number of device support modules. The 
purpose of device support is to hide hardware specific details from record processing routines. Thus support can be 
developed for a new device without changing the record support routines.

A device support routine has knowledge of the record definition. It also knows how to talk to the hardware directly or how 
to call a device driver which interfaces to the hardware. Thus device support routines are the interface between hardware 
specific fields in a database record and device drivers or the hardware itself.

Release 3.14.8 introduced the concept of extended device support, which provides an optional interface that a device 
support can implement to obtain notification when a record's address is changed at runtime. This permits records to be 
reconnected to a different kind of I/O device, or just to a different signal on the same device.
Extended device support is described in more detail in section [Extended Device Support](#extended-device-support) below.

Database common contains two device related fields:

- dtyp:  Device Type.

- {external+epics-base:cpp:class}`typed_dset`:  Address of (type-safe) Device Support Entry Table.

```{note}
A type-safe version of the dset structure has been added to the {doc}`epics-base:devSup_h` header.
The original structure definition has not been changed so existing support modules will still build normally,
but older modules can be modified and new code written to be compatible with both.
```
### Device Support Entry Table definition

Since EPICS Base Release 7.0.4, record types in Base define their Device Support Entry Table (DSET)
structures in the record header file. While this is still optional, developers of
external support modules are encouraged to use the record's new definitions 
instead of the traditional approach of copying the structure definitions into each source file 
that needs them. By following the instructions below it is still possible for the converted code to build and
work with older Base releases.

At the same time it would also be good to modify the device support to use the **type-safe
device support entry tables** that were introduced in Base-3.16.2 -- see
[the corresponding section below](#type-safe-device-and-driver-support-tables) for the
description of that change, which is also optional for now.

Look at the aiRecord for example. Near the top of the generated {doc}`epics-base:aiRecord_h`
header file is a new section that declares the `aidset`:

```C
/* Declare Device Support Entry Table */
struct aiRecord;
typedef struct aidset {
    dset common;
    long (*read_ai)(struct aiRecord *prec);
    long (*special_linconv)(struct aiRecord *prec, int after);
} aidset;
#define HAS_aidset
```

Notice that the common members (`number`, `report()`, `init()`, `init_record()`
and `get_ioint_info()` don't appear directly, but are included by embedding the
`dset common` member instead. This avoids the need to have separate definitions
of those members in each record dset, but does require those members to be
wrapped inside another set of braces `{}` when initializing the data structure
for the individual device supports. It also requires changes to code that
references those common members, but that code usually only appears inside the
record type implementation and very rarely in device supports.

An {doc}`aiRecord <epics-base:aiRecord>` device support that will only be built against 7.0.4 or later
versions of EPICS can now declare its dset like this:

```C
aidset devAiSoft = {
    { 6, NULL, NULL, init_record, NULL },
    read_ai, NULL
};
epicsExportAddress(dset, devAiSoft);
```

However, most device support that is not built into EPICS itself will need to
remain compatible with older EPICS versions, which is why the ai record's header
file also declares the preprocessor macro `HAS_aidset`. This makes it easy to
define the `aidset` in the device support code when it's needed, and not when
it's provided in the header:

```C
#ifndef HAS_aidset
typedef struct aidset {
    dset common;
    long (*read_ai)(aiRecord *prec);
    long (*special_linconv)(aiRecord *prec, int after);
} aidset;
#endif
aidset devAiSoft = {
    { 6, NULL, NULL, init_record, NULL },
    read_ai, NULL
};
epicsExportAddress(dset, devAiSoft);
```

The above `typedef struct` declaration was copied directly from the new
{doc}`epics-base:aiRecord_h` file and wrapped in the `#ifndef HAS_aidset` conditional.

This same pattern should be followed for all record types except for the {doc}`lsi <epics-base:lsiRecord>`,
{doc}`lso <epics-base:lsoRecord>` and {doc}`printf <epics-base:printfRecord>` record types, 
which have published their device support entry
table structures since they were first added to Base but didn't previously embed
the `dset common` member. Device support for these record types therefore can't
use the dset name since the new definitions are different from the originals and
will cause a compile error, so this pattern should be used instead:

```C
#ifndef HAS_lsidset
struct {
    dset common;
    long (*read_string)(lsiRecord *prec);
}
#else
lsidset
#endif
devLsiEtherIP = {
    {5, NULL, lsi_init, lsi_init_record, get_ioint_info},
    lsi_read
};
```

The field `DTYP` contains the index of the menu choice as defined by the device ASCII definitions. `iocInit` uses this 
field and the device support structures defined in {doc}`epics-base:devSup_h` to initialize the field `DSET`. 
Thus record support can locate its associated device support via the `DSET` field.

## Synchronous vs. Asynchronous Device Support

Device support modules can be divided into two basic classes: synchronous and asynchronous. Synchronous device 
support is used for hardware that can be accessed without delays for I/O. Many register based devices are synchronous 
devices. Other devices, for example all devices accessed through a network or serial interface, can only be accessed
via I/O requests that may take large amounts
of time to complete. Such devices must have associated asynchronous device support. This changes the way that links between
records work, which needs to be taken into account when designing databases.

:::{tip}
A common framework for writing asynchronous device support is the {doc}`asyn:index` module.
Source code repository is [here](https://github.com/epics-modules/asyn).
:::

If a device can be accessed with a delay of less than a few microseconds, synchronous device support is appropriate.
If a device causes delays of greater than 100 microseconds, asynchronous device support is appropriate.
Between these values the best solution depends on the specific use case.

If a device takes a long time to accept requests there is another option than asynchronous device support.

Some device support modules for slow devices use a different design:
The driver periodically polls all its attached input devices. The device support (synchronously) returns the latest polled value.
Output values are just (synchronously) forwarded to the driver, which, during one of its polling phases, writes the new value to the device.
The EPICS Allen Bradley device/driver support is an example using this concept.

###  Example Synchronous Device Support Module

```C
/* Create the dset for devBiSoft */
static long init_record(dbCommon *pcommon);
static long read_bi(biRecord *prec);

bidset devBiSoft = {
    {5, NULL, NULL, init_record, NULL},
    read_bi
};
epicsExportAddress(dset, devBiSoft);

static long init_record(dbCommon *pcommon)
{
    biRecord *prec = (biRecord *)pcommon;

    if (recGblInitConstantLink(&prec->inp, DBF_ENUM, &prec->val))
        prec->udf = FALSE;
    return 0;
}

static long readLocked(struct link *pinp, void *dummy)
{
    biRecord *prec = (biRecord *) pinp->precord;
    long status = dbGetLink(pinp, DBR_USHORT, &prec->val, 0, 0);

    if (status) return status;

    prec->udf = FALSE;
    if (dbLinkIsConstant(&prec->tsel) &&
        prec->tse == epicsTimeEventDeviceTime)
        dbGetTimeStamp(pinp, &prec->time);

    return 2;
}

static long read_bi(biRecord *prec)
{
    long status = dbLinkDoLocked(&prec->inp, readLocked, NULL);

    if (status == S_db_noLSET)
        status = readLocked(&prec->inp, NULL);

    return status;
}

```

The example is `devBiSoft` (status at Base release 7.0.8) which supports soft binary inputs.
The `INP` field can be a constant or a database link or a channel access (CA or PVA) link.
Only two routines are provided in the dset (the rest are declared `NULL`).
The `init_record` routine first checks that the link type is valid.
If the link is a constant, it initializes `VAL` and clears the UDF alarm.

Atomic processing of a group of records that belong to the same lockset was implemented in Base release 3.16.1. 
For this purpose, the `read_bi` routine was split into two parts: 
First part tries to do a an atomic read within the lockset. If this is not possible or necessary
(the record does not belong to a lockset or the link does not support locked reads),
value and timestamp are read from the input link.

###  Example Asynchronous Device Support Module

This example shows how to write an asynchronous device support routine.
It does the following sequence of operations:

- When first called, `PACT` is `FALSE`.
It arranges for a callback (`myCallback`) routine to be called after a number of seconds specified by the `DISV` field.

- It prints a message stating that processing has started, sets `PACT` to `TRUE`, and returns.
The record processing routine returns without completing processing.

- When the specified time elapses `myCallback` is called.
It calls `dbScanLock` to lock the record, calls `process`, and calls `dbScanUnlock` to unlock the record.
It directly calls the `process` entry of the record support module, which it locates via the `RSET` field in `dbCommon`,
rather than calling `dbProcess`. `dbProcess` would not call `process` because `PACT` is `TRUE`.

- When `process` executes, it again calls `read_ai`.
This time `PACT` is `TRUE`.

- `read_ai` prints a message stating that record processing is complete and returns a status of 2.
Normally a value of  0 would be returned.
The value 2 tells the record support routine not to attempt any conversions.
This is a convention (a bad convention!) used by the analog input record.

- When `read_ai` returns the record processing routine completes record processing.

At this point the record has been completely processed.
The next time process is called everything starts all over.

Note that this is somewhat of an artificial example since real code of this form would more likely use
the `callbackRequestProcessCallbackDelayed` function to perform the required processing.

```C
static void myCallback(CALLBACK *pcallback)
{
    struct dbCommon   *precord;
    struct typed_rset *prset;

    callbackGetUser(precord,pcallback);
    prset = (struct typed_rset *)(precord->rset);
    dbScanLock(precord);
    (*prset->process)(precord);
    dbScanUnlock(precord);
}

static long init_record(struct aiRecord *pai)
{
    CALLBACK *pcallback;
    switch (pai->inp.type) {
    case (CONSTANT) :
        pcallback = (CALLBACK *)(calloc(1,sizeof(CALLBACK)));
        callbackSetCallback(myCallback,pcallback);
        callbackSetUser(pai,pcallback);
        pai->dpvt = (void *)pcallback;
        break;
    default :
        recGblRecordError(S_db_badField,(void *)pai,
            "devAiTestAsyn (init_record) Illegal INP field");
        return(S_db_badField);
    }
    return(0);
}

static long read_ai(struct aiRecord *pai)
{
    CALLBACK *pcallback = (CALLBACK *)pai->dpvt;
    if(pai->pact) {
        pai->val += 0.1; /* Change VAL just to show we've done something. */
        pai->udf = FALSE; /* We modify VAL so we are responsible for UDF too. */
        printf("Completed asynchronous processing: %s\n",pai->name);
        return(2); /* don't convert*/
    } 
    printf("Starting asynchronous processing: %s\n",pai->name);
    pai->pact=TRUE;
    callbackRequestDelayed(pcallback,pai->disv);
    return(0);
}

/* Create the dset for devAiSoft */
static long init_record(dbCommon *pcommon);
static long read_ai(aiRecord *prec);

aidset devAiSoft = {
    {6, NULL, NULL, init_record, NULL},
    read_ai, NULL
};
```

##  Device Support Routines

This section describes the routines defined in the `DSET`.
Any routine that does not apply to a specific record type must be declared `NULL`.

### Type-safe Device and Driver Support Tables

Type-safe versions of the device and driver support structures `dset` and
`drvet` have been added to the {doc}`epics-base:devSup_h` and {doc}`epics-base:drvSup_h` headers respectively. The
original structure definitions have not been changed so existing support
modules will still build normally, but older modules can be modified and new
code written to be compatible with both.

The old structure definitions will be replaced by the new ones, if the macros
`USE_TYPED_DSET` and/or `USE_TYPED_DRVET` are defined when the appropriate
header is included. The best place to define these is in the Makefile, as with
the `USE_TYPED_RSET` macro that was introduced in Base-3.16.1 and described
below. See the comments in `devSup.h` for a brief usage example.

A helper function `DBLINK* dbGetDevLink(dbCommon *prec)` has also been added
to `devSup.h` which fetches a pointer to the INP or OUT field of the record.

### Generate Device Report

{external+epics-base:cpp:member}`dset::report`

This routine is responsible for reporting all I/O cards it has found.
The `interest` value is provided to allow for different kinds of reports, or to control how much detail to display.
If a device support module is using a driver, it may choose not to implement this routine because the driver generates the report.

### Initialize Device Processing

{external+epics-base:cpp:member}`dset::init`

This routine is called at {doc}`IOC initialization <docs:appdevguide/IOCInit>` time.
Any action is device specific.
This routine is called twice: once before any database records are initialized, and once after all records are initialized,
but before the scan tasks are started.
`after` has the value 0 before and 1 after record initialization.

### Initialize Specific Record

{external+epics-base:cpp:member}`dset::init_record`

The record support `init_record` routine calls this routine.

### Get I/O Interrupt Information

{external+epics-base:cpp:member}`dset::get_ioint_info`

This routine is called by the I/O interrupt scan task,
with `cmd` set to 0 when the associated record is being placed into an I/O scan list, and `cmd` set to 1 when it is taken out.
See Scanning Specification in {doc}`Process Database Concepts </process-database/EPICS_Process_Database_Concepts>` for details.

All other device support routines are record type specific.

## Extended Device Support

This section describes the additional behaviour and routines required for a device support layer
to support online changes to a record's hardware address.

### Rationale

In releases prior to R3.14.8 it was possible to change the value of the INP or OUT field of a record.
Unless a soft device support is used, this generally has no effect on the behaviour of the device support at all.
Device supports can check this hardware address field for changes every time they process, but this will not allow
switching between different device support layers at runtime, as nothing can look up
a new value for the DSET field after iocInit.

The extended device interface has been carefully designed to retain maximal backwards compatibility with existing device and record support layers.
As a result it cannot just introduce new routines into the DSET:

- Different record types have different numbers of DSET routines

- Every device support module defines its own DSET structure layout

- Some device support modules add their own routines to the DSET (GPIB, BitBus)

Since both basic and extended device support layers have to co-exist within the same IOC, some rules are enforced concerning whether the device address
of a particular record is allowed to be changed:

- Records that were connected at iocInit to a device support module that does not implement the extended interface
  are never allowed to have address fields changed at runtime.

- Extended device support layers are not required to implement both the `add_record` and `del_record` routines; some devices may only allow one-way changes.

- The old device support layer is informed and allowed to refuse an address change before the field change is made (it does not get to see the new address).

- The new device support layer is informed after the field change has been made, and it may refuse to accept the new address.
In this case the record will be set as permanently busy (PACT=true) until an address is accepted.

- Record support layers can also get notified about this process by making their address field special, in which case the record type's special routine
can refuse to accept the new address before it is presented to the device support layer.
The special routine cannot prevent the old device support from being disconnected.

If an address change is refused, the change to the INP or OUT field will cause an error or exception to be passed to the software performing the change.
If the source was a remote network client, an exception callback will be generated.

To switch to a different device support module, it is necessary to change the `DTYP` field before the `INP` or `OUT` field.
The change to the `DTYP` field has no effect until the latter field change takes place.

If a record is set to I/O Interrupt scan but the new device support does not support this, the scan will be changed to `Passive`.

### Initialization/Registration

Device support that implements the extended behaviour must provide an `init` routine in the Device Support Entry Table 
(see Section [Initialize Device Processing](#initialize-device-processing) ).
In the first call to this routine (pass 0) it registers the address of its Device Support eXtension Table (DSXT) in a call to `devExtend`.

The only exception to this registration requirement is when the device support uses a link type of `CONSTANT`.  In this
circumstance the system will automatically register an empty DSXT for that particular support layer (both the 
`add_record` and `del_record` routines pointed to by this DSXT do nothing and return zero). This exception allows 
existing soft channel device support layers to continue to work without requiring any modification, since the iocCore 
software already takes care of changes to PV\_LINK addresses.

The following is an example of a DSXT and the initialization routine that registers it:

```C
static struct dsxt myDsxt = {
    add_record, del_record
};

static long init(int pass) {
    if (pass==0) devExtend(&myDsxt);
    return 0;
}
```

A call to `devExtend` can only be made during the first pass of the device support initialization process.
If called at any other time it will log an error message and immediately return.

### Device Support eXtension Table

The full definition of {external+epics-base:cpp:class}`struct dsxt <dsxt>` is found in {doc}`epics-base:devSup_h`.

It has at least the following members:

- {external+epics-base:cpp:member}`dsxt::add_record`

- {external+epics-base:cpp:member}`dsxt::del_record`

There may be future additions to this table to support additional functionality; such extensions may only be made by
changing the {doc}`epics-base:devSup_h` header file and rebuilding EPICS Base and all support modules.
Neither record types nor device support are permitted to make any private use of this table.

The two function pointers are the means by which the extended device support is notified about the record instances it is being given
or that are being moved away from its control.
In both cases the only parameter is a pointer to the record concerned, which the code will have to cast to the appropriate pointer for the record type.
The return value from the routines should be zero for success, or an EPICS error status code.

### Add Record Routine

{external+epics-base:cpp:member}`dsxt::add_record`

This function is called to offer a new record to the device support.
It is also called during `iocInit`, in between the pass 0 and pass 1 calls to the regular device support `init_record` routine
(described in section [Initialize Specific Record](#initialize-specific-record) above).
When converting an existing device support layer, this routine will usually be very similar to the old `init_record` routine, although in some cases
it may be necessary to do a little more work depending on the particular record type involved.
The extra code required in these cases can generally be copied straight from the record type implementation itself.
This is necessary because the record type has no knowledge of the address change that is taking place, so the device support must perform
any bitmask generation and/or readback value conversions itself.
This document does not attempt to describe all the necessary processing for the various different standard record types,
although the following (incomplete) list is presented as an aid to device support authors:

- mbbi/mbbo record types:
Set SHFT, convert NOBT and SHFT into MASK

- bi/bo record types:
Set SHFT, convert SHFT to MASK

- analog record types:
Calculate ESLO and EOFF

- Output record types:
Possibly read the current value from hardware and back-convert to VAL, or send the current record output value to the hardware. 
*This behaviour is not required or defined, and it's not obvious what should be done. There may be complications here with
ao records using `OROC` and/or `OIF=Incremental`; solutions to this issue have yet to be considered by the community.*

If the `add_record` routine discovers any errors, say in the link address, it should return a non-zero error status value to reject the record.
This will cause the record's `PACT` field to be set, preventing any further processing of this record until some other address change to it gets accepted.

### Delete Record Routine

{external+epics-base:cpp:member}`dsxt::del_record`

This function is called to notify the device support of a request to change the hardware address of a record, and allow the device support
to free up any resources it may have dedicated to this particular record.

Before this routine is called, the record will have had its `SCAN` field changed to `Passive` if it had been set to `I/O Interrupt`.
This ensures that the device support's `get_ioint_info` routine is never called after the the call to `del_record` has returned successfully,
although it may also lead to the possibility of missed interrupts if the address change is rejected by the `del_record` routine.

If the device support is unable to disconnect from the hardware for some reason, this routine should return a non-zero error status value,
which will prevent the hardware address from being changed.
In this event the `SCAN` field will be restored if it was originally set to I/O Interrupt.

After a successful call to `del_record`, the record's `DPVT` field is set to NULL and `PACT` is cleared, ready for use by the new device support.
Any dynamically allocated structures linked to the `DPVT` field must be released before `del_record` returns success.

### Init Record Routine

The `init_record` routine from the DSET (section [Initialize Specific Record](#initialize-specific-record)) is called by the record type,
and must still be provided since the record type's per-record initialization is run some time *after* the initial call to the DSXT's `add_record` routine.
Most record types perform some initialization of record fields at this point, and an extended device support layer
may have to fix anything that the record overwrites.
The following (incomplete) list is presented as an aid to device support authors:


- mbbi/mbbo record types:
Calculate MASK from SHFT

- analog record types:
Calculate ESLO and EOFF

- Output record types:
Perform readback of the initial raw value from the hardware.

