How to find which IOC provides a PV
===================================

``` {tags}
beginner, user, developer
```

This process is for IOCs running on Linux servers.

Find Host and TCP port
----------------------

The `cainfo` command will tell you which host is serving a particular
PV, and which TCP port number on that host is used.

    $ cainfo LN-TS{EVR:1A-SFP}Pwr:RX-I
    LN-TS{EVR:1A-SFP}Pwr:RX-I
    State:            connected
    Host:             10.0.152.111:5064
    Access:           read, write
    Native data type: DBF_DOUBLE
    Request type:     DBR_DOUBLE
    Element count:    1

Here we see that the PV "LN-TS{EVR:1A-SFP}Pwr:RX-I" is served from port
number 5064 of 10.0.152.111.

    $ cainfo LN-RF{AMP:1}Amp-Sts
    LN-RF{AMP:1}Amp-Sts
    State:            connected
    Host:             linacioc01.cs.nsls2.local:36349
    Access:           read, write
    Native data type: DBF_ENUM
    Request type:     DBR_ENUM
    Element count:    1

Here is another example where the hostname is shown instead of an IP
address. Also this server has more than one IOC, and the one in question
is using port 36349.

Find which process is using a TCP port (Linux only)
---------------------------------------------------

Super-user (root) permission is required to find which Linux process is
bound to a particular TCP port.

To continue the example from above. On the server
linacioc01.cs.nsls2.local we run:

    $ sudo netstat -tlpn | grep 36349
    tcp        0      0 0.0.0.0:36349           0.0.0.0:*               LISTEN      4627/s7ioc

This tells us that TCP port 36349 is bound by process ID (PID) 4627,
which has the process name of 's7ioc'.

Find information about a process (Linux only)
---------------------------------------------

The `ps` command can give some information, including the command used
to start the process. This often contains enough information to identify
where the IOC's files can be found.

    $ ps aux|grep 4627
    softioc   4627  1.5  0.0  93748  6616 pts/23   Ssl+ Jan07 744:18 ../../bin/linux-x86/s7ioc /epics/iocs/RF-CONTROL/iocBoot/iocrf-control/st.cmd

There are several pieces of information available under `/proc` which
are useful. The entry `/proc/<pid>/cwd` is a symbolic link to the
current working directory of the process. There is also
`/proc/<pid>/exe` which links to the executable.

    $ sudo ls -l /proc/4627/cwd
    lrwxrwxrwx 1 softioc softioc 0 Feb 10 11:49 /proc/4627/cwd -> /epics/iocs/RF-CONTROL
    $ sudo ls -l /proc/4627/exe
    lrwxrwxrwx 1 softioc softioc 0 Jan  7 09:58 /proc/4627/exe -> /epics/iocs/RF-CONTROL/bin/linux-x86/s7ioc

Additional: Finding the procServ/screen running an IOC (Linux only)
-------------------------------------------------------------------

The `ps` command can also tell us the PID of the parent of the IOC
process. The techniques of step 3 can also be applied to the parent.

    $ ps -eo pid,ppid,user,cmd|grep 4627
    4627  4566 softioc  ../../bin/linux-x86/s7ioc /epics/iocs/RF-CONTROL/iocBoot/iocrf-control/st.cmd

The parent PID in the second column is 4566.

    $ ps aux|grep 4566
    softioc   4566  0.0  0.0   3452   592 ?        Ss   Jan07   2:18 /usr/bin/procServ -q -c /epics/iocs/RF-CONTROL/iocBoot/iocrf-control -i ^D^C^] -p /var/run/softioc-RF-CONTROL.pid -n RF-CONTROL --restrict --logfile=/var/log/softioc-RF-CONTROL.log 4057 /epics/iocs/RF-CONTROL/iocBoot/iocrf-control/st.cmd

And to complete the circle, and get access to the IOC console, we find
which TCP port this procServ instance is bound to.

    $ sudo netstat -tlpn|grep 4566
    tcp        0      0 127.0.0.1:4057          0.0.0.0:*               LISTEN      4566/procServ
    $ telnet localhost 4057
    epics> dbpr LN-RF{AMP:1}Amp-Sts
    ASG:                DESC: Ampl.500 MHz E-Source             DISA: 0             
    DISP: 0             DISV: 1             NAME: LN-RF{AMP:1}Amp-Sts               
    RVAL: 16            SEVR: NO_ALARM      STAT: NO_ALARM      SVAL: 0             
    TPRO: 0             VAL: 1
