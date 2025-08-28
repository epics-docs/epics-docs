# IOC shell

## Introduction

The EPICS IOC shell is a command interpreter
which provides a subset of the capabilities of the VxWorks shell.
It is used to interpret startup scripts (`st.cmd`)
and to run commands entered at the console terminal.
In most cases,
the IOC shell can interpret VxWorks startup scripts
without modification.
The following sections of this chapter describe the operation
of the IOC shell from the user's and programmer's points of view.

## IOC shell operation

The IOC shell reads lines of input,
expands environment variable parameters,
breaks the line into commands and arguments
then calls functions corresponding to the decoded command.
Commands and arguments are separated by one or more "space" characters.
Characters interpreted as spaces include the actual space character,
the tab character,
commas,
and open and close parentheses.

Thus,
the IOC shell would interpret the following command line

```{code-block} csh
dbLoadRecords("db/dbExample1.db","user=mrk")
```

as the `dbLoadRecords` command
with arguments `db/dbExample1.db` and `user=mrk`.

Unrecognized commands result in a diagnostic message
but are otherwise ignored.
Missing arguments are given a default value
(0 for numeric arguments, `NULL` for string arguments).
Extra arguments are ignored.

Unlike the VxWorks shell,
string arguments do not have to be inside quotes
unless they contain one or more of the space characters.
In that case,
one of the quoting mechanisms
described in the following section
must be used.

### Environment variable expansion

Lines of input not beginning with a comment character (`#`) are searched
for macro references in the form `${name}` or `$(name)`.

The documentation for the `macLib` facility describes some possible syntax variations
for macro references.
Such references are replaced with the value of the environment variable they name
before any other processing takes place.
Macro expansion is recursive so,
for example

```{code-block} csh
epics> epicsEnvSet v1 \${v2}
epics> epicsEnvSet v2 \${v3}
epics> epicsEnvSet v3 somePV
epics> dbpr ${v1}
```

prints information about the `somePV` process variable:
the `${v1}` argument to the `dbpr` command expands to `${v2}`
which expands to `${v3}`
which expands to `somePV`.

The backslashes in the definitions are needed
to postpone the substitution of the following variables,
which would otherwise be performed before the `epicsEnvSet` command is run.

Macro references that appear inside single-quotes are not expanded.

### Quoting

Quoting is used to remove the special meaning
normally assigned to certain characters
and can be used to include space or quote characters in arguments.

Quoting takes place after the macro expansion described earlier has been performed,
and cannot be used to extend a command over more than one input line.

There are three quoting mechanisms:
the backslash character,
single quotes,
and double quotes.

