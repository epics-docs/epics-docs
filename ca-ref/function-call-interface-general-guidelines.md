# Function Call Interface General Guidelines

## Flushing and Blocking

Significant performance gains can be realized when the CA client library
doesn't wait for a response to return from the server after each
request. All requests which require interaction with a CA server are
accumulated (buffered) and not forwarded to the IOC until one of
{external+epics-base:cpp:func}`ca_flush_io`,
{external+epics-base:cpp:func}`ca_pend_io`,
{external+epics-base:cpp:func}`ca_pend_event`,
or {external+epics-base:cpp:func}`ca_sg_block`
are called allowing several operations to be efficiently sent over the
network together.
Any process variable values written into your program's variables
by {external+epics-base:c:macro}`ca_get() <ca_get>`
should not be referenced by your program
until {external+epics-base:c:macro}`ECA_NORMAL` has been received
from {external+epics-base:cpp:func}`ca_pend_io`.

## Status Codes

If successful, the routines described here return the status code
{external+epics-base:c:macro}`ECA_NORMAL`.
Unsuccessful status codes returned from the client library
are listed with each routine in this manual. Operations that appear to
be valid to the client can still fail in the server. Writing the string
`off` to a floating point field is an example of this type of error.
If the server for a channel is located in a different address space than
the client then the `ca_xxx()` operations that communicate with the
server return status indicating the validity of the request and whether
it was successfully enqueued to the server, but communication of
completion status is deferred until a user callback is called, or
lacking that an exception handler is called. An error number and the
error's severity are embedded in CA status (error) constants.
Applications shouldn't test the success of a CA function call by
checking to see if the returned value is zero as is the UNIX convention.
Below are several methods to test CA function returns. See
{external+epics-base:cpp:func}`ca_signal`
and {external+epics-base:c:macro}`SEVCHK() <SEVCHK>`
for more information on this topic.

``` c
status = ca_XXXX();
SEVCHK( status, "ca_XXXX() returned failure status");

if ( status & CA_M_SUCCESS ) {
        printf ( "The requested ca_XXXX() operation didn't complete successfully");
}

if ( status != ECA_NORMAL ) {
        printf("The requested ca_XXXX() operation didn't complete successfully because \"%s\"\n",
                ca_message ( status ) );
}
```

## Channel Access Data Types

CA channels form a virtual circuit between a process variable (PV) and a
client side application program. It is possible to connect a wide
variety of data sources into EPICS using the CA server library. When a
CA channel communicates with an EPICS Input Output Controller (IOC) then
a field is a specialization of a PV, and an EPICS record is a plug
compatible function block that contains fields, and the meta data below
frequently are mapped onto specific fields within the EPICS records by
the EPICS record support (see the EPICS Application Developer Guide).

Arguments of type chtype specifying the data type you wish to transfer.
They expect one of the set of `DBR_XXXX` data type codes defined in
db_access.h. There are data types for all of the C primitive types, and
there are also compound (C structure) types that include various process
variable properties such as units, limits, time stamp, or alarm status.
The primitive C types follow a naming convention where the C typedef
`dbr_xxxx_t` corresponds to the `DBR_XXXX` data type code. The compound (C
structure) types follow a naming convention where the C structure tag
`dbr_xxxx` corresponds to the `DBR_XXXX` data type code. The following
tables provides more details on the structure of the CA data type space.
Since data addresses are passed to the CA client library as typeless
`void *` pointers then care should be taken to ensure that you have
passed the correct C data type corresponding to the `DBR_XXXX` type that
you have specified. Architecture independent types are provided in
db_access.h to assist programmers in writing portable code. For example
{external+epics-base:cpp:type}`dbr_short_t` should be used
to send or receive type {external+epics-base:c:macro}`DBR_SHORT`.
Be aware that type name {external+epics-base:c:macro}`DBR_INT` has been deprecated
in favor of the less confusing type name {external+epics-base:c:macro}`DBR_SHORT`.
In practice, both the {external+epics-base:c:macro}`DBR_INT` type code
and the {external+epics-base:c:macro}`DBR_SHORT` type code refer to a 16 bit integer type,
and are functionally equivalent.

