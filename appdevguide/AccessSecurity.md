# IOC Access Security


## Features

Access security protects IOC databases from unauthorized Channel Access
or pvAccess Clients. Access security is based on the following:

 **Who**

   User id of the client (Channel Access/pvAccess). With pvAccess, it is also possible to define user groups that have a specified role. See below for more details.

**Where**

   Host id where the user is logged on. This is the host on which the
   client runs. No attempt is made to see if a
   user is local or is remotely logged on to the host.

**What**

   Individual fields of records are protected. Each record has a field
   containing the Access Security Group (ASG) to which the record
   belongs. Each field has an access security level, either ASL0 or ASL1.
   The security level is defined in the record definition file (.dbd). Thus the
   access security level for a field is the same for all record instances
   of a record type.

**When**

   Access rules can contain input links and calculations similar to the
   calculation record.

## Limitations

An IOC database can be accessed only via pvAccess, Channel Access or the ioc (or vxWorks) shell.
It is assumed that access to the local IOC console
is protected via physical security, and that network access is protected
via normal networking and physical security methods.

No attempt has been made to protect against the sophisticated saboteur.
Network and physical security methods must be used to limit access to
the subnet on which the IOCs reside.

:::{note}

No access security is invoked within an IOC. This means that database
links and local channel access clients calls are not subject to access
control.
:::

### Definitions

This document uses the following terms:

- **ASL**
   Access Security Level.
- **ASG**
   Access Security Group
- **UAG**
   User Access Group
- **HAG**
   Host Access Group

## Quick Start

In order to "turn on" access security for a particular IOC the following
must be done:

