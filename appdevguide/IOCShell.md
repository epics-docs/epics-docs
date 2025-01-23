# IOC Shell

## Introduction

The EPICS IOC shell is a simple command interpreter
which provides a subset of the capabilities of the vxWorks shell.
It is used to interpret startup scripts (st.cmd)
and to execute commands entered at the console terminal.
In most cases vxWorks startup scripts can be interpreted
by the IOC shell without modification.
The following sections of this chapter describe the operation
of the IOC shell from the user's and programmer's points of view.

## IOC Shell Operation

The IOC shell reads lines of input,
expands environment variable parameters,
breaks the line into commands and arguments
then calls functions corresponding to the decoded command.
Commands and arguments are separated by one or more \`space\' characters.
Characters interpreted as spaces include the actual space character
and the tab character
as well as commas
and open and close parentheses.
Thus,
the command line

    dbLoadRecords("db/dbExample1.db","user=mrk")

would be interpreted by the IOC shell
as the `dbLoadRecords` command
with arguments `db/dbExample1.db` and `user=mrk`.

Unrecognized commands result in a diagnostic message
but are otherwise ignored.
Missing arguments are given a default value
(0 for numeric arguments, NULL for string arguments).
Extra arguments are ignored.

Unlike the vxWorks shell,
string arguments do not have to be enclosed in quotes
unless they contain one or more of the space characters,
in which case one of the quoting mechanisms
described in the following section
must be used.

### Environment variable expansion

Lines of input not beginning with a comment character (`#`) are searched
for macro references in the form \${name} or \$(name).
The documentation for the macLib facility (chapter 19) describes some possible syntax variations
for macro references.
Such references are replaced with the value of the environment variable they name
before any other processing takes place.
Macro expansion is recursive so,
for example,

    epics> epicsEnvSet v1 \${v2}
    epics> epicsEnvSet v2 \${v3}
    epics> epicsEnvSet v3 somePV
    epics> dbpr ${v1}

will print information about the `somePV` process variable -
the `${v1}` argument to the dbpr command expands to `${v2}`
which expands to `${v3}`
which expands to `somePV`.
The backslashes in the definitions are needed
to postpone the substitution of the following variables,
which would otherwise be performed before the `epicsEnvSet` command was run.

Macro references that appear inside single-quotes are not expanded.

### Quoting

Quoting is used to remove the special meaning
normally assigned to certain characters
and can be used to include space or quote characters in arguments.
Quoting takes place after the macro expansion described above has been performed,
and cannot be used to extend a command over more than one input line.

There are three quoting mechanisms:
the backslash character,
single quotes,
and double quotes.
A backslash (\\) preserves the literal value
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
as well as easy access to previous commands
through the command-line history capabilties provided by these libraries.
For full details,
refer to the readline or tecla library documentation.
Command and argument completion is not supported.

If neither the readline nor tecla library is used
the only command-line editing and history capabilities will be those supplied
by the underlying operating system.
The console keyboard driver in Windows,
for example,
provides its own command-line editing and history commands.
On vxWorks the ledLib command-line input library routines are used.

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
(i.e. with no command)
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

### Utility Commands

The IOC shell recognizes the following commands
as well as the commands described in chapter 6 (Database Definition)
and chapter 9 (IOC Test Facilities) among others.
The commands described in the sequencer documentation will also be recognized
if the sequencer is included.