::: {table} Channel Access Primitive Data Types
| CA Type Code                              | Primitive C Data Type                               | Data Size                  |
|:------------------------------------------|:----------------------------------------------------|:---------------------------|
| {external+epics-base:c:macro}`DBR_CHAR`   | {external+epics-base:cpp:type}`dbr_char_t`          | 8 bit character            |
| {external+epics-base:c:macro}`DBR_SHORT`  | {external+epics-base:cpp:type}`dbr_short_t`         | 16 bit integer             |
| {external+epics-base:c:macro}`DBR_ENUM`   | {external+epics-base:cpp:type}`dbr_enum_t`          | 16 bit unsigned integer    |
| {external+epics-base:c:macro}`DBR_LONG`   | {external+epics-base:cpp:type}`dbr_long_t`          | 32 bit signed integer      |
| {external+epics-base:c:macro}`DBR_FLOAT`  | {external+epics-base:cpp:type}`dbr_float_t`         | 32 bit IEEE floating point |
| {external+epics-base:c:macro}`DBR_DOUBLE` | {external+epics-base:cpp:type}`dbr_double_t`        | 64 bit IEEE floating point |
| {external+epics-base:c:macro}`DBR_STRING` | {external+epics-base:cpp:type}`dbr_string_t`        | 40 character string        |
:::

::: {list-table} Channel Access Primitive Data Types Structure of the Channel Access Data Type Space
:header-rows: 1

* - CA Type Code
  - Read / Write
  - Primitive C Data Type
  - Process Variable Properties

* - `DBR_<PRIMITIVE TYPE>`
  - RW
  - `dbr_<primitive type>_t`
  - value
* - `DBR_STS_<PRIMITIVE TYPE>`
  - R
  - `struct dbr_sts_<primitive type>`
  - value, alarm status, and alarm severity
* - `DBR_TIME_<PRIMITIVE TYPE>`
  - R
  - `struct dbr_time_<primitive type>`
  - value, alarm status, alarm severity, and time stamp
* - `DBR_GR_<PRIMITIVE TYPE>`
  - R
  - `struct dbr_gr_<primitive type>`
  - value, alarm status, alarm severity, units, display precision, and graphic limits
* - `DBR_CTRL_<PRIMITIVE TYPE>`
  - R
  - `struct dbr_ctrl_<primitive type>`
  - value, alarm status, alarm severity, units, display precision, graphic limits, and control limits
* - {external+epics-base:c:macro}`DBR_PUT_ACKT`
  - W
  - {external+epics-base:cpp:type}`dbr_put_ackt_t`
  - Used for global alarm acknowledgement.
    Do transient alarms have to be acknowledged?

    (0,1) means (no, yes).
* - {external+epics-base:c:macro}`DBR_PUT_ACKS`
  - W
  - {external+epics-base:cpp:type}`dbr_put_acks_t`
  - Used for global alarm acknowledgement.
    The highest alarm severity to acknowledge.

    If the current alarm severity is less then or equal to this value the alarm is acknowledged.
* - {external+epics-base:c:macro}`DBR_STSACK_STRING`
  - R
  - {external+epics-base:cpp:type}`dbr_stsack_string_t`
  - value, alarm status, alarm severity, ackt, acks
* - {external+epics-base:c:macro}`DBR_CLASS_NAME`
  - R
  - {external+epics-base:cpp:type}`dbr_class_name_t`
  - name of enclosing interface (name of the record if channel is attached to EPICS run time database)
:::

Channel value arrays can also be included within the structured CA data
types. If more than one element is requested, then the individual
elements can be accessed in an application program by indexing a pointer
to the value field in the `DBR_XXX` structure. For example, the following
code computes the sum of the elements in a array process variable and
prints its time stamp. The {external+epics-base:c:macro}`dbr_size_n` function can
be used to determine the correct number of bytes to reserve when there
are more than one value field elements in a structured CA data type.

