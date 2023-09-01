# How to Set Up Console Access and Logging for VME and Soft IOCs

_This evolved from my notes when doing this for the IOCs at BESSY. Please add or correct things as you find them wrong or out-of-date._

The following instructions are based on our Debian Linux machines. (Which version? I don't remember. _Too stable_, I guess.) Other distributions (or other Unixes) might have slightly different commands and different places for things. The general steps will be the same on all distributions, though.

Knowledge of general system administration tasks (creating user accounts, using ssh, rsync etc.) is assumed.

I was giving a talk on [Administration of Soft IOCs under Linux](ftp://ftp.desy.de/pub/EPICS/meeting-2007/SoftIOC_Admin.pdf) at the [EPICS Collaboration Meeting in April 2007](http://epics.desy.de/content/e2/e127/index_eng.html) that partly covered this issue.


## Introduction

### Why are we doing this?

When debugging and/or trying to look what is happening on an IOC, the developer does not necessarily know if the database is running on a VME based or on a host based soft IOC.

*   Console access (and logging console output) should be uniform: working the same way for soft as for VME IOCs.
*   Connecting to a console should be easy. It should not require intimate knowledge of the system structure, the name of the IOC should be all that is needed for connecting to its console.
*   Multiple users should be able to log onto the same console. Only one of those should be granted write access. Forcing to take over write access must be possible, so that no one is able to block a console by not logging off.
*   Viewing log files should be as easy as pointing your browser to a certain URL.


### Conserver

[Conserver](http://www.conserver.com) is a free software that does provide all of the functionality needed plus a lot more things.

From its docs:

>Conserver is an application that allows multiple users to watch a serial console at the same time. It can log the data, allows users to take write-access of a console (one at a time), and has a variety of bells and whistles to accentuate that basic functionality. The idea is that conserver will log all your serial traffic so you can go back and review why something crashed, look at changes (if done on the console), or tie the console logs into a monitoring system (just watch the logfiles it creates). With multi-user capabilities you can work on equipment with others, mentor, train, etc. It also does all that client-server stuff so that, assuming you have a network connection, you can interact with any of the equipment from home or wherever.

I will describe a setup consisting of multiple conserver hosts, connect to a set of VME based IOCs (through telnet to terminal servers) and soft IOCs (through ssh). Setting up your soft IOCs to be accessed through ssh is described in the document [How to Set Up a Soft IOC Framework on Linux](setup-softioc-framework-linux).

### Multiple Server Setup

Conserver supports running multiple servers, that are aware of the lists of consoles each of the member serves. A conserver-client can ask any of the server nodes for a console, the server will automatically redirect the request to the appropriate server node.

Main advantage: client machines never need any re-configuration, if consoles are moved between servers or additional consoles are added to the system. They have to know the name of console they want to attach to and one of the servers (preferably through a DNS alias name) - that's it.


## Setting up Your Machines

### Get conserver

The machines intended to run conserver (i.e. the nodes that connect to consoles, provide console access, and log console output), need the conserver-server package installed.

The machines intended to be clients (i.e. the nodes where the console application can be run), need the conserver-client package installed.


### Configure the Conserver Servers

Conserver's configuration files use a straightforward configuration languange with lots of different options and very few structures. (See `man conserver.cf` for more details.)

It's a bit like configuring bootp or dhcp: The most important structure is a define command for aliases, that allow inclusion of other defines, adding or overriding parameters. Using a smart set of those definitions, the actual entries for the consoles can be quite short.

#### Shared vs. Local Configuration

To allow multiple servers to share the same configuration, the `#include` directive is used to add by-host configuration. For each of the servers, a separate configuration file is created for keeping the local configuration. The matching local configuration file is soft-linked to the generic name conserver.local. The shared conserver.cf file includes this file to read the by-host information.

So, e.g. on a conserver server s1, the directory `/etc/conserver` looks like

``` console
-rw-r----- 1 root     root 28785 Apr 18 12:15 conserver.cf
-rw-r----- 1 root     root   201 Mar 30 15:48 conserver.s1.cf
-rw-r----- 1 root     root   205 Mar 30 15:48 conserver.s2.cf
lrwxrwxrwx 1 root     root    20 Mar 30 15:29 conserver.local.cf -> conserver.s1.cf
```

That way, you can distribute a complete set of configuration files to multiple servers without damaging the setup.

#### The Local Configuration File

Local configuration will usually only set the master for certain console groups, i.e. it enables the server to decide which console lines it serves itself, and to which other master it should redirect requsts for other console lines.

For a server that should host the consoles for the project "bii" locally, and redirect the requests for "mls" consoles to another server, the local configuration looks like this:

``` console
default m-mls { master s2.mls.bessy.de; }
default m-bii { master localhost; }
```

#### Users and Groups

Set up a scheme of users and groups that you want to use. Authentification can be done by a password file or using PAM. Users and group definitions are used to grant access rights (read-only, read-write, admin) to certain users and groups. Decide what you need, and configure it.

We are using something like

```
group grp-adm  { users me, you, doubleyou; }

group grp-tsc  { users grp-adm, tscadm; }
group grp-id   { users grp-adm, idadm; }
```

to have people from two different areas (controls, insertion devices) use a password for write access to their IOCs.

#### Access to the Server

Define who will be the administrators on the server and which networks you will be allowing access from.

In this case: Use the group of administrators defined above, and allow access from all local (private) IPs.

```
access * {
        admin   grp-adm;
        allowed 127.0.0.1, 192.168.0.0/16;
}
```


#### Defaults for the Server

This block provides a reasonable set of default definitions for things. Some may even not be necessary, they're just here for clarification.

```
config localhost {
        autocomplete true;
        defaultaccess rejected;
        initdelay 60;
        logfile /var/log/conserver/conserver/conserver.log;
        passwdfile /etc/conserver/conserver.passwd;
        primaryport 782;
        redirect yes;
        reinitcheck 1;
        secondaryport 0;
        sslrequired false;
        unifiedlog /var/log/conserver/unified.log;
}
```

#### Defaults for the Groups

In this case, just make the logs go in different subdirectories, and allow read/write access for the groups defined above.

```
default tsc-def  { logfile /var/log/conserver/tsc/&.log;   rw grp-tsc; }
default id-def   { logfile /var/log/conserver/id/&.log;    rw grp-id; }
```

#### Message of the Day and Time Stamping

This defines what connecting users will see as a warning when they connect.

```
default message {
        motd \\
                                 WARNING!!!
This is only an example! ; }
```

General default that includes the message just defined and adds the definition of time stamps that conserver adds to log entries: at every line.

```
default def {
        include message;
        timestamp "1lb";
}
```

#### Include the Local Definitions

Include the local by-host configuration (as mentioned above).

`#include /etc/conserver/conserver.local.cf`

#### Defining the Soft IOC Hosts

Here the host machines for the soft IOCs are defined. (So that the conserver knows where to ssh to.)

```
default h-mls-sioc { host iochost.mls.bessy.de; }
default h-bii-sioc { host iochost.bii.bessy.de; }
```

#### Defaults for Console Types

These are the generic definitions for soft IOCs and terminal server based IOCs for the different groups and projects. We do it in a way so that the instances of console lines will only have to include one definition and add the stuff needed for that instance. the examples show the definitions for soft IOCs and terminal servers (telnet access to port 2001...2016 for a 16 port terminal server).
The first include is a definition from the local configuration file, telling the server which of the servers that console is connected to (who is the master of the console). The other included defintions were shown above.

```
default bii-sioc {
        include m-bii;
        include def;
        include tsc-def;
        include h-bii-sioc;
        type exec;
        execrunas iocadm;
        exec /usr/bin/ssh -i /home/controls/iocadm/.ssh/conserver -t U@H;
        execsubst U=cs,H=hs;
}
```

```
default bii-ts {
        include m-bii;
        include def;
        include tsc-def;
        type host;
        portbase 2000;
}
```

#### Lists of Terminal Servers

Next are the lists of the existing terminal servers, that VME IOC consoles (or other hardware) are connected to.

```
default ts2    { include bii-ts; host ts2.bii.bessy.de; }
default ts3    { include bii-ts; host ts3.bii.bessy.de; }
```

#### Lists of Console Instances

Finally, there are the lists of console instances. One line per each soft IOC or VME IOC that we are connecting to. Have a look at two VME IOCs on terminal server 2, one on terminal server 3, plus three soft IOCs.

```
console ioc1    { include ts2; port  1; include tsc-def; aliases ts2-01; }
console ioc2    { include ts2; port  2; include tsc-def; aliases ts2-02; }
console ioc3    { include ts3; port  1; include tsc-def; aliases ts3-01; } 
```

```
console sioc1   { include bii-sioc; }
console sioc2   { include bii-sioc; }
console sioc3   { include bii-sioc; }
```

### Start the Conserver Servers

`/etc/init.d/conserver-server start` (or the equivalent on your Linux distribution) should get things running.

Entering it in your system configuration will make sure it gets started when the machine boots.

### Caveat: Memory Leak

There is a memory leak in the conserver server (as of version 8.1.14). We have set up a cron job that restarts the conserver server once a week to get around. This bug is known to the conserver developers - hopefully it will be fixed some time soon.

### Configure the Conserver Clients

After installing the conserver-client package, the system-wide configuration file `/etc/console.cf` will contain the default configuration for the console clients.

It might be a good idea to add a DNS alias console to all your networks, so that all console configurations can point to the same master. Even if you move a conserver to a different machine, you will be able to change the DNS alias and don't have to reconfigure all clients.

## Set up Web Browsing for the Log Files

### Collect the Log Files

On your web server, create a location where the conserver logs are to be placed. Set up cron jobs that collect the logfiles from your servers using commands like this:

``` bash
/usr/bin/rsync -a --delete consync@s1.bii.bessy.de:/var/log/conserver /web/conserver-bii >> /web/conserver-bii/consync.log 2>&1
```

(This one requires a user account for consync being created on the conserver server s1, and that the collecting user account having ssh access to it.)

### Setup the Web Server

This is well outside the scope of this Wiki page and should be fairly easy - refer to the documentation of your web server to learn about it.

_**Good luck!**_

[Ralph Lange (BESSY)](mailto:Ralph.Lange_at_bessy.de)
