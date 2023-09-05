===================
IOC Access Security
===================

.. tags:: developer, advanced


.. contents:: Table of Contents
 :depth: 3

Features
--------

Access security protects IOC databases from unauthorized Channel Access
or pvAccess Clients. Access security is based on the following:

Who
   User id of the client(Channel Access/pvAccess).
Where
   Host id where the user is logged on. This is the host on which the
   client exists. Thus no attempt is made to see if a
   user is local or is remotely logged on to the host.
What
   Individual fields of records are protected. Each record has a field
   containing the Access Security Group (ASG) to which the record
   belongs. Each field has an access security level, either ASL0 or ASL1.
   The security level is defined in the record definition file (.dbd). Thus the
   access security level for a field is the same for all record instances
   of a record type.
When
   Access rules can contain input links and calculations similar to the
   calculation record.

Limitations
^^^^^^^^^^^

An IOC database can be accessed only via pvAccess, Channel Access or the ioc (or vxWorks) shell.
It is assumed that access to the local IOC console
is protected via physical security, and that network access is protected
via normal networking and physical security methods.

No attempt has been made to protect against the sophisticated saboteur.
Network and physical security methods must be used to limit access to
the subnet on which the IOCs reside.

Definitions
^^^^^^^^^^^

This document uses the following terms:

ASL
   Access Security Level.
ASG
   Access Security Group
UAG
   User Access Group
HAG
   Host Access Group

Quick Start
-----------

In order to "turn on" access security for a particular IOC the following
must be done:

-  Create the access security file.
-  IOC databases may have to be modified

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


Access Security Configuration File
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This section describes the format of a file containing definitions of the
user access groups, host access groups, and access security groups. An
IOC creates an access configuration database by reading an access
configuration file (the extension .acf is recommended). Lets first give a
simple example and then a complete description of the syntax.

Simple Example
''''''''''''''

::

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

Syntax Definition
'''''''''''''''''

In the following description:

   [ ] surrounds optional elements

   \| separates alternatives

   ... means that an arbitrary number of definitions may be given.

   # introduces a comment line

The elements <name>, <user>, <host>, <pvname> and <calculation> can be
given as quoted or unquoted strings. The rules for unquoted strings are
the same as for database definitions.

::

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

Discussion
''''''''''

-  UAG: User Access Group. This is a list of user names. The list may be
   empty. A user name may appear in more than one UAG. To match, a user
   name must be identical to the user name read by the CA client library
   running on the client machine. For vxWorks clients, the user name is
   usually taken from the user field of the boot parameters.
-  HAG: Host Access Group. This is a list of host names. It may be
   empty. The same host name can appear in multiple HAGs. To match, a
   host name must match the host name read by the CA client library
   running on the client machine; both names are converted to lower case
   before comparison however. For vxWorks clients, the host name is
   usually taken from the target name of the boot parameters.
-  ASG: An access security group. The group DEFAULT is a special case.
   If a member specifies a null group or a group which has no ASG
   definition then the member is assigned to the group DEFAULT.
-  INP<index>Index must have one of the values A to L. These are just
   like the INP fields of a calculation record. It is necessary to define
   INP fields if a CALC field is defined in any RULE for the ASG.
-  RULE This defines access permissions. <level> must be 0 or 1.
   Permission for a level 1 field implies permission for level 0 fields.
   The permissions are NONE, READ, and WRITE. WRITE permission implies
   READ permission. The standard EPICS record types have all fields set
   to level 1 except for VAL, CMD (command), and RES (reset). An
   optional argument specifies if writes should be trapped. See the
   section below on trapping Channel Access writes for how this is used.
   If not given the default is NOTRAPWRITE.

   -  UAG specifies a list of user access groups that can have the access
      privilege. If UAG is not defined then all users are allowed.
   -  HAG specifies a list of host access groups that have the access
      privilege. If HAG is not defined then all hosts are allowed.
   -  CALC is just like the CALC field of a calculation record except
      that the result must evaluate to TRUE or FALSE. The rule only
      applies if the calculation result is TRUE, where the actual test
      for TRUE is (0.99 < result < 1.01). Anything else is regarded as
      FALSE and will cause the rule to be ignored. Assignment statements
      are not permitted in CALC expressions here.

