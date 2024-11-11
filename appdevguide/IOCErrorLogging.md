# IOC Error Logging

See {external+epics-base::doc}`errlog_h` for up-to-date API information.

(err-log-overview)=
## Overview 

EPICS error logging system consists of functions for passing error messages and the [iocLog client and server](ioclog-chapter). 
Error logging functions support generating messages with varying severity, registering and un-registering listeners 
and modifying the log buffer size and max message size.

Errors detected by an IOC can be divided into classes:
Errors related to a particular client and errors not attributable to a particular client.
An example of the first type of error is an illegal Channel Access request.
For this type of error, a status value should be passed back to the client.
An example of the second type of error is a device driver detecting a hardware error.
This type of error should be reported to a system wide error handler.

Dividing errors into these two classes is complicated by a number of factors.

  - In many cases it is not possible for the routine detecting an error to decide which type of error occurred.

  - Normally, only the routine detecting the error knows how to generate a fully descriptive error message.
    Thus, if a routine decides that the error belongs to a particular client and merely returns an error status value, the ability to generate a fully descriptive error message is lost.

  - If a routine always generates fully descriptive error messages then a particular client could cause error message storms.

  - While developing a new application the programmer normally prefers fully descriptive error messages.
    For a production system, however, the system wide error handler should not normally receive error messages cause by a particular client.


If used properly, the error handling facilities described in this chapter can process both types of errors.