| Command | Description |
|:---|:---|
| help \[command ...\] | Display synopsis of specified commands. Wild-card matching is applied so \`help db\*' displays a synopsis of all commands beginning with the letters \`db'. With no arguments this displays a list of all commands. |
| \# | A \`#' as the first non-whitespace character on a line marks the beginning of a comment, which continues to the end of the line (however some versions of Base may require a space after the \`#' character to properly recognize it as a comment) |
| exit | Stop reading commands. When the top-level command interpreter encounters an exit command or end-of-file (EOF) it returns to its caller. |
| cd directory | Change working directory to directory. |
| pwd | Print the name of the working directory. |
| var \[name \[value\]\] | If both arguments are present, assign the value to the named variable.If only the name argument is present, print the current value of that variable.If neither argument is present, print the value of all variables registered with the shell. Variables are registered in application database definitions using the variable keyword as described in Section6.9 on page104. |
| show \[-level\] \[task ...\] | Show information about specified tasks. If no task arguments are present, show information on all tasks. The level argument controls the amount of information printed. The default level is 0. The task arguments can be task names or task i.d. numbers. |
| system command_string | Send command_string to the system command interpreter for execution. This command is present only if some application database definition file contains registrar(iocshSystemCommand) and if the system provides a suitable command interpreter (vxWorks does not). |
| epicsEnvSet name value | Set environment variable name to the specified value. |
| epicsEnvShow \[name\] | If no name is specified the names and values of all environment variables will be shown. If a name is specified the value of that environment variable will be shown. |
| epicsParamShow | Show names and values of all EPICS configuration parameters. |
| iocLogInit | Initialize IOC logging. |
| epicsThreadSleep sec | Pause execution of IOC shell for sec seconds. |

The `var` command is intended for simple applications
such as setting the value of debugging flags.
Applications which require more complex expression handling
should use the cexp package.

A `spy` command to show periodic activity reports is available on RTEMS
as part of the RTEMS_UTILS support module.
The following changes must be made to add this command to an application.

-   Add an RTEMS_UTILS entry to the application configure/RELEASE file.
-   Add `spy.dbd` to the list of application dbd files and `rtemsutils`
    to the list of application libraries in the application Makefile.

### Environment Variables

The IOC shell uses the following environment variables to control its
operation.

| Variable | Description |
|:---|:---|
| IOCSH_PS1 | Prompt string. Default is \`\`epics\> ''. |
| IOCSH_HISTSIZE | Number of previous command lines to remember. If the IOCSH_HISTSIZE environment variable is not present the value of the HISTSIZE environment variable is used. In the absence of both environment variables, 10 command lines will be remembered. |
| TERM, INPUTRC | These and other environment variables are used by the readline and termcap libraries and are described in the documentation for those libraries. |

### Conditionals

The IOC shell does not provide operaters
for conditionally executing commands
but the effect can be simulated using macro expansion.
The simplest technique is to preceed a command with a macro
that expands to either \``#`\' or \`\' (or \` \').
The following startup script line shows how this can be done:

    ...
    $(LOAD_DEBUG=#) $(DEBUG) dbLoadRecords("db/debugRec.db", "P=$(P),R=debug")
    ...

Starting the IOC in the normal fashion
will result in the above line being commented out
and the debugRec.db file being omitted:

    ./st.cmd

Setting the `LOAD_DEBUG` environment variable to an empty string
before starting the IOC will result in the debugRec.db file being loaded:

    LOAD_DEBUG="" ./st.cmd

A similar technique can be used to execute external scripts conditionally.
The startup command file contains code like:

    epicsEnvSet PILATUS_ENABLED "$(PILATUS_ENABLED=NO)"
    ...
    < pilatus-$(PILATUS_ENABLED).cmd

with one set of conditional code in a file named pilatus-YES.cmd
and the other set of conditional code in a file named pilatus-NO.cmd
This technique can be expanded to a form similar to a C \`switch\' statement
for the example above by providing additional pilatus-*XXX*.cmd scripts.

## IOC Shell Programming

The declarations described in this section are included in the `iocsh.h`
header file.

### Invoking the IOC shell

The prototypes for calling the IOC shell command interpreter are:

    int iocsh(const char *pathname);
    int iocshCmd(const char *cmd);

The pathname argument to the `iocsh` function is the name of the file
from which commands are to be read.
If the pathname argument is NULL,
commands are read from the standard input
and prompts are issued to the standard output.
Commands are read until an `exit` command is encountered
or until end-of-file is reached,
at which point iocsh returns a value of 0.
If the specified file can not be opened iocsh returns -1.

The IOC shell can be invoked from the vxWorks shell,
either from within a vxWorks startup script
or from vxWorks command-line interpreter,
using

    iocsh "script"

to read from an IOC shell script.
It can also be invoked from the vxWorks command-line interpreter with no argument,
in which case the IOC shell takes over the duties
of command-line interaction.

The `iocshCmd` function takes a single IOC shell command
and executes it.
The function may be called from any thread,
but many of the commands are not necessarily thread-safe
so this should only be used with care.
The function is most useful to execute a single IOC shell command
from a vxWorks startup script or command line,
like this:

    iocshCmd "iocsh command string"

The stdio stream redirection
and environment variable expansion processes described above
are performed on the string
as part of the execution process.

### Registering Commands

Commands must be registered before they can be recognized by the IOC shell.
Registration is achieved by calling the registration function:

    void iocshRegister(const iocshFuncDef *piocshFuncDef, iocshCallFunc func);

The first argument is a pointer to a data structure
which describes the command and any arguments it may take.
The second argument is a pointer to a function
which will be called by iocsh
when the corresponding command is encountered.

The command is described by the `iocshFuncDef `structure:

    struct iocshFuncDef {
        const char *name;
        int nargs;
        const iocshArg * const *arg;
    };

The name element is the name of the command.
The arg element is a pointer to an array of pointers to structures
each of which defines a single argument.
The nargs element declares the number of entries
in the array of pointers
to the argument descriptions.
If nargs is zero,
arg can be NULL.
The structures which define each of the arguments is:

    struct iocshArg {
        const char *name;
        iocshArgType type;
    }iocshArg;

The name element is used by the help command
to print a synopsis for the command.
The type element describes the type of the argument
and takes one of the following values:

| Type Specifier | Description |
|:---|:---|
| iocshArgInt | The argument will be converted to an integer value. |
| iocshArgDouble | The argument will be converted to a double-precision floating point value. |
| iocshArgString | The argument will be left as a string. The memory used to hold the string is \`owned' by iocsh and will be reused once the handler function returns. |
| iocshArgPersistentString | A copy of the argument will be made and a pointer to the copy will be passed to the handler. The called function can release this copy by using the pointer as an argument to free(). |
| iocshArgPdbbase | The argument must be pdbbase. |
| iocshArgArgv | An arbitrary number of arguments is expected. Subsequent iocshArg structures will be ignored. |

The \`handler\' function which is called when its corresponding command
is recognized should be of the form:

    void showCallFunc(const iocshArgBuf *args);

The argument to the handler function is a pointer to an array of unions.
The number of elements in this array is equal to the number of arguments
specified in the structure describing the command.
The type and name of the union element
which contains the argument value
depends on the \`type\' element
of the corresponding argument descriptor:

| Type Specifier           | Type      | Union element     |
|:-------------------------|:----------|:------------------|
| iocshArgInt              | int       | args\[i\].ival    |
| iocshArgDouble           | double    | args\[i\].dval    |
| iocshArgString           | char \*   | args\[i\].sval    |
| iocshArgPersistentString | char \*   | args\[i\].sval    |
| iocshArgPdbbase          | void \*   | args\[i\].vval    |
| iocshArgArgv             | int       | args\[i\].aval.ac |
|                          | char \*\* | args\[i\].aval.av |

If an `iocshArgArgv `argument type is present
it is often the first and only argument specified for the command.
In this case,
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

    #include <iocsh.h>
    #include <epicsExport.h>

    /* drvXxx code, FuncDef and CallFunc definitions ... */

    static void drvXxxRegistrar(void)
    {
        iocshRegister(&drvXxxConfigureFuncDef, drvXxxConfigureCallFunc);
    }
    epicsExportRegistrar(drvXxxRegistrar);

To include this driver in an application a developer would then add

    registrar(drvXxxRegistrar)

to an application database description file.

#### Automatic Command Registration

A C++ static constructor can also be used
to register IOC shell commands
before the EPICS application begins.
The following example shows how the `epicsThreadSleep` command
could be described and registered.

    #include <iocsh.h>

    static const iocshArg epicsThreadSleepArg0 = { "seconds",iocshArgDouble};
    static const iocshArg *const epicsThreadSleepArgs=
        {&epicsThreadSleepArg0};
    static const iocshFuncDef epicsThreadSleepFuncDef =
        {"epicsThreadSleep",1,epicsThreadSleepArgs};
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