-  Create an [access security file](#acf-file).
-  IOC databases may have to be modified:

   -  Record instances may have to have values assigned to field ASG. If
      ASG is null the record is in group DEFAULT.
   -  Access security files can be reloaded after iocInit via a
      subroutine record with asSubInit and asSubProcess as the
      associated subroutines. Writing the value 1 to this record will
      cause a reload.

   -  The startup script must contain the following command before iocInit. ::

         asSetFilename("/full/path/to/accessSecurityFile")

  -  The following is an optional command. ::

         asSetSubstitutions("var1=sub1,var2=sub2,...")

The following rules decide if access security is turned on for an IOC:

-  If asSetFilename is not executed before iocInit, access security will
   never be started.
-  If asSetFile is given and any error occurs while first initializing
   access security, then all access to that ioc is denied.
-  If after successfully starting access security, an attempt is made to
   restart and an error occurs then the previous access security
   configuration is maintained.

After an IOC has been booted with access security enabled, the access
security rules can be changed by issuing the asSetFilename,
asSetSubstitutions, and asInit. The functions asInitialize, asInitFile,
and asInitFP, which are described below, can also be used.

(acf-file)=
## Access Security Configuration File


This section describes the format of a file containing definitions of the
user access groups, host access groups, and access security groups. An
IOC creates an internal access configuration by reading an access
configuration file (the extension .acf is recommended). Lets first give a
simple example and then a complete description of the syntax.


:::{note}

In EPICS release 7.0.10 the Access Security Configuration File (ACF) parser was modified to
standardize the ACF grammar for forward compatibility.
The syntax that was accepted by earlier versions of the parser was not modified,
so existing access security configuration files do not need to be modified.
All ACF definitions will adhere to a consistent syntax format,
which will allow future additions to the access security language
without breaking existing configurations.
:::

### Simple Example


      UAG(uag) {user1,user2}
      HAG(hag) {host1,host2}
      ASG(DEFAULT) {
              RULE(1,READ)
              RULE(1,WRITE) {
                      UAG(uag)
                      HAG(hag)
             }
      }

These rules provide read access to anyone located anywhere and write
access to user1 and user2 if they are located at host1 or host2.

## Syntax Definition


In the following description:

   `[ ]` surrounds optional elements

   `|` separates alternatives

   `...` means that an arbitrary number of definitions may be given.

   `#` introduces a comment line

The elements `<name>`, `<user>`, `<host>`, `<pvname>` and `<calculation>` can be
given as quoted or unquoted strings. The rules for unquoted strings are
the same as for database definitions.


      UAG(<name>) [{ <user> [, <user> ...] }]
      ...
      HAG(<name>) [{ <host> [, <host> ...] }]
      ...
      ASG(<name>) [{
          [INP<index>(<pvname>)
          ...]
          RULE(<level>,NONE | READ | WRITE [, NOTRAPWRITE | TRAPWRITE]) {
              [UAG(<name> [,<name> ...])]
              [HAG(<name> [,<name> ...])]
              CALC(<calculation>)
          }
          ...
      }]
      ...


### Definitions


-  **UAG**: User Access Group. This is a list of user names that can have the access
   privilege. It may be empty; if UAG is not defined all users are allowed. A user name may appear in more than one UAG. To match, a user name must be identical to the user name
   read by the CA client library running on the client machine.
   With pvAccess (QSRV) it is possible to define user roles that define the access rights for a group of users, without the need to list each user individually.
-  **HAG**: Host Access Group. This is a list of host names. It may be
   empty; If HAG is not defined then all hosts are allowed. The same host name can appear in multiple HAGs. To match, a
   host name must match the host name read by the CA client library
   running on the client machine; both names are converted to lower case
   before comparison.
-  **ASG**: An access security group. The group DEFAULT is a special case.
   If a member specifies a null group or a group which has no ASG
   definition then the member is assigned to the group DEFAULT.
-  **INP\<index>** Index must have one of the values A to U. These are links to
   input process variables whose value can be used in a CALC condition.
   These are just like the INP fields of a calculation record.
   It is necessary to define INP fields if a CALC field is defined
   in any RULE for the ASG.
-  **RULE** This defines access permissions for each security level.
   \<level\> *must* be 0 or 1.
   The standard EPICS record types have all fields set
   to level 1 except for VAL, CMD (command), and RES (reset).
   Permission for a level 1 field implies permission for level 0 fields.
   The permissions are NONE, READ, and WRITE.
   WRITE permission implies READ permission.
   An optional argument specifies if writes should be trapped.
   Trapping makes it possible for modules like caPutLog to log database put operations.
   If not specified the default is NOTRAPWRITE.

-  **CALC** is just like the CALC field of a calculation record except
   that the result must evaluate to TRUE or FALSE. The rule only
   applies if the calculation result is TRUE, where the actual test
   for TRUE is (0.99 < result < 1.01). Anything else is regarded as
   FALSE and will cause the rule to be ignored. Assignment statements
   are not permitted in CALC expressions here.

:::{note}

**Semantics for unrecognised ACF file elements**

To enable adding new elements to ACF files in new EPICS releases
without breaking older clients that load those files,
elements that are included in an ACF file will be ignored
by a parser that does not understand them.

- If an element that is not understood by the parser is seen in an ACF file,
the parser will output a warning but does not handle it as an error,
as long as its syntax is otherwise correct.
- If elements are added to the ACF file that are malformed (e.g. missing parentheses),
the parser will report a syntax error.

:::

:::{note}
Rules allow the prescribed access if and only if
all the predicates the rule contains are satisfied.
- If the rule contains predicates that are unknown to the parser
(indicating future functionality), then the rule will NOT match,
a warning will be output, but will not cause an error as long as the syntax is otherwise correct.
- If the rule contains predicates that the parser does not recognise
which are malformed (e.g. missing parentheses),
then the rule will not match and the parser will report a syntax error.
- In this way rules can be extended with new predicates
without breaking older clients or giving those older clients elevated privileges.
:::

Each IOC record contains a field ASG, which specifies the name of the ASG
to which the record belongs.
If this field is null or specifies a group which is not defined
in the access security file then the record is placed in group DEFAULT.

The access privilege for a channel access or pvAccess client is determined as follows:

1. The ASG associated with the record is searched.
2. Each RULE is checked for the following:

   * The field's level must be less than or equal to the level for this
      RULE.
   * If UAG is defined, the user must belong to one of the specified
      UAGs. If UAG is not defined all users are accepted.
   * If HAG is defined, the user's host must belong to one one of the
      HAGs. If HAG is not defined all hosts are accepted.
   * If CALC is specified, the calculation must yield the value 1, i.e.
      TRUE. If any of the INP fields associated with this calculation are
      in INVALID alarm severity the calculation is considered false. The
      actual test for TRUE is .99 <result <1.01.

3. The maximum access allowed by step 2 is the access chosen.

Multiple RULEs can be defined for a given ASG, even RULEs with identical
levels and access permissions. The TRAPWRITE setting used for a client
is determined by the first WRITE rule that passes the rule checks.

### Checking Hostname Against DNS


Before EPICS Base release 7.0.3.1, host names given in a HAG entry of an IOC's
Access Security Configuration File (ACF) were compared against the hostname provided by the CA
client at connection time, which may or may not be the actual name of the host that the client
is running on.
This allowed rogue clients to pretend to be a different host, and the
IOC would believe them.

From that release on, it is possible to tell an IOC to ask its operating system to look
up the IP address of any hostnames listed in its ACF (which will normally be
done using the DNS or the `/etc/hosts` file). The IOC will then compare the
resulting IP address against the client's actual IP address when checking
access permissions at connection time. This name resolution is performed at
ACF file load time, which has a few consequences:

  1. If the DNS is slow when the names are resolved this will delay the process of loading the ACF file.
  2. If a host name cannot be resolved the IOC will proceed, but this host name will never be matched.
  3. Any changes in the hostname to IP address mapping will not be picked up by the IOC unless and until the ACF file gets reloaded.

Optionally, IP addresses may be added instead of, or in addition to, host
names in the ACF file.

This feature can be enabled before `iocInit` with

    asCheckClientIP = 1

### ascheck - Check Syntax of Access Configuration File

After creating or modifying an access configuration file it can be checked
for syntax errors by issuing the command:
::

   ascheck -S "xxx=yyy,..." < "filename"

This is a Unix command. It displays errors on stdout; if no errors are
detected it prints nothing.
The flag `-S` means a set of macro substitutions may appear. This is just like the
macro substitutions for dbLoadDatabase.

## IOC Access Security Initialization

In order to have access security turned on during IOC initialization the
following command must appear in the startup file before iocInit is
called:

      asSetFilename("/full/path/to/access/security/file.acf")

If this command is not used then access security will not be started by
iocInit. If an error occurs when iocInit calls asInit then all access to
the IOC is disabled, i.e. no CA/PVA client will be able to
access the IOC. Note that this command does not read the file itself, it
just saves the argument string for use later on, nor does it save the
current working directory, thus the use of an absolute path-name
for the file is recommended. A relative path name is not
recommended as the working directory may change during the startup process.

Access security also supports macro substitution just like database expansion routines. The desired substitutions can be defined as follows:

      asSetSubstitutions("var1=sub1,var2=sub2,...")

This command must be issued before iocInit.

After an IOC is initialized the access security database can be changed.
The preferred way is via the subroutine record described in the next
section. It can also be changed by issuing the following command to the
vxWorks shell:

      asInit

It is also possible to reissue asSetFilename and/or asSetSubstitutions
before asInit. If any error occurs during asInit the old access security
configuration is maintained. It is NOT permissible to call asInit before
iocInit is called.

Restarting access security after ioc initialization is an expensive
operation and should not be used as a regular procedure.

## Database Configuration


### Access Security Group


Each database record has a field ASG which holds a character string. Any
database configuration tool can be used to give a value to this field. If
the ASG of a record is not defined or is not equal to a ASG in the
configuration file then the record is placed in DEFAULT.

### Subroutine Record Support


Two subroutines, which can be attached to a subroutine record, are
available (provided with iocCore):

      asSubInit
      asSubProcess

:::{note}
These subroutines are automatically registered so there is no need for a
registrar definition in your database definition file.
:::

If a record is created that attaches to these routines, it can be used
to force the IOC to load a new access configuration database. To change
the access configuration:

1. Modify the file specified by the last call to asSetFilename so that it
   contains the new configuration desired.
2. Write a 1 to the subroutine record VAL field. This can be
   done via channel access.

   The record perfoms the following actions:

   * When the value is found to be 1, asInit is called and the value set
   back to 0.
   * The record is treated as an asynchronous record. Completion occurs
   when the new access configuration has been initialized or a time-out
   occurs. If initialization fails the record is placed into alarm with
   a severity determined by BRSV.

### Record Type Description


Each field of each record type has an associated access security level of
ASL0 or ASL1 (default value).
Fields which operators normally change are assigned ASL0, other fields are assigned ASL1.
For example, the VAL field of an analog output record is assigned ASL0 and all other fields ASL1.
This is because only the VAL field should be modified during normal operations.

#### Example:


Lets design a set of rules for a Linac. Assume the following:

1. Anyone can have read access to all fields at anytime.
2. Linac engineers, located in the injection control or control room,
   can have write access to most level 0 fields only if the Linac is not
   in operational mode.
3. Operators, located in the injection control or control room, can have
   write access to most level 0 fields anytime.
4. The operations supervisor, linac supervisor, and the application
   developers can have write access to all fields but must have some way
   of not changing something inadvertently.
5. Most records use the above rules but a few (high voltage power
   supplies, etc.) are placed under tighter control. These will follow
   rules 1 and 4 but not 2 or 3.
6. IOC channel access clients always have level 1 write privilege.

Most Linac IOC records will not have the ASG field defined and will thus
be placed in ASG DEFAULT. The following records will have an ASG defined:

-  `LI:OPSTATE` and any other records that need tighter control have
   ASG="critical". One such record could be a subroutine record used to
   cause a new access configuration file to be loaded. `LI:OPSTATE` has the
   value (0,1) if the Linac is (not operational, operational).
-  `LI:lev1permit` has ASG="permit". In order for the opSup, linacSup, or
   an appDev to have write privilege to everything this record must be
   set to the value 1.

The following access configuration satisfies the above rules.


      UAG(op) {op1,op2,superguy}
      UAG(opSup) {superguy}
      UAG(linac) {waw,nassiri,grelick,berg,fuja,gsm}
      UAG(linacSup) {gsm}
      UAG(appDev) {nda,kko}
      HAG(icr) {silver,phebos,gaea}
      HAG(cr) {mars,hera,gold}
      HAG(ioc) {ioclic1,ioclic2,ioclid1,ioclid2,ioclid3,ioclid4,ioclid5}
      ASG(DEFAULT) {
          INPA(LI:OPSTATE)
          INPB(LI:lev1permit)
          RULE(0,WRITE) {
              UAG(op)
              HAG(icr,cr)
              CALC("A=1")
          }
          RULE(0,WRITE) {
              UAG(op,linac,appdev)
              HAG(icr,cr)
              CALC("A=0")
          }
          RULE(1,WRITE) {
              UAG(opSup,linacSup,appdev)
              CALC("B=1")
          }
          RULE(1,READ)
          RULE(1,WRITE) {
              HAG(ioc)
          }
      }
      ASG(permit) {
          RULE(0,WRITE) {
              UAG(opSup,linacSup,appDev)
          }
          RULE(1,READ)
          RULE(1,WRITE) {
              HAG(ioc)
          }
      }
      ASG(critical) {
          INPB(LI:lev1permit)
          RULE(1,WRITE) {
              UAG(opSup,linacSup,appdev)
              CALC("B=1")
          }
          RULE(1,READ)
          RULE(1,WRITE) {
              HAG(ioc)
          }
      }

### pvAccess (QSRV) Specific Features


QSRV will enforce the access control policy loaded by the usual means as described above. This policy is applied to both Single and Group PVs.
With Group PVs, restrictions are not defined for the group, but rather for the individual member records.
The same policy will be applied regardless of how a record is accessed (individually, or through a group).

Policy application differs from CA (RSRV) in several ways:

   1. Client hostname is always the numeric IP address. HAG() entries must either contain
   numeric IP addresses, or **asCheckClientIP=1** flag must be set to translate hostnames into
   IPs on ACF file load (effects CA server as well). This prevents clients from trivially forging "hostname".
   2. In additional to client usernames, UAG definitions may contained items beginning with "role/" which are matched against the list of groups of which the client username is a
   member. Username to group lookup is done internally to QSRV, and depends on IOC host
   authentication configuration. Note that this is still based on the client provided username
   string.

  UAG(special) {
     someone, "role/op"
  }

The "special" UAG will match CA or PVA clients with the username "someone". It will
also match a PVA client if the client provided username is a member of the "op"
group (supported on POSIX targets and Windows).


## Full Language Specification for Access Security Configuration Files

### Lexical tokens

**Ignored stuff**

-   *Whitespace*: space, tab, `\r` (carriage return) -- may appear between tokens.

-   *Newlines*: `\n` -- same as whitespace for syntax, but tracked for error messages.

-   *Comments*: `#` ... end of line -- ignored.

**Terminals**

-   `UAG` → literal string `"UAG"`
-   `HAG` → `"HAG"`
-   `ASG` → `"ASG"`
-   `RULE` → `"RULE"`
-   `CALC` → `"CALC"`
-   `INP(link)` → literal `"INP"` followed immediately by one uppercase letter `A`-`U`

```text
    link-letter  ::= "A" | "B" | ... | "U"
    INP(link)    ::= "INP" link-letter
```

-   `INT` → integer literal

```text
    INT ::= [ "+" | "-" ]? DIGIT+
    DIGIT ::= "0" | "1" | ... | "9"
```

-   `FLOAT` → floating-point literal with decimal point

```text
    FLOAT ::= [ "+" | "-" ]? DIGIT* "." DIGIT+ [ ( "e" | "E" ) [ "+" | "-" ] DIGIT+ ]?
```

-   `STRING` → either
    -   **Unquoted**: One or more of

```text
        NAMECHAR ::= letter | digit | "_" | "-" | "+" | ":" | "." | "[" | "]" | "<" | ">" | ";"
        STRING(unquoted) ::= NAMECHAR+
```

    -   **Quoted**: Surrounding quotes are stripped;
        escapes are kept literal at parse level.

```text
        STRING(quoted) ::= '"' { STRINGCHAR | ESCAPE } '"'
        STRINGCHAR     ::= any char except '"' "\" "\n"
        ESCAPE         ::= "\" any-char
```

-   Punctuation tokens (single-character terminals):

```text
    "("  ")"  "{"  "}"  ","
```

---

### Grammar

#### Top level

```{eval-rst}
.. productionlist::
   acf_file : `asconfig`
   asconfig : `asconfig_item` { asconfig_item }
   asconfig_item : `uag_def`
   asconfig_item : `hag_def`
   asconfig_item : `asg_def`
   asconfig_item : `generic_top_level_item`
```

##### UAG / HAG groups

```{eval-rst}
.. productionlist::
   uag_def : "UAG" `uag_head` [ `uag_body` ]
   uag_head : "(" STRING ")"
   uag_body : "{" `uag_user_list` "}"
   uag_user_list : STRING { "," STRING }

```

```{eval-rst}
.. productionlist::
   hag_def : "HAG" `hag_head` [ `hag_body` ]
   hag_head : "(" STRING ")"
   hag_body : "{" `hag_host_list` "}"
   hag_host_list : STRING { "," STRING }
```

##### ASG (access security group)

```{eval-rst}
.. productionlist::
   asg_def : "ASG" `asg_head` [ `asg_body` ]
   asg_head : "(" STRING ")"
   asg_body : "{" `asg_body_item` { `asg_body_item` } "}"
   asg_body_item : `inp_config` | `rule_config`
```

###### INP config

```{eval-rst}
.. productionlist::
   inp_config : INP(link) "(" STRING ")"
```

###### RULE config

```{eval-rst}
.. productionlist::
   rule_config : "RULE" `rule_head` [ `rule_body` ]
   rule_head : "(" `rule_head_mandatory` "," `rule_log_option` ")"
   rule_head : "(" `rule_head_mandatory` ")"
   rule_head_mandatory : INT "," STRING
   rule_log_option : STRING
```

```{eval-rst}
.. productionlist::
   rule_body : "{" `rule_list` "}"
   rule_list : `rule_list_item` { `rule_list_item` }
   rule_list_item : "UAG" "(" `rule_uag_list` ")"
   rule_list_item : "HAG" "(" `rule_hag_list` ")"
   rule_list_item : "CALC" "(" STRING ")"
   rule_list_item : `rule_generic_block_elem`
```

```{eval-rst}
.. productionlist::
   rule_uag_list : STRING { "," STRING }
   rule_hag_list : STRING { "," STRING }
```

##### Generic / future-proof syntax

These are the "catch-all" constructs that are **parsed** but currently **ignored** semantically.

###### Keyword classes

These are parser-level categories used inside generic constructs:

```{eval-rst}
.. productionlist::
   keyword : "UAG"
   keyword : "HAG"
   keyword : "CALC"
   keyword : `non_rule_keyword`
   non_rule_keyword : "ASG"
   non_rule_keyword : "RULE"
   non_rule_keyword : INP(link)
```
(* INPA..INPU *)

###### Generic head (argument list)

```{eval-rst}
.. productionlist::
   generic_head : "(" ")"
   generic_head : "(" `generic_element` ")"
   generic_head :"(" `generic_list` ")"
   generic_list : `generic_element` "," `generic_element` { "," `generic_element` }
   generic_element : `keyword`
   generic_element : STRING
   generic_element : INT
   generic_element : FLOAT
```

###### Generic blocks

```{eval-rst}
.. productionlist::
   generic_block : "{" `generic_element` "}"
   generic_block : "{" `generic_list` "}"
   generic_block : "{" `generic_block_list` "}"
   generic_block_list : `generic_block_elem` { `generic_block_elem` }
   generic_block_elem : `generic_block_elem_name` `generic_head` [ `generic_block` ]
   generic_block_elem_name : `keyword`
   generic_block_elem_name :  STRING
```

###### Generic top-level items

These are "unknown" top-level constructs, all of which are parsed and then ignored with a warning.

```{eval-rst}
.. productionlist::
   generic_top_level_item : STRING `generic_head` `generic_list_block`
   generic_top_level_item : STRING `generic_head` `generic_block`
   generic_top_level_item : STRING `generic_head`
```

where

```{eval-rst}
.. productionlist::
   generic_list_block : "{" `generic_element` "}" "{" `generic_list` "}"
```

###### Generic blocks inside RULE bodies

These are the "future predicates" in a RULE's body; they cause the RULE to be disabled with a warning, but they **must** still parse.

```{eval-rst}
.. productionlist::
   rule_generic_block_elem : `rule_generic_block_elem_name` `generic_head` [ `generic_block` ]
   rule_generic_block_elem_name : `non_rule_keyword` | STRING
```