Each IOC record contains a field ASG, which specifies the name of the ASG
to which the record belongs. If this field is null or specifies a group
which is not defined in the access security file then the record is placed
in group DEFAULT.

The access privilege for a channel access client is determined as
follows:

#. The ASG associated with the record is searched.
#. Each RULE is checked for the following:

   #. The field's level must be less than or equal to the level for this
      RULE.
   #. If UAG is defined, the user must belong to one of the specified
      UAGs. If UAG is not defined all users are accepted.
   #. If HAG is defined, the user's host must belong to one one of the
      HAGs. If HAG is not defined all hosts are accepted.
   #. If CALC is specified, the calculation must yield the value 1, i.e.
      TRUE. If any of the INP fields associated with this calculation are
      in INVALID alarm severity the calculation is considered false. The
      actual test for TRUE is .99 <result <1.01.

#. The maximum access allowed by step 2 is the access chosen.

Multiple RULEs can be defined for a given ASG, even RULEs with identical
levels and access permissions. The TRAPWRITE setting used for a client
is determined by the first WRITE rule that passes the rule checks.

ascheck - Check Syntax of Access Configuration File
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After creating or modifying an access configuration file it can be checked
for syntax errors by issuing the command:
::

   ascheck -S "xxx=yyy,..." < "filename"

This is a Unix command. It displays errors on stdout. If no errors are
detected it prints nothing. Only syntax errors not logic errors are
detected. Thus it is still possible to get your self in trouble. The flag
-S means a set of macro substitutions may appear. This is just like the
macro substitutions for dbLoadDatabase.

IOC Access Security Initialization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In order to have access security turned on during IOC initialization the
following command must appear in the startup file before iocInit is
called:
::

      asSetFilename("/full/path/to/access/security/file.acf")

If this command is not used then access security will not be started by
iocInit. If an error occurs when iocInit calls asInit than all access to
the ioc is disabled, i.e. no channel access client will be able to
access the ioc. Note that this command does not read the file itself, it
just saves the argument string for use later on, nor does it save the
current working directory, which is why the use of an absolute path-name
for the file is recommended (a path name could be specified relative to
the current directory at the time when iocInit is run, but this is not
recommended if the IOC also loads the subroutine record support as a
later reload of the file might happen after the current directory had
been changed).

Access security also supports macro substitution just like
dbLoadDatabase. The following command specifies the desired
substitutions:
::

      asSetSubstitutions("var1=sub1,var2=sub2,...")

This command must be issued before iocInit.

After an IOC is initialized the access security database can be changed.
The preferred way is via the subroutine record described in the next
section. It can also be changed by issuing the following command to the
vxWorks shell:
::

      asInit

It is also possible to reissue asSetFilename and/or asSetSubstitutions
before asInit. If any error occurs during asInit the old access security
configuration is maintained. It is NOT permissible to call asInit before
iocInit is called.

Restarting access security after ioc initialization is an expensive
operation and should not be used as a regular procedure.

Database Configuration
----------------------

Access Security Group
^^^^^^^^^^^^^^^^^^^^^

Each database record has a field ASG which holds a character string. Any
database configuration tool can be used to give a value to this field. If
the ASG of a record is not defined or is not equal to a ASG in the
configuration file then the record is placed in DEFAULT.

Subroutine Record Support
^^^^^^^^^^^^^^^^^^^^^^^^^

Two subroutines, which can be attached to a subroutine record, are
available (provided with iocCore):
::

      asSubInit
      asSubProcess

NOTE: These subroutines are automatically registered thus do NOT put a
registrar definition in your database definition file.

If a record is created that attaches to these routines, it can be used
to force the IOC to load a new access configuration database. To change
the access configuration:

#. Modify the file specified by the last call to asSetFilename so that it
   contains the new configuration desired.
#. Write a 1 to the subroutine record VAL field. Note that this can be
   done via channel access.

The following action is taken:

#. When the value is found to be 1, asInit is called and the value set
   back to 0.
#. The record is treated as an asynchronous record. Completion occurs
   when the new access configuration has been initialized or a time-out
   occurs. If initialization fails the record is placed into alarm with
   a severity determined by BRSV.