``` c
#include <stdio.h>
#include <stdlib.h>

#include "cadef.h"

int main ( int argc, char ** argv )
{
    struct dbr_time_double * pTD;
    const dbr_double_t * pValue;
    unsigned nBytes;
    unsigned elementCount;
    char timeString[32];
    unsigned i;
    chid chan;
    double sum;
    int status;

    if ( argc != 2 ) {
        fprintf ( stderr, "usage: %s <channel name>", argv[0] );
        return -1;
    }

    status = ca_create_channel ( argv[1], 0, 0, 0, & chan );
    SEVCHK ( status, "ca_create_channel()" );
    status = ca_pend_io ( 15.0 );
    if ( status != ECA_NORMAL ) {
        fprintf ( stderr, "\"%s\" not found.\n", argv[1] );
        return -1;
    }

    elementCount = ca_element_count ( chan );
    nBytes = dbr_size_n ( DBR_TIME_DOUBLE, elementCount );
    pTD = ( struct dbr_time_double * ) malloc ( nBytes );
    if ( ! pTD ) {
        fprintf ( stderr, "insufficient memory to complete request\n" );
        return -1;
    }

    status = ca_array_get ( DBR_TIME_DOUBLE, elementCount, chan, pTD );
    SEVCHK ( status, "ca_array_get()" );
    status = ca_pend_io ( 15.0 );
    if ( status != ECA_NORMAL ) {
        fprintf ( stderr, "\"%s\" didn't return a value.\n", argv[1] );
        return -1;
    }

    pValue = & pTD->value;
    sum = 0.0;
    for ( i = 0; i < elementCount; i++ ) {
        sum += pValue[i];
    }

    epicsTimeToStrftime ( timeString, sizeof ( timeString ),
        "%a %b %d %Y %H:%M:%S.%f", & pTD->stamp );

    printf ( "The sum of elements in %s at %s was %f\n",
        argv[1], timeString, sum );

    ca_clear_channel ( chan );
    ca_task_exit ();
    free ( pTD );

    return 0;
}
```

## User Supplied Callback Functions

Certain CA client initiated requests asynchronously execute an
application supplied callback in the client process when a response
arrives. The functions
{external+epics-base:c:macro}`ca_put_callback() <ca_put_callback>`,
{external+epics-base:c:macro}`ca_get_callback() <ca_get_callback>`,
and {external+epics-base:cpp:func}`ca_create_subscription`
all request notification of asynchronous
completion via this mechanism.
The {external+epics-base:cpp:class}`evargs` structure is
passed *by value* to the application supplied callback.

In this structure the {external+epics-base:cpp:member}`~evargs::dbr` field is a void pointer
to any data that might be returned.
The {external+epics-base:cpp:member}`~evargs::status` field will be set to one of the CA error codes
in {doc}`epics-base:caerr_h`
and will indicate the status of the operation performed in the IOC.
If the status field isn't set to {external+epics-base:c:macro}`ECA_NORMAL`
or data isn't normally returned from the operation (i.e. put callback)
then you should expect
that the {external+epics-base:cpp:member}`~evargs::dbr` field
will be set to a null pointer (zero).

The fields {external+epics-base:cpp:member}`~evargs::usr`,
{external+epics-base:cpp:member}`~evargs::chid`,
and {external+epics-base:cpp:member}`~evargs::type` are set to the values specified
when the request was made by the application.
The {external+epics-base:cpp:member}`~evargs::dbr` pointer,
and any data that it points to,
are valid only when executing within the user's callback function.

``` c
typedef struct event_handler_args {
    void            *usr;   /* user argument supplied with request */
    chanId          chid;   /* channel id */
    long            type;   /* the type of the item returned */
    long            count;  /* the element count of the item returned */
    const void      *dbr;   /* a pointer to the item returned */
    int             status; /* ECA_XXX status of the requested op from the server */
} evargs;

void myCallback ( struct event_handler_args args )
{
    if ( args.status != ECA_NORMAL ) {
    }
    if ( args.type == DBR_TIME_DOUBLE ) {
         const struct dbr_time_double * pTD =
              ( const struct dbr_time_double * ) args.dbr;
    }
}
```

## Channel Access Exceptions

When the server detects a failure, and there is no client callback
function attached to the request, an exception handler is executed in
the client. The default exception handler prints a message on the
console and exits if the exception condition is severe. Certain internal
exceptions within the CA client library, and failures detected by the
SEVCHK macro may also cause the exception handler to be invoked.
To modify this behavior
see {external+epics-base:cpp:func}`ca_add_exception_event`.

## Server and Client Share the Same Address Space on The Same Host

