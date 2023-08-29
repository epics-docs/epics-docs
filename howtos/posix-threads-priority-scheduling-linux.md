# How To Use POSIX Thread Priority Scheduling under Linux

## Introduction

The Linux scheduler supports the SCHED_FIFO scheduling policy defined by POSIX.1-2001. Threads scheduled with this "real-time" policy can be assigned a priority (under Linux) in the range 1..99 with 99 representing the highest priority. Since ordinary, "non-real time" processes execute at priority 0 ([nice(1)](https://linux.die.net/man/1/nice) modifies a "dynamic priority" which only affects processes with real-time priority 0 and implements fair timesharing among such processes) SCHED_FIFO threads are always capable to preempt "ordinary processes" (these use the policy SCHED_OTHER). Note, however, that unless the Linux kernel is built with the RT_PREEMPT patch and measures are taken to lock the EPICS process in memory etc., no strictly deterministic latencies can be expected even under the SCHED_FIFO policy which thus is to be considered _soft-real time_.

## Configuring How can I let epicsThreads use the SCHED_FIFO Policy?

In order to let EPICS use the SCHED_FIFO real-time policy you first need to check that the following option is set to "YES" in `epics-base/configure/CONFIG_SITE`

``` makefile
# Use POSIX thread priority scheduling (YES or NO)
USE_POSIX_THREAD_PRIORITY_SCHEDULING = YES
```

If you find that the current setting is "NO" then you need to rebuild EPICS base (`make clean uninstall; make`) after changing to "YES". Since engaging the SCHED_FIFO policy gives any thread created under that policy a higher priority than any normal process, using SCHED_FIFO requires special privileges. Under a reasonably recent Linux equipped with the pam_security module or systemd it is not necessary to execute EPICS IOCs as root. Depending on your Linux system granting an IOC process running as a non-root user the required permissions requires some configuration, though.

### SysV-style Init System, or user-mode systemd

On Linux systems using the traditional init system, the system administrator can define the maximum priority that may be used by specific users and/or groups in a file under `/etc/security/limits.d/`, see the [manpage for `limits.conf(5)`](https://linux.die.net/man/5/limits.conf). E.g., if a file `/etc/security.limits.d/epics.conf` is created with the following contents (it may be necessary for a user to log out and log back on in order to obtain the new privileges):

``` bash
someuser hard rtprio 99
someuser soft rtprio  0
someuser hard memlock unlimited
someuser soft memlock  0
```

then processes created by "_someuser_" still have priority and memlock limts of 0 by default (this is the "soft" value) but "_someuser_" may increase the rtprio limit up to 99 either from a running program (using the system call [setrlimit(2)](https://linux.die.net/man/2/setrlimit)) or within a shell e.g., with Bash's `ulimit -r` utility. Note that a user process can set and/or lower its hard limit but _never increase_ it. RTM.

If you are starting IOCs using user-mode systemd (i.e. with `systemctl --user` commands) you will also need the above settings or an equivalent for the user account(s) that you run your IOC under.

### IOCs as systemd Services

On Linux systems using systemd you probably already have a service file in `/etc/systemd/system/myioc.service` or elsewhere that starts your IOC as a service. The following example uses procServ and includes the required configuration for granting the IOC process the necessary permissions.

``` systemd
[Unit]
Description=EPICS Soft IOC myioc
Requires=network.target
After=network.target

[Service]
ExecStart=/usr/bin/procServ --foreground --quiet --port 4051 /path_to_myioc/iocBoot/myiocinstance/st.cmd
Restart=always
User=iocuser
RuntimeDirectory=myioc
CPUAffinity=1-3
LimitMEMLOCK=infinity
LimitRTPRIO=99

[Install]
WantedBy=multi-user.target
```

Note the last three lines of the `[Service]` section which are granting the process permissions to run in real-time. Refer to the [systemd.exec documentation](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#Process%20Properties) for details.

**Tip:** In case your service file is generated automatically by a deployment tool which doesn't allow you to configure these real-time parameters you can augment an existing service file by dropping the real-time related configuration into `/etc/systemd/system/myioc.service.d/10-realtime.conf`:

``` systemd
[Service]
CPUAffinity=1-3
LimitMEMLOCK=infinity
LimitRTPRIO=99
```

Once your service file is in place, instruct systemd to reload its configuration and to start your IOC:

``` console
$ sudo systemctl daemon-reload
$ sudo systemctl start myioc.service
```

### Summary

You need to do three things:

1.  Build EPICS base with `USE_POSIX_THREAD_PRIORITY_SCHEDULING=YES`
2.  Make sure your EPICS application process has sufficient privileges to use SCHED_FIFO and the desired priority range.
3.  _SysV Init only:_ Set the soft and hard RTPRIO limits for your EPICS application process to enable it to actually make use of the privilege. This step is required because it is usually a bad idea to run _all_ processes created by a given user or group at real-time priorities.  
    _Systemd only:_ Set the permissions for RTPRIO and MEMLOCK in the `[Service]` section of your IOC service configuration.

## Verify that Real-Time Scheduling has been enabled correctly

### Verify that Memory has been locked

Run

``` console
$ grep Vm /proc/`pgrep st.cmd`/status
```

![Example output of "grep Vm /proc/`pgrep st.cmd`/status"](Check-VmLck.png)

on the command line. If the size reported for "VmLck" is close to "VmSize" your IOC has been locked into memory successfully, if "VmLck" is "0 kB" the IOC process didn't lock its memory. If an EPICS IOC detects that it has permissions to set real-time thread priorities it tries to lock memory – double check that the IOC process has both permission to adjust real-time thread priorities _and_ to lock memory!

### Verify scheduling Policy and Thread Priorities

``` console
$ ps -To pid,tid,policy,rtprio,comm -p `pgrep st.cmd`
```

![Example output of "ps -To pid,tid,policy,rtprio,comm -p `pgrep st.cmd`"](Check-scheduling-policy-and-thread-priorities-using-CLI.png)

If your system is configured correctly you should see "FF" (short for SCHED_FIFO) in the "POL" column and different priorities in the "RTPRIO" column. If you see "TS" (short for SCHED_OTHER) and "-" in the "POL" column for the IOC's threads, your IOC process probably doesn't have the necessary permissions to run with real-time priority.

If you have linked your IOC against [MCore Utils](https://github.com/epics-modules/MCoreUtils) you can also verify this on the IOC shell by running

``` console
epics> mcoreThreadShowAll
```

![](Check-scheduling-policy-and-thread-priorities-using-mcoreThreadShowAll-1.png)

You should see different priorities for the various threads in the "OSSPRI" column, the "POLICY" column should report "FIFO".

### Verify the CPU Affinity

You can get the CPU affinity of init/systemd as well as the one of your IOC process by running

``` console
$ taskset -c -p 1
$ taskset -c -p `pgrep st.cmd`
```

![Example output of "taskset -c -p 1; taskset -c -p `pgrep st.cmd`"](Check-CPU-affinity-using-CLI.png)

on the command line. On the IOC again

``` console
epics> mcoreThreadShowAll
```

![Example output of "mcoreThreadShowAll"](Check-CPU-affinity-using-mcoreThreadShowAll.png)

comes in handy – check the "CPUSET" column.
