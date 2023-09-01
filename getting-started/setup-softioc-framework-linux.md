# How to Set Up a Soft IOC Framework on Linux


_This evolved from my notes when doing this for the soft IOCs at BESSY. Please add or correct things as you find them wrong or out-of-date._

The following instructions are based on our Debian Linux machines. (Which version? I don't really care. _Too stable_, I guess.) Other distributions (or other Unixes) might have different commands and different places for things. This is especially true for the Debian `/etc/init.d` script I'm attaching to this page. If you create a different script for a different distribution, please add it to this page. Others will be able to use it. The general steps will be the same on all distributions, though.

Knowledge of general system administration tasks (creating user accounts etc.) is assumed.

I was giving a talk on [Administration of Soft IOCs under Linux](ftp://ftp.desy.de/pub/EPICS/meeting-2007/SoftIOC_Admin.pdf) at the [EPICS Collaboration Meeting in April 2007](http://epics.desy.de/content/e2/e127/index_eng.html) that partly covered this issue.

## Introduction

### Why are we doing this?

When using soft IOCs in production, they should be treated as important system services:

* Soft IOCs should be started and stopped by the system.
* There should be a fallback system you can easily switch over to in case of hardware failures.

Other objectives were: In the same way as for VME IOCs, the application developer should be able to reset the soft IOC without needing root access to the host.

* The IOC application developer should be able to start and stop IOCs manually.

When multiple soft IOCs share the same host (and the same IP address), Channel Access can not tell them apart. Access Security will not be able to distiguish between CA connections coming from different soft IOCs. When debugging CA clients, CA will not be able to tell you which of the soft IOCs a connection goes to.

* Channel Access should be able to distinguish between different soft IOCs, even if they are hosted on the same machine.

I was considering using a virtualization layer (based on VMware) to allow running soft IOCs in an encapsulated environment. I found the effort too high, the layer too thick, and the expected performance hit too hard – only to get a separate IP address for each soft IOC.

When debugging and/or trying to look what is happening on an IOC, the developer does not necessarily know if the database is running on a VME based or on a host based soft IOC.

* Console access (and logging console output) should be uniform: working the same way for soft as for VME IOCs.

The setup necessary to achieve this is described in the document [How to Set Up Console Access and Logging for VME and Soft IOCs](console-logging-vme-softioc).

### Concept

To allow Access Security telling the soft IOCs apart, they are run under separate user names.

The procServ utility will be used as an environment that allows to start soft IOCs in the background and connect to their consoles later, much like the serial consoles of VME IOCs. (See the procServ link on the [Extensions Page](https://epics-controls.org/resources-and-support/extensions/). Formerly, the screen facility was used, but reported problems, e.g. IOCs hanging up after console access, made us change to something less complex.)

Attaching to a soft IOC console will be done through ssh, using a special console access key. Ssh is set up with the matching telnet commands that reattach to the soft IOCs. Opening an ssh connection using the console access key to the user ioc123 on the soft IOC host will immediately attach to the console of the soft IOC named ioc123 (that is running as user ioc123).

## Setting up Your Machine

### Create User Accounts and ssh Access

#### Soft IOC Administrator Account

Create a generic user account that application developers will use to start/stop soft IOCs. (We call it iocadm.)

Put the public ssh keys of the application developers into `~/.ssh/authorized_keys` of iocadm.

#### ssh Key Pairs

As iocadm, create one key pair for this user, and another key pair for console access.

#### Soft IOCs

Create one user account for each soft IOC you intend to host. User name should be the IOC name, the group is not really important. (Maybe create a group iocs that you put all of them into?)

Into each of the `~/.ssh/authorized_keys` files, put two public keys:

1.  The public ssh key of iocadm.
2.  The public ssh key for console access.

In front of the console access key, put the telnet command to reattach to the soft IOC console. For a user/IOC ioc123 that provides console access on port 24703, the line should look like this:

```
command="telnet localhost 24703" ssh-rsa AAAAB3NzaC1yc2EAAAA.....
```

### Configure the sudo Facility

#### Allow the iocadm User to Start and Stop Soft IOCs

On the soft IOC host, allow iocadm to use sudo to execute commands as any of the soft IOC users. `/etc/sudoers` should have a line like:

```
iocadm ALL = (ioc123, ioc124, ioc125) NOPASSWD: ALL
```

### Setup the Start/Stop script

#### Create the /etc/init.d script

I'm attaching the script that we're using as `/etc/init.d/softIOC`. It got quite huge and complex – _sorry!_. It has been modelled after Debian's skeleton scripts, you should probably adapt it to match the standards that your distribution implies.

It contains the local settings for where to find things, routines to read in the configuration file, the code necessary to start/stop a soft IOC as a different user under procServ, and the usual init.d script stuff that checks command line arguments and calls the other routines.

_If you have a script working for a different distribution, please add it to this page, as it could make life easier for others!_

#### Create the Configuration File

The configuration file contains a section for each of the soft IOCs. A section starts with the IOC name followed by a colon, and ends with an empty line.

Within a section you can set special variables used by the softIOC script as well as environment variables that will be set for the soft IOC.

The special section global: contains settings that will be applied to _all_ soft IOCs (may be overridden by the IOC section).

The special line auto: contains the names of the soft IOCs that should be started when the script is run as part of the system boot-up process.

Section and IOC names are not case sensitive.

So a minimal configuration file could look like this (remember the empty line that is required after each section):

```
AUTO:   ioc123

GLOBAL:

ioc123:

ioc124:

ioc125:

```

### Distribute the Required Stuff to the Soft IOC Host

#### EPICS Base

Soft IOCS will need libraries from EPICS base. Make sure these are existing and can be found.

#### Code and Databases

Add the soft IOC host to the code deployment scheme you are using. The soft IOC binaries, databases, and start up scripts must be available for the soft IOCs to be started.

## Start Your Soft IOCs

### Start the IOCs using the startup script

Starting and stopping the soft IOCs should work now! Ssh to the soft IOC host as iocadm and try calling the startup script:

```
/etc/init.d/softIOC start ioc123
```

### Watch them run

Ssh to the soft IOC host using the console access key and see if you can get access to the IOC console:

``` bash
ssh -i ~iocadm/.ssh/console_access -t ioc123@iochost
```

You should be directly connected to your IOC's console.

### Check if Starting IOCs at reboot works

If you made entries to the auto: section, reboot the machine to check that starting IOCs at boot time works.

_**Good luck!**_

[Ralph Lange (BESSY)](mailto:Ralph.Lange_at_bessy.de)


* * *

## The Startup Script

`/etc/init.d/softIOC` script for Debian Linux

``` sh
#! /bin/sh
# Author: <Ralph.Lange@bessy.de>
#
# History:
#          2006-03-12: Adapted from D. HerrendÃ¶rfer's ca-gateway script
#          2006-04-04: Bugfix in config file parser
#          2008-05-20: Adapted to procServ

# Do NOT "set -e"

# !! This script is located on a mounted file system
# !! It must be run after the mountnfs.sh script

PATH=/sbin:/usr/sbin:/bin:/usr/bin
DESC="EPICS soft IOCs"
SCRIPTNAME=/etc/init.d/softIOC
HOST=`uname -n`


PROCSERV=/usr/local/bin/procServ
CONFFILE=/opt/IOC/softIOC/softiocs.$HOST
HOMEDIRS=/home/controls


# Check for config file
if [ ! -r $CONFFILE ]
then
        echo "Error: Can't find configuration file $CONFFILE!"
        exit 1
fi

#
# Functions that read in the configuration file
#
clear_options()
{
        for option in "CA_AUTO" "CA_ADDR" "CA_PORT" "IOC_USER" "PORT"
        do
                unset $option;
        done
}

evaluate_options()
{
        while [ $# != 0 ]
        do
                TAG=`echo $1 | tr [:lower:] [:upper:]`
                case "$TAG" in
                "#")            ;;
                "CA_AUTO" | "CA_ADDR" | "CA_PORT" | "COREDUMPSIZE" | \
                "HOMEDIR" | "BOOTDIR" | "IOC_USER" | "PORT" )
                                # Test the presence of values for the current option
                                OPTION=$TAG
                                shift
                                if [ -z $TAG -o $TAG = "#" ]
                                then
                                        echo "$CONFFILE: Value(s) required for $TAG.";
                                        exit 1
                                else
                                        VALUE=$1
                                        shift
                                fi
                                # If more values follow assign them too
                                while [ $1 != '#'  -a  $# != 0 ]
                                do
                                        VALUE="$VALUE $1"
                                        shift;
                                done
                                eval ${OPTION}=\$VALUE
                                ;;
                *)              echo "$CONFFILE: Unknown option $1."
                                exit 1
                esac
                shift
        done
}

default_options()
{
        # Set IOC defaults for options
        # (may be overridden in config file)
        IOC_LC=$1
        IOC_UC=`echo $1 | tr [:lower:] [:upper:]`

        if [[ "$IOC_LC" = "mdi"* ]]
            then
            TOP=DiagR3.14.9.0.1-Tornado2.2.1
        elif [[ "$IOC_LC" = *"p" ]]
            then
            TOP=MLS-Controls
        else
            TOP=BII-Controls/base-3-14
        fi

        BOOTDIR=/opt/IOC/$TOP/boot/$IOC_UC
        HOMEDIR=$HOMEDIRS/$IOC_LC
        PIDFILE=$HOMEDIR/$IOC_LC.pid
        ENVFILE=$HOMEDIR/$IOC_LC.env
        IOC_USER=$IOC_LC
}

assign_options()
{
        # Find $TAG section
        # Remove comments
        # Remove leading and trailing whitespace
        # Remove $TAG: tag
        # Join lines ending with a "\"
        # Mark end of option with a "#"
        # Remove unnecessary whitespace
        TAG=$1
        SECTION=`sed -n "/^$TAG:/I,/^[\t ]*$/p" $CONFFILE | \
                 sed -n '/^[^#]/p' | \
                 sed -e 's/^[ \t]*//' -e 's/[ \t]*$//' \
                     -e "s/$TAG://I" \
                     -e :a -e '/\\\\$/N; s/\\\\\\n//; ta' \
                     -e 's/$/ \#/' \
                     -e 's/[\t ]/ /g'`
        evaluate_options $SECTION
}

get_iocs()
{
        # Get IOCs from command line or AUTO: entry in configuration file
        # Test for matching section in configuration file
        if [ $# = 0 ]
        then
                TEST_LIST=`grep -i '^AUTO:' "$CONFFILE" | cut -d: -f2- | tr [:upper:] [:lower:]`
        else
                TEST_LIST="$@"
        fi

        CHECKED_LIST=""
        for IOC in $TEST_LIST
        do
                grep -qi "^$IOC:" $CONFFILE
                if [ $? = 0 ]
                then
                        CHECKED_LIST="$CHECKED_LIST $IOC"
                fi
        done
        echo $CHECKED_LIST
}

set_cmdenvopts()
{
        # Set up the environment setup string

        SETENV="LINES=60 "`test ! -z "$CA_AUTO" && echo "export EPICS_CA_AUTO_ADDR_LIST=\"$CA_AUTO\";"`
        SETENV="$SETENV "`test ! -z "$CA_ADDR" && echo "export EPICS_CA_ADDR_LIST=\"$CA_ADDR\";"`
        SETENV="$SETENV "`test ! -z "$CA_PORT" && echo "export EPICS_CA_SERVER_PORT=\"$CA_PORT\";"`
        SETENV="$SETENV "`test ! -z "$BOOTDIR" && echo "export BOOTDIR=\"$BOOTDIR\";"`

        # Set up the options for the procserv program

        PROCSERVOPTS=`test ! -z "$IOC_USER" && echo "-n \"$IOC_USER\""`
        PROCSERVOPTS="$PROCSERVOPTS "`test ! -z "$COREDUMPSIZE" && echo "--coresize \"$COREDUMPSIZE\""`
        PROCSERVOPTS="$PROCSERVOPTS -q -c $BOOTDIR -p $PIDFILE -i ^D^C^] $PORT"
}

#
# Function that starts the daemon/service
#
do_start()
{
        # Return
        #   0 if daemon has been started
        #   1 if daemon was already running
        #   2 if daemon could not be started
        # Add code here, if necessary, that waits for the process to be ready
        # to handle requests from services started subsequently which depend
        # on this one.  As a last resort, sleep for some time.

        echo -n "Starting soft IOCs ... "
        MYIOCS=`get_iocs $@`
        [ "$MYIOCS" = "" ] && echo -n "<none> "
        for IOC in $MYIOCS
        do
                echo -n "$IOC "
                clear_options
                default_options "$IOC"
                assign_options "GLOBAL"
                assign_options "$IOC"
                set_cmdenvopts

                if [ -d $BOOTDIR ]
                    then
                    if [ -d $HOMEDIR ]
                        then

                        sudo -H -u $IOC sh -c "$SETENV (env > $ENVFILE; /sbin/start-stop-daemon --start --quiet --chdir $BOOTDIR \
                            --pidfile $PIDFILE --startas $PROCSERV --name procServ --test > /dev/null)"
                        if [ "$?" = 1 ]
                            then
                            echo -n "<was running> "
                            else
                            sudo -H -u $IOC sh -c "$SETENV (env > $ENVFILE; /sbin/start-stop-daemon --start --quiet --chdir $BOOTDIR \
                                --pidfile $PIDFILE --startas $PROCSERV --name procServ -- $PROCSERVOPTS ./st.cmd)"
                            if [ "$?" = 1 ]
                                then
                                echo -n "<failed> "
                            fi
                        fi

                    else
                        echo -e "\nWarning: Home directory $HOMEDIR does not exist! Ignoring $IOC"
                    fi
                else
                        echo -e "\nWarning: Boot directory $BOOTDIR does not exist! Ignoring $IOC"
                fi
        done
        echo "... done."
}

#
# Function that stops the daemon/service
#
do_stop()
{
        # Return
        #   0 if daemon has been stopped
        #   1 if daemon was already stopped
        #   2 if daemon could not be stopped
        #   other if a failure occurred

        echo -n "Stopping soft IOCs ... "
        MYIOCS=`get_iocs $@`
        [ "$MYIOCS" = "" ] && echo -n "<none> "
        for IOC in $MYIOCS
        do
                echo -n "$IOC "
                clear_options
                default_options "$IOC"
                assign_options "GLOBAL"
                assign_options "$IOC"
                set_cmdenvopts

                sudo -H -u $IOC sh -c "/sbin/start-stop-daemon --stop --quiet --pidfile $PIDFILE --name procServ --test > /dev/null"
                if [ $? = 1 ]
                    then
                    echo -n "<not running> "
                    else
                    sudo -H -u $IOC sh -c "/sbin/start-stop-daemon --stop --quiet --retry=TERM/30/KILL/5 --pidfile $PIDFILE --name procServ"
                    if [ $? = 1 ]
                        then
                        echo -n "<failed> "
                    else
                        sudo -H -u $IOC sh -c "rm -f $PIDFILE"
                    fi
                fi
        done
        echo "... done."
}

#
# Function that sends a SIGHUP to the daemon/service
#
do_reload() {
        #
        # If the daemon can reload its configuration without
        # restarting (for example, when it is sent a SIGHUP),
        # then implement that here.
        #
#       start-stop-daemon --stop --signal 1 --quiet --pidfile $PIDFILE --name $NAME
#       return 0

        echo "Restarting soft IOCs ... "
        STARTDIR=$PWD
        IOCS=`get_iocs $@`
        [ "$IOCS" = "" ] && echo -n "<none> "
        for IOC in $IOCS
        do
                echo -n "$IOC "
                clear_options
                default_options "$IOC"
                assign_options "GLOBAL"
                assign_options "$IOC"
                if [ -d $BOOTDIR ]
                then
                        cd "$BOOTDIR"
# restart it!
                        echo -e "\ndebug: Reloading ioc $IOC"
                        cd "$STARTDIR"
                else
                        echo -e "\nWarning: Boot directory $BOOTDIR does not exist! Entry for $NET ignored!"
                fi
        done
        echo "... done."
}


COMMAND=$1
shift
IOCS=`echo $@ | tr [:upper:] [:lower:]`

case "$COMMAND" in
  start)
        do_start $IOCS
        ;;
  stop)
        do_stop $IOCS
        ;;
  #reload|force-reload)
        #
        # If do_reload() is not implemented then leave this commented out
        # and leave 'force-reload' as an alias for 'restart'.
        #
        #log_daemon_msg "Reloading $DESC" "$NAME"
        #do_reload
        #log_end_msg $?
        #;;
  restart|force-reload)
        #
        # If the "reload" option is implemented then remove the
        # 'force-reload' alias
        #
        do_stop $IOCS
        sleep 1
        do_start $IOCS
        ;;
  *)
        #echo "Usage: $SCRIPTNAME {start|stop|restart|reload|force-reload}" >&2
        echo "Usage: $SCRIPTNAME {start|stop|restart|force-reload} [iocs ...]" >&2
        exit 3
        ;;
esac
```