A backslash (`\`) preserves the literal value
of the following character.
Enclosing characters in single or double quotes preserves the literal value
of each character (including backslashes)
within the quotes.

A single quote may occur between double quotes
and a double quote may occur between single quotes.
Note that commands called from the shell may perform additional unescaping
and macro expansion on their argument strings.

### Command-line editing and history

The IOC shell can use the readline or tecla library
to obtain input from the console terminal.
This provides full command-line editing
and quick access to previous commands
through the command-line history capabilities provided by these libraries.
For full details,
refer to the readline or tecla library documentation.

If neither the readline nor tecla library is used
the only command-line editing and history capabilities will be those supplied
by the underlying operating system.
The console keyboard driver in Windows,
for example,
provides its own command-line editing and history commands.
On VxWorks the ledLib command-line input library routines are used.

### Redirection

The IOC shell recognizes a subset of UNIX shell I/O redirection operators.
The redirection operators may precede,
or appear anywhere within,
or follow a command.
Redirections are processed in the order they appear,
from left to right.
Failure to open or create a file causes the redirection to fail
and the command to be ignored.

Redirection of input causes the file
whose name results from the expansion of `filename`
to be opened for reading on file descriptor `n`,
or the standard input (file descriptor 0)
if `n` is not specified.
The general format for redirecting input is:

    [n]<filename

As a special case,
the IOC shell recognizes a standard input redirection appearing by itself
(that is, with no command)
as a request to read commands from `filename`
until an exit command or EOF is encountered.

The IOC shell then resumes reading commands from the current source.
Commands read from `filename` are not added to the readline command history.
The level of nesting is limited only
by the maximum number of files that can be open simultaneously.

Redirection of output causes the file
whose name results from the expansion of `filename`
to be opened for writing on file descriptor `n`,
or the standard output (file descriptor 1)
if `n` is not specified.

If the file does not exist it is created;
if it does exist it is truncated to zero size.
The general format for redirecting output is:

    [n]>filename

The general format for appending output is:

    [n]>>filename

Redirection of output in this fashion causes the `filename`
to be opened for appending on file descriptor `n`,
or the standard output (file descriptor 1)
if `n` is not specified.
If the file does not exist it is created.

### Utility commands

The IOC shell recognizes the following commands
as well as the commands described in {doc}`databaseDefinition`
and {doc}`IOCTestFacilities` among others.
The commands described in the sequencer documentation will also be recognized
if the sequencer is included.

:::{describe} help [command ...]
Display synopsis of specified commands.
Wild-card matching is applied so `help db*` displays a synopsis
of all commands beginning with the letters `db`.
With no arguments this displays a list of all commands.
:::

::::{describe} #
A `#` as the first non-whitespace character on a line
marks the beginning of a comment,
which continues to the end of the line.

:::{note}
Older versions of EPICS Base may require a space after the `#` character
to recognize it as a comment.
:::
::::

:::{describe} exit
Stop reading commands.
When the top-level command interpreter encounters an exit command
or end-of-file (EOF) it returns to its caller.
:::

:::{describe} cd directory
Change working directory to `directory`.
:::

:::{describe} pwd
Print the name of the working directory.
:::

:::{describe} var [variable [value]]
Print all,
print a single variable,
or set value to single variable.

:(default): print all variables and their values defined in database definitions files
:variable: if only parameter, print value for this variable
:value: set the value to variable

Variables are registered in application Database Definitions
using the `variable` keyword.
See {ref}`dbd-variable` in the Database Definition reference
for more information.
:::

:::{describe} epicsThreadShow [-level] [thread ...]
Show information about the specified threads.
If no thread arguments are present,
show information on all threads.
The level argument controls the amount of information printed.
The default level is 0.
The thread arguments can be thread names or thread i.d. numbers.
:::

::::{describe} system command_string
Send `command_string` to the system command interpreter for execution.

To enable this command,
add `registrar(iocshSystemCommand)` to an application dbd file,
or include `system.dbd`.

:::{warning}
This command isn't available on all OSes:
this command is present only
if the system provides a suitable command interpreter
(VxWorks does not).
:::
::::

:::{describe} epicsEnvSet name value
Set environment variable name to the specified value.
:::

:::{describe} epicsEnvShow [name]
If `name` isn't specified
the names and values of all environment variables will be shown.
If `name` is specified the value of that environment variable will be shown.
:::

:::{describe} epicsParamShow
Show names and values of all EPICS configuration parameters.
:::

:::{describe} iocLogInit
Initialize IOC logging.
:::

:::{describe} epicsThreadSleep sec
Pause execution of IOC shell for sec seconds.
:::

### Environment variables

The IOC shell uses the following environment variables to control its
operation.

:::{envvar} IOCSH_PS1
Prompt string.
Default is `epics>`.
:::

:::{envvar} IOCSH_HISTSIZE
Number of previous command lines to remember.
If the `IOCSH_HISTSIZE` environment variable is not present
the value of the `HISTSIZE` environment variable is used.
In the absence of both environment variables,
10 command lines will be remembered.
:::

Other environment variables such as `TERM` and `INPUTRC`
are used by the readline and termcap libraries
and are described in the documentation for those libraries.

### Conditionals

The IOC shell does not provide operators
for conditionally executing commands
but the effect can be achieved by using macro expansion.
The simplest technique is to precede a command with a macro
that expands to either `#` or the empty string (or a space).

The following startup script line shows how this can be done:

```{code-block} csh
...
$(LOAD_DEBUG="#") $(DEBUG) dbLoadRecords("db/debugRec.db", "P=$(P),R=debug")
...
```

Starting the IOC in the normal fashion
will comment the line above
and omit loading the `debugRec.db` file:

```{code-block} bash
./st.cmd
```

Setting the `LOAD_DEBUG` environment variable to an empty string
before starting the IOC will load the `debugRec.db` file:

```{code-block} bash
LOAD_DEBUG="" ./st.cmd
```

A similar technique can be used to run external scripts conditionally.
The startup command file contains code like:

```{code-block} csh
epicsEnvSet PILATUS_ENABLED "$(PILATUS_ENABLED=NO)"
...
< pilatus-$(PILATUS_ENABLED).cmd
```

with one set of conditional code in a file named `pilatus-YES.cmd`
and the other set of conditional code in a file named `pilatus-NO.cmd`

This technique can be expanded to a form similar to a C `switch` statement
for the example above by providing additional {samp}`pilatus-{XXX}.cmd` scripts.

## IOC shell programming

The declarations described in this section are included in the `iocsh.h`
header file.

### Invoking the IOC shell

The prototypes for calling the IOC shell command interpreter are:

- {external+epics-base:cpp:func}`iocsh`
- {external+epics-base:cpp:func}`iocshLoad`
- {external+epics-base:cpp:func}`iocshCmd`
- {external+epics-base:cpp:func}`iocshRun`

See their documentation for more usage information.

The IOC shell can be invoked from the vxWorks shell,
either from within a vxWorks startup script
or from vxWorks command-line interpreter,
using

```{code-block} csh
iocsh "script"
```

to read from an IOC shell script.

It can also be invoked from the vxWorks command-line interpreter with no argument,
in which case the IOC shell takes over the duties
of command-line interaction.

The `iocshCmd` function is most useful to run a single IOC shell command
from a VxWorks startup script or command line,
like this:

```{code-block} csh
iocshCmd "iocsh command string"
```

### Registering Commands

Commands must be registered before they can be recognized by the IOC shell.
Registration is achieved by calling the registration function
{external+epics-base:cpp:func}`iocshRegister`:

```{code-block} c
:caption: Example

#include <epicsExport.h>
#include <iocsh.h>

// Implementation of the command
static void myIOCCommand(const iocshArgBuf* args) {
	const char *arg0 = args[0].sval;
	int arg1 = args[1].ival;

	// ...
}

// Description of the command

// First argument
static const iocshArg myIOCCommandArg0 = {
    .name = "Port Name",
    .type = iocshArgString,
};

// Second argument
static const iocshArg myIOCCommandArg1 = {
    .name = "Number Devices",
    .type = iocshArgInt,
};

// All arguments
static const iocshArg* const myIOCCommandArgs[] = {
    &myIOCCommandArg0,
    &myIOCCommandArg1,
};

// Full description
static const iocshFuncDef myIOCCommandFuncDef = {
    .name = "my-ioc-command",
    .nargs = 2,
    .arg = myIOCCommandArgs,
    .usage = "Helpful help message."
};

// Registrar
static void myRegistrar(void) {
    iocshRegister(&myIOCCommandFuncDef, &myIOCCommand);
}

epicsExportRegistrar(myRegistrar);
```

See these documentation sections for more information:

{external+epics-base:cpp:func}`iocshRegister`
: For registering the IOC shell command.

{external+epics-base:cpp:struct}`iocshFuncDef`
: For defining the command arguments

{external+epics-base:cpp:struct}`iocshArg`
: For defining a single command argument

{external+epics-base:cpp:enum}`iocshArgType`
: For specifying the type of a command argument

{external+epics-base:cpp:union}`iocshArgBuf`
: For getting the arguments in the implementation

The "handler" function which is called
when its corresponding command is recognized
should be of the form:

```cpp
void myIOCCommand(const iocshArgBuf *args);
```

The argument to the handler function points to an array of unions.
The number of elements in this array is equal to the number of arguments
specified in the structure describing the command.

The type and name of the union element
which contains the argument value
depends on the `type` element
of the corresponding argument descriptor.
See {external+epics-base:cpp:union}`iocshArgBuf`
for more information.

If an {external+epics-base:cpp:enumerator}`iocshArgArgv` argument type is present
it is often the first and only argument specified for the command.
In this case,
`args[0].aval.ac` will be the number of arguments passed,
`args[0].aval.av[0]` will be the name of the command,
`args[0].aval.av[1]` will be the first argument, and so on.

### Registrar Command Registration

Commands are normally registered with the IOC shell
in a registrar function.
The application's database description file uses the `registrar` keyword
to specify a function
which will be called from the EPICS initialization code
during the application startup process.
This function then calls `iocshRegister`
to register its commands with the iocsh.

The following code fragments shows how this can be performed
for an example driver.

```{code-block} c
#include <iocsh.h>
#include <epicsExport.h>

/* drvXxx code, FuncDef and CallFunc definitions ... */

static void drvXxxRegistrar(void)
{
    iocshRegister(&drvXxxConfigureFuncDef, drvXxxConfigureCallFunc);
}
epicsExportRegistrar(drvXxxRegistrar);
```

To include this driver in an application a developer would then add

```{code-block} csh
registrar(drvXxxRegistrar)
```

to an application database description file.

#### Automatic Command Registration

A C++ static constructor can also be used
to register IOC shell commands
before the EPICS application begins.
The following example shows how the `epicsThreadSleep` command
could be described and registered.

```{code-block} cpp
#include <iocsh.h>

static const iocshArg epicsThreadSleepArg0 = {
    .name = "seconds",
    .type = iocshArgDouble,
};
static const iocshArg *const epicsThreadSleepArgs= {
    &epicsThreadSleepArg0,
};
static const iocshFuncDef epicsThreadSleepFuncDef = {
    .name = "epicsThreadSleep",
    .nargs = 1,
    .arg = epicsThreadSleepArgs,
    .usage = "Pause execution of IOC shell for <seconds> seconds\n";
};
static void epicsThreadSleepCallFunc(const iocshArgBuf *args)
{
    epicsThreadSleep(args[0].dval);
}

static int doRegister(void)
{
    iocshRegister(epicsThreadSleepFuncDef, epicsThreadSleepCallFunc);
    return 1;
}
static int done = doRegister();
```