Record Type Description
'''''''''''''''''''''''

Each field of each record type has an associated access security level of
ASL0 or ASL1 (default value).
Fields which operators normally change are assigned ASL0, other fields are assigned ASL1.
For example, the VAL field of an analog output record is assigned ASL0 and all other fields ASL1.
This is because only the VAL field should be modified during normal operations.

Example:
^^^^^^^^

Lets design a set of rules for a Linac. Assume the following:

#. Anyone can have read access to all fields at anytime.
#. Linac engineers, located in the injection control or control room,
   can have write access to most level 0 fields only if the Linac is not
   in operational mode.
#. Operators, located in the injection control or control room, can have
   write access to most level 0 fields anytime.
#. The operations supervisor, linac supervisor, and the application
   developers can have write access to all fields but must have some way
   of not changing something inadvertently.
#. Most records use the above rules but a few (high voltage power
   supplies, etc.) are placed under tighter control. These will follow
   rules 1 and 4 but not 2 or 3.
#. IOC channel access clients always have level 1 write privilege.

Most Linac IOC records will not have the ASG field defined and will thus
be placed in ASG DEFAULT. The following records will have an ASG defined:

-  LI:OPSTATE and any other records that need tighter control have
   ASG="critical". One such record could be a subroutine record used to
   cause a new access configuration file to be loaded. LI:OPSTATE has the
   value (0,1) if the Linac is (not operational, operational).
-  LI:lev1permit has ASG="permit". In order for the opSup, linacSup, or
   an appDev to have write privilege to everything this record must be
   set to the value 1.

The following access configuration satisfies the above rules.
::

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


Summary of Functional Requirements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A brief summary of the Functional Requirements is:

#. Each field of each record type is assigned an access security level.
#. Each record instance is assigned to a unique access security group.
#. Each user is assigned to one or more user access groups.
#. Each node is assigned to a host access group.
#. For each access security group a set of access rules can be defined.
   Each rule specifies:

   #. Access security level
   #. READ or READ/WRITE access.
   #. An optional list of User Access Groups or \* meaning anyone.
   #. An optional list of Host Access Groups or \* meaning anywhere.
   #. Conditions based on values of process variables

Additional Requirements
^^^^^^^^^^^^^^^^^^^^^^^

Performance
''''''''''''

Although the functional requirements do not mention it, a fundamental
goal is performance. The design provides almost no overhead during
normal database access and moderate overhead for the following: channel
access client/server connection, ioc initialization, a change in value
of a process variable referenced by an access calculation, and
dynamically changing a records access control group. Dynamically
changing the user access groups, host access groups, or the rules,
however, can be a time consuming operation. This is done, however, by a
low priority IOC task and thus does not impact normal ioc operation.

Generic Implementation
''''''''''''''''''''''

Access security should be implemented as a stand alone system, i.e. it
should not be embedded tightly in database or channel access.

No Access Security within an IOC
''''''''''''''''''''''''''''''''

No access security is invoked within an IOC . This means that database
links and local channel access clients calls are not subject to access
control. Also test routines such as dbgf should not be subject to access
control.

Defaults
''''''''

It must be possible to easily define default access rules.

Access Security is Optional
'''''''''''''''''''''''''''

When an IOC is initialized, access security is optional.

pvAccess (QSRV) Specific Features
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

QSRV will enforce the access control policy loaded by the usual means (cf. asSetFilename() ).
This policy is applied to both Single and Group PVs.
With Group PVs, restrictions are not defined for the group, but rather for the individual member records.
The same policy will be applied regardless of how a record is accessed (individually, or through a group).

Policy application differs from CA (RSRV) in several ways:

Client hostname is always the numeric IP address. HAG() entries must either contain
numeric IP addresses, or **asCheckClientIP=1** flag must be set to translate hostnames
into IPs on ACF file load (effects CA server as well). This prevents clients from trivially
forging "hostname". In additional to client usernames, UAG definitions may contained items
beginning with "role/" which are matched against the list of groups of which the client
username is a member. Username to group lookup is done internally to QSRV, and depends on
IOC host authentication configuration. Note that this is still based on the client provided username string.
::

  UAG(special) {
     someone, "role/op"
  }

The "special" UAG will match CA or PVA clients with the username "someone". It will
also match a PVA client if the client provided username is a member of the "op"
group (supported on POSIX targets and Windows).