This chapter describes the following:

  - [Error Message Generation Routines](#error-message-routines) - Routines which pass messages to the errlog Task.

  - [Error Log Listeners](#errlog-listeners) - Any code can register to receive errlog messages.

  - [errlogThread](#errlogthread) - A thread that passes the messages to all registered listeners.

  - Messages can also be written to the console. 
    [The storage for the message queue](#console-output-and-message-queue-size) can be specified by the user.

  - [status codes](#status-codes) - EPICS status codes.

  - [iocLog](#ioclog), a system wide error logger supplied with base.
    It writes all messages to a system wide file.


```{note}
`recGbl` error routines are also provided.
They in turn call one of the error message routines.
```
## Error Message Routines

### Basic Routines

- {external+epics-base:cpp:func}`errlogPrintf`
- {external+epics-base:cpp:func}`errlogVprintf`
- {external+epics-base:cpp:func}`errlogMessage`
- {external+epics-base:cpp:func}`errlogFlush`

`errlogPrintf` and  `errlogVprintf` are like [`printf`](https://cplusplus.com/reference/cstdio/printf/) and 
[`vprintf`](https://cplusplus.com/reference/cstdio/vprintf) provided by the standard C library, except that their output is sent to the errlog task; unless configured not to, the output will appear on the console as well.
Consult any book that describes the standard C library such as "The C Programming Language ANSI C Edition" by Kernighan and Ritchie.

`errlogMessage` sends message to the errlog task.

`errlogFlush` wakes up the errlog task and then waits until all messages are flushed from the queue.

### Log with Severity

Errlog severities: {external+epics-base:cpp:enum}`errlogSevEnum`

- {external+epics-base:cpp:func}`errlogSevPrintf`
- {external+epics-base:cpp:func}`errlogSevVprintf`
- {external+epics-base:cpp:func}`errlogGetSevEnumString`
- {external+epics-base:cpp:func}`errlogSetSevToLog`
- {external+epics-base:cpp:func}`errlogGetSevToLog`

`errlogSevPrintf` and `errlogSevVprintf` are like `errlogPrintf` and  `errlogVprintf` except that they add the severity to the beginning of the message in the form `sevr=<value>` where value is one of `[info, minor, major, fatal]`.
Also the message is suppressed if  severity is less than the current severity to suppress.
If `epicsThreadIsOkToBlock` is true, which is true during iocInit, `errlogSevVprintf` does NOT send output to the errlog task.

`errlogGetSevEnumString` gets the string value of severity.

`errlogSetSevToLog` sets the severity to log.
`errlogGetSevToLog` gets the current severity to log.

### Status Routines

- {external+epics-base:c:macro}`errMessage`
- {external+epics-base:cpp:func}`errPrintf`

Routine `errMessage` is actually a macro that calls `errPrintf` 

The calling routine is expected to pass a descriptive message to this routine.
Many subsystems provide routines built on top of `errMessage` which generate descriptive messages.

An IOC global variable `errVerbose`, defined as an `external` in `errMdef.h`, specifies verbose messages.
If `errVerbose` is `TRUE` then `errMessage` should be called whenever an error is detected even if it is known that the error belongs to a specific client.
If `errVerbose` is `FALSE` then `errMessage` should be called only for errors that are not caused by a specific client.

An EPICS status code can also be converted to a string.

See {external+epics-base:cpp:func}`errSymLookup`.

If the supplied status code isn't registered in the status code database then the raw status code number is converted into a string in the destination buffer.

### Obsolete Routines

- {external+epics-base:c:macro}`epicsPrintf`
- {external+epics-base:c:macro}`epicsVprintf`

### errlog Listeners

Any code can receive errlog message.
The following are the calls to add and remove a listener.

- {external+epics-base:cpp:type}`errlogListener` (function type)
- {external+epics-base:cpp:func}`errlogAddListener`
- {external+epics-base:cpp:func}`errlogRemoveListeners`

These routines add/remove a callback that receives each error message.
These routines are the interface to the actual system wide error handlers.

## errlogThread

The error message routines can be called by any non-interrupt level code.
These routines pass the message to the errlog thread.
If any of the error message routines are called at interrupt level, `epicsInterruptContextMessage` is called with the message "errlogPrintf called from interrupt level".

`errlogThread` manages the messages.
Messages are placed in a message queue, which is read by errlogThread.
The message queue uses a fixed block of memory to hold all messages.
When the message queue is full additional messages are rejected but a count of missed messages is kept.
The next time the message queue empties an extra message about the missed messages is generated.

The maximum message size is by default 256 characters.
If a message is longer, the message is truncated and a message explaining that it was truncated is appended.
There is a chance that long messages corrupt memory.
This only happens if client code is defective.
Long messages most likely result from `%s` formats with a bad string argument.

errlogThread passes each message to any registered listener.

## Console output and message queue size

The errlog system can also display messages on the ioc console.
It calls {external+epics-base:cpp:func}`epicsThreadIsOkToBlock` to decide when to display the message.
If it is OK to block, the message is displayed by the same thread that calls one of the errlog print routines.
If it is not OK to block, errlogThread displays the messages.

Normally the errlog system displays all messages on the console.
`eltc` can be used to suppress these messages.

- {external+epics-base:cpp:func}`eltc`
- {external+epics-base:cpp:func}`errlogInit`
- {external+epics-base:cpp:func}`errlogInit2`

eltc determines if errlog task writes message to the console.
During error message storms this command can be used to suppress console messages.
A argument of 0 suppresses the messages, any other value lets messages go to the console.

`errlogInit` or `errlogInit2` can be used to initialize the error logging system 
with a larger buffer and maximum message size.

## Status codes

EPICS defined status values provide the following features:

- Whenever possible, IOC routines return a status value: 0 means OK, non-0 means an error.
- The header files for most IOC subsystems contain macros defining error status symbols and strings.
- Routines are provided for run time access of the error status symbols and strings.
- A global variable `errVerbose` helps code decide if error messages should be generated.

IOC routines often return a [long integer](https://en.wikipedia.org/wiki/Integer_(computer_science)#Long_integer)
status value, encoded similar to vxWorks error status encoding.
On some modern architectures a long integer is more than 32 bits wide, but in order to keep the API compatible the status values are still passed as long integers, even though only 32 bits are ever used.
The most significant 16 bits indicate the subsystem or module where the error occurred.
The least significant 16 bits contain a subsystem-specific status value.
In order that status values do not conflict with the vxWorks error status values, all subsystem numbers are greater than 500.

A header file `errMdef.h` defines macros for all the subsystem numbers.
For example the database access routines use this module number:

`#define M_dbAccess  (511 << 16)   /*Database Access Routines*/`

There are header files for every IOC subsystem that returns standard status values.
The status values are encoded with lines of the following format:

`#define S_xxxxxxx value /*string value*/`

For example:

`#define S_dbLib_recNotFound (M_dbLib|5)        /* Record Not Found */`

For example, when {external+epics-base:cpp:func}`dbFindRecordPart` cannot find a record, it executes the statement:

`return S_dbLib_recNotFound;`

The calling routine checks the return status as follows:

```
status = dbGetField(...);
if(status) {/* Call was not successful */ }
```
(ioclog-chapter)=
## iocLog

IOC logging comprises two modules:
`iocLogServer` and `iocLogClient`.

See {external+epics-base::doc}`logClient_h` for up-to-date API information.

The client code runs on each IOC and listens for the messages generated locally by the [errlog](#err-log-overview) system.
It also reports the messages from the vxWorks logMsg facility.

### iocLogServer

```{note}
 iocLogServer is still supplied with EPICS Base but **deprecated**. Consider using other logging servers (e.g. [Logstash](https://www.elastic.co/logstash) or [Graylog](https://graylog.org/) instead.
```
This runs on a host.
It receives messages for all enabled iocLogClients in the local area network.
The messages are written to a file.

To start a log server on a UNIX or PC workstation you must first set the following environment variables and then run the executable `iocLogServer` on your PC or UNIX workstation.

{external+epics-base:cpp:member}`EPICS_IOC_LOG_FILE_NAME`

The name and path to the log file.

{external+epics-base:cpp:member}`EPICS_IOC_LOG_FILE_LIMIT`

The maximum size in characters for the log file.
If the file grows larger than this limit the server will seek back to the beginning of the file and write new messages over the old messages starting from the beginning.
If the value is zero then there is no limit on the size of the log file.

{external+epics-base:cpp:member}`EPICS_IOC_LOG_FILE_COMMAND`

A shell command string used to obtain the log file path name during initialization and in response to SIGHUP.
The new path name will replace any path name supplied in `EPICS_IOC_LOG_FILE_NAME`.

Thus, if `EPICS_IOC_LOG_FILE_NAME` is `a/b/c.log` and `EPICS_IOC_LOG_FILE_COMMAND` returns `A/B` or `A/B/` the log server will be stored at `A/B/c.log`.

If `EPICS_IOC_LOG_FILE_COMMAND`` is empty then this behavior is disabled.
This feature is used at some sites for switching the server to a new directory at a fixed time each day.
This variable is currently used only by the UNIX version of the log server.

{external+epics-base:cpp:member}`EPICS_IOC_LOG_PORT`

THE TCP/IP port used by the log server.

To configure an IOC to log its messages it must have an environment variable `EPICS_IOC_LOG_INET` set to the IP address of the host that is running the log server, and `EPICS_IOC_LOG_PORT` to the TCP/IP port used by the log server.

Defaults for all of the above parameters are specified in  the files `$(EPICS_BASE)/config/CONFIG_SITE_ENV` and `$(EPICS_BASE)/config/CONFIG_ENV`.

### iocLogClient

Client on the IOC that forwards log messages to the log server.

Together with the program iocLogServer, a log client provides generic support for logging text messages from an IOC or other program to the log server host machine. 

{external+epics-base:cpp:func}`logClientCreate`

The global variable `iocLogDisable` can be used to enable/disable the messages from being sent to the server.
Setting this variable to (0,1) (enables, disables) the messages generation.
If `iocLogDisable` is set to 1 before calling `iocLogInit` then `iocLogClient` will not even initialize itself.
`iocLogDisable` can also be changed to turn logging on or off.

`iocLogClient` calls `errlogAddListener` and sends each message to the `iocLogServer|.

### Configuring a Private Log Server

In a testing environment it is desirable to use a private log server.
This can be done with an epicsEnvSet commmand in your IOC startup file:

`epicsEnvSet("EPICS_IOC_LOG_INET=xxx.xxx.xxx.xxx")`

The inet address is that of your host workstation.
On your host workstation, start the log server.

### iocLogPrefix

Many sites run multiple soft IOCs on the same machine.
With some log viewers like cmlogviewer it is not possible to distinguish between the log messages from these IOCs since their hostnames are all the same.
One solution to this is to add a unique prefix to every log message.

The {external+epics-base:cpp:func}`iocLogPrefix` command can be run from the startup file during IOC initialization to establish such a prefix that will be prepended to every log message when it is sent to the iocLogServer.

For example, adding the following lines to your `st.cmd` file 

```
epicsEnvSet("IOC","sioc-b34-mc10");
iocLogPrefix("fac=LI21 proc=${IOC} ");
```

will categorize all log messages from this IOC as belonging to the facility `LI21` and to the process `sioc-b34-mc10`.

Note that log messages echoed to the IOC's standard output will not show the prefix, 
it only appears in the version sent to the log server.
`iocLogPrefix` should appear fairly early in the startup script so 
the IOC doesn't try to send any log messages without the prefix.
Once the prefix has been set, it cannot be changed without rebooting the IOC.
One can determine if a log prefix has been set using `logClientShow`.
