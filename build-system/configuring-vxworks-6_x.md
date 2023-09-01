# Configuring vxWorks 6.x

{audience}`user, advanced`

## vxWorks 6.x Information

This page provides a advice on configuring and using the Wind River’s Workbench environment and the vxWorks 6.x RTOS with EPICS. If you discover any other information that ought to be published here, please [let me know](mailto:anj@anl.dot.gov).

Note that there is a [separate page](vxworks6_tornado) provided for users of vxWorks 5.x and Wind River’s Tornado.

[Tornado 2.2 and Linux](https://epics-controls.org/resources-and-support/documents/howto-documents/vxworks6/t2-2-linux/)

[PowerPC](https://epics-controls.org/resources-and-support/documents/howto-documents/vxworks6/powerpc/)

[Configuring WRS Tornado 2.x for EPICS](https://epics-controls.org/resources-and-support/documents/howto-documents/vxworks6/t20xconfig/)

### Configuring a vxWorks 6.x image

Using the Wind River Workbench to create a vxWorks image suitable for running EPICS IOCs, the following components are **required** in addition to the standard components included with a new vxWorks 6.x Image Project (System Image) with a PROFILE\_DEVELOPMENT Configuration Profile:

*   C++ components
    *   standard library
        *   C++ Iostreams and other … — INCLUDE\_CPLUS\_IOSTREAMS
*   Network Components (default)
    *   Network Applications (default)
        *   SNTP Components
            *   SNTP Client (daemon) — INCLUDE\_IPSNTPC  
                _Set the NTP server addresses under here. The primary server IPv4 address can be set to sysBootParams.had for the IOC to always use its boot host as an NTP server._
    *   Network Core Components (default)
        *   Backwards compatibility wrapper routines
            *   libc wrappers
                *   sntpcTimeGet wrapper — INCLUDE\_IPWRAP\_SNTPCTIMEGET
        *   network init — INCLUDE\_NET\_INIT
*   operating system components (default)
    *   IO system components (default)
        *   IO Subsystem Components
            *   Basic IO System
                *   max # open files in the system — NUM\_FILES  
                    _Configure this to more than the maximum number of CA sessions you expect need to connect into and out of this IOC at the same time. The CA protocol uses one file handle per client, and every additional network socket, serial port and other vxWorks device will use at least one._
    *   kernel components (default)
        *   unix compatable environment variables (default)
            *   install environment variable task create/delete hooks — ENV\_VAR\_USE\_HOOKS  
                _This variable must be set to FALSE._

The following components are **optional** but will often be wanted:

*   Network Components (default)
    *   Network Applications (default)
        *   SNTP Components
            *   INCLUDE\_IPSNTP\_CMD
        *   DNS Client — INCLUDE\_IPDNSC  
            _Set the DNS domain name and at least the DNS primary name server under here. The server can be set to sysBootParams.had for the IOC to always use its boot host as a DNS server_
    *   Network Core Components (default)
        *   Backwards compatibility wrapper routines
            *   libc wrappers
                *   arp utility wrapper — INCLUDE\_IPWRAP\_ARP
            *   utilslib wrappers
                *   ifShow wrapper — INCLUDE\_IPWRAP\_IFSHOW
                *   ifconfig wrapper — INCLUDE\_IPWRAP\_IFCONFIG
                *   netstat wrapper — INCLUDE\_IPWRAP\_NETSTAT
                *   ping wrapper — INCLUDE\_IPWRAP\_PING
                *   routec wrapper — INCLUDE\_IPWRAP\_ROUTECMD
*   development tool components (default)
    *   spy — INCLUDE\_SPY
*   operating system components (default)
    *   IO system components (default)
        *   NFS Components
            *   NFS client All — INCLUDE\_NFS\_CLIENT\_ALL

These components are included in the PROFILE\_DEVELOPMENT configuration by default but **not required** by EPICS so may safely be excluded:

*   Network Components (default)
    *   Network Core Components (default)
        *   Backwards compatibility wrapper routines
            *   libc wrappers
                *   getservbyname wrapper — INCLUDE\_IPWRAP\_GETSERVBYNAME
                *   getservbyport wrapper — INCLUDE\_IPWRAP\_GETSERVBYPORT
*   application components (default)
    *   application initialization — INCLUDE\_USER\_APPL
*   development tool components (default)
    *   Compiler support routines
        *   Diab compiler support routines — INCLUDE\_DIAB\_INTRINSICS
*   operating system components (default)
    *   ANSI C components (libc) (default)
        *   ANSI locale — INCLUDE\_ANSI\_LOCALE
        *   ANSI stdio extensions — INCLUDE\_ANSI\_STDIO\_EXTRA
    *   POSIX components
        *   POSIX timers (default) — INCLUDE\_POSIX\_TIMERS
        *   sigevent notification library — INCLUDE\_SIGEVENT
    *   Real Time Process components — FOLDER\_RTP
    *   SYSCTL Component — FOLDER\_SYSCTL

### vxWorks 6.6 GNU Header stdexcept

There is a bug in the GNU C++ header file stdexcept as delivered with vxWorks 6.6 which results in some undefined symbols when you try to load the IOC code. The header has been fixed in later vxWorks releases, and there may have been an official Wind River patch issued to fix this, but Erik Bjorklund has provided [this patch](https://epics.anl.gov/base/vxWorks6.6-gnu-stdexcept.patch) to address the problem.

### Adding a CR/CSR Master Window to the mv6100 BSP

Eric Bjorklund [gave a talk](https://epics.anl.gov/meetings/2006-06/RecDevDrv_Support/Support_for_CR-CSR_Addressing.pdf) at a EPICS collaboration meeting in June 2006 describing how he added support for accessing the VME CR/CSR address space to the mv6100 BSP.