If the Process Variable's server and it's client are colocated within
the same memory address space and the same host then the `ca_xxx()`
operations bypass the server and directly interact with the server tool
component (commonly the IOC's function block database). In this
situation the `ca_xxx()` routines frequently return the completion
status of the requested operation directly to the caller with no
opportunity for asynchronous notification of failure via an exception
handler. Likewise, callbacks may be directly invoked by the CA library
functions that request them.

## Arrays

For routines that require an argument specifying the number of array
elements, no more than the process variable's maximum native element
count may be requested. The process variable's maximum native element
count is available from {external+epics-base:cpp:func}`ca_element_count`
when the channel is connected.

If fewer elements than the process variable's native element count are requested,
the requested values will be fetched beginning at element zero.
By default CA limits the number of elements in an array
to be no more than approximately 16k divided
by the size of one element in the array.
Starting with EPICS R3.14
the maximum array size may be configured in the client and in the server.

## Connection Management

Application programs should assume that CA servers may be restarted, and
that network connectivity is transient. When you create a CA channel its
initial connection state will most commonly be disconnected. If the
Process Variable's server is available the library will immediately
initiate the necessary actions to make a connection with it. Otherwise,
the client library will monitor the state of servers on the network and
connect or reconnect with the process variable's server as it becomes
available. After the channel connects the application program can freely
perform IO operations through the channel, but should expect that the
channel might disconnect at any time due to network connectivity
disruptions or server restarts.

Three methods can be used to determine if a channel is connected: the
application program might call {external+epics-base:cpp:func}`ca_state` to obtain the
current connection state, block in {external+epics-base:cpp:func}`ca_pend_io` until
the channel connects, or install a connection callback handler when it
calls {external+epics-base:cpp:func}`ca_create_channel`. The
{external+epics-base:cpp:func}`ca_pend_io` approach is best suited to simple
command line programs with short runtime duration, and the connection
callback method is best suited to toolkit components with long runtime
duration. Use of {external+epics-base:cpp:func}`ca_state` is appropriate only in
programs that prefer to poll for connection state changes instead of
opting for asynchronous notification.
The {external+epics-base:cpp:func}`ca_pend_io` function blocks
only for channels created specifying a null connection handler callback
function. The user's connection state change function will be run
immediately from within {external+epics-base:cpp:func}`ca_create_channel`
if the CA client and CA server are both hosted within the same address
space (within the same process).

## Thread Safety and Preemptive Callback to User Code

Starting with EPICS R3.14 the CA client libraries are fully thread safe
on all OS (in past releases the library was thread safe only on
vxWorks). When the client library is initialized the programmer may
specify if preemptive callback is to be enabled. Preemptive callback is
disabled by default. If preemptive callback is enabled, then the user's
callback functions might be called by CA's auxiliary threads when the
main initiating channel access thread is not inside of a function in the
channel access client library. Otherwise, the user's callback functions
will be called only when the main initiating channel access thread is
executing inside of the CA client library. When the CA client library
invokes a user's callback function, it will always wait for the current
callback to complete prior to executing another callback function.
Programmers enabling preemptive callback should be familiar with using
mutex locks to create a reliable multi-threaded program.

To set up a traditional single threaded client,
you will need code like this
(see {external+epics-base:cpp:func}`ca_context_create` and {ref}`ca-auxiliary-threads`).

```c
SEVCHK ( ca_context_create(ca_disable_preemptive_callback ), "application pdq calling ca_context_create" );
```

To set up a preemptive callback enabled CA client context,
you will need code like this
(see {external+epics-base:cpp:func}`ca_context_create` and {ref}`ca-auxiliary-threads`).

```c
SEVCHK ( ca_context_create(ca_enable_preemptive_callback ), "application pdq calling ca_context_create" );
```

(ca-auxiliary-threads)=
## CA Client Contexts and Application Specific Auxiliary Threads

It is often necessary for several CA client side tools running in the
same address space (process) to be independent of each other. For
example, the database CA links and the sequencer are designed to not use
the same CA client library threads, network circuits, and data
structures.
Each thread that calls
{external+epics-base:cpp:func}`ca_context_create` for the first time either
directly or implicitly when calling any CA library function for the
first time, creates a CA client library context. A CA client library
context contains all of the threads, network circuits, and data
structures required to connect and communicate with the channels that a
CA client application has created. The priority of auxiliary threads
spawned by the CA client library are at fixed offsets from the priority
of the thread that called {external+epics-base:cpp:func}`ca_context_create`.
An application specific auxiliary thread can join a CA context by
calling {external+epics-base:cpp:func}`ca_attach_context` using the CA
context identifier that was returned from
{external+epics-base:cpp:func}`ca_current_context` when it is called by the
thread that created the context which needs to be joined. A context
which is to be joined must be preemptive - it must be created using
`ca_context_create(ca_enable_preemptive_callback)`.
It is not possible to attach a thread to a non-preemptive CA context
created explicitly *or implicitly* with
`ca_create_context(ca_disable_preemptive_callback)`. Once a thread has
joined with a CA context it need only make ordinary `ca_xxxx()` library
calls to use the context.

A CA client library context can be shut down and cleaned up, after
destroying any channels or application specific threads that are
attached to it,
by calling {external+epics-base:cpp:func}`ca_context_destroy`.
The context may be created and destroyed by different threads
as long as they are both part of the same context.

## Polling the CA Client Library From Single Threaded Applications

If preemptive callback is not enabled, then for proper operation CA must
periodically be polled to take care of background activity. This
requires that your application must either wait in one of
{external+epics-base:cpp:func}`ca_pend_event`,
{external+epics-base:cpp:func}`ca_pend_io`,
or {external+epics-base:cpp:func}`ca_sg_block` or alternatively
it should call {external+epics-base:c:macro}`ca_poll() <ca_poll>`
at least every 100 milliseconds.
In single threaded applications a file descriptor manager like Xt or the
interface described in fdManager.h can be used to monitor both mouse clicks and
also CA's file descriptors so that `ca_poll()` can be called immediately when
CA server messages arrives over the network.

## Avoid Emulating Bad Practices that May Still be Common

With the embryonic releases of EPICS it was a common practice to examine
a channel's connection state, its native type, and its native element
count by directly accessing fields in a structure using a pointer stored
in type `chid`. Likewise, a user private pointer in the per channel
structure was also commonly set by directly accessing fields in the
channel structure. A number of difficulties arise from this practice,
which has long since been deprecated. For example, prior to release 3.13
it was recognized that transient changes in certain private fields in
the per channel structure would make it difficult to reliably test the
channels connection state using these private fields directly.
Therefore, in release 3.13 the names of certain fields were changed to
discourage this practice. Starting with release 3.14 codes written this
way will not compile. Codes intending to maintain the highest degree of
portability over a wide range of EPICS versions should be especially
careful. For example you should replace all instances off
`channel_id->count` with `ca_element_count(channel_id)`. This approach
should be reliable on all versions of EPICS in use today. The construct
`ca_puser(chid) = xxxx` is particularly problematic. The best mechanisms
for setting the per channel private pointer will be to pass the user
private pointer in when creating the channel. This approach is
implemented on all versions. Otherwise, you can also use
`ca_set_puser(CHID,PUSER)`, but this function is available only after
the first official (post beta) release of EPICS 3.13.

## Calling CA Functions from the vxWorks Shell Thread

Calling CA functions from the vxWorks shell thread is a somewhat
questionable practice for the following reasons.

-   The vxWorks shell thread runs at the very highest priority in the
    system and therefore socket calls are made at a priority that is
    above the priority of tNetTask. This has caused problems with the
    WRS IP kernel in the past. That symptom was observed some time ago,
    but we don't know if WRS has fixed the problem.

-   The vxWorks shell thread runs at the very highest priority in the
    system and therefore certain CA auxiliary threads will not get the
    priorities that are requested for them. This might cause problems
    only when in a CPU saturation situations.

-   If the code does not call {external+epics-base:cpp:func}`ca_context_destroy`
    (named {external+epics-base:cpp:func}`ca_task_exit` in past releases)
    then resources are left dangling.

-   In EPICS R3.13 the CA client library installed vxWorks task exit
    handlers behaved strangely if CA functions were called from the
    vxWorks shell, {external+epics-base:cpp:func}`ca_task_exit` wasn't called,
    and the vxWorks shell restarted.
    In EPICS R3.14 vxWorks task exit handlers are not installed and therefore
    cleanup is solely the responsibility of the user.
    With EPICS R3.14 the user must call {external+epics-base:cpp:func}`ca_context_destroy`
    or {external+epics-base:cpp:func}`ca_task_exit()` to clean up on vxWorks.
    This is the same behavior as on all other OS.

## Calling CA Functions from POSIX signal handlers

As you might expect, it isn't safe to call the CA client library from a
POSIX signal handler. Likewise, it isn't safe to call the CA client
library from interrupt context.
