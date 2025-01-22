# Configuration

## Why Reconfigure Channel Access

Typical reasons to reconfigure EPICS Channel Access:

-   Two independent control systems must share a network without fear of
    interaction
-   A test system must not interact with an operational system
-   Use of address lists instead of broadcasts for name resolution and
    server beacons
-   Control system occupies multiple IP subnets
-   Nonstandard client disconnect time outs or server beacon intervals
-   Specify the local time zone
-   Transport of large arrays

(ca-client-env-vars)=
## EPICS Environment Variables

All Channel Access (CA) configuration occurs through EPICS environment
variables. When searching for an EPICS environment variable EPICS first
looks in the environment using the ANSI C getenv() call. If no matching
variable exists then the default specified in the EPICS build system
configuration files is used.

Environment variables are set differently depending on the command line
shell that is in use.

:C shell: `setenv EPICS_CA_ADDR_LIST 1.2.3.4`
:Bash: `export EPICS_CA_ADDR_LIST=1.2.3.4`
:vxWorks shell: `putenv ( "EPICS_CA_ADDR_LIST=1.2.3.4" )`
:DOS command line: `set EPICS_CA_ADDR_LIST=1.2.3.4`
:Windows NT / 2000 / XP: control panel / system / environment tab

::: {envvar} EPICS_CA_ADDR_LIST

:Syntax: `{N.N.N.N N.N.N.N:P ...}`
:Default: None
:::

::: {envvar} EPICS_CA_AUTO_ADDR_LIST

:Syntax: `{YES, NO}`
:Default: `YES`
:::

::: {envvar} EPICS_CA_NAME_SERVERS

:Syntax: `{N.N.N.N N.N.N.N:P ...}`
:Default: None
:::

::: {envvar} EPICS_CA_CONN_TMO

:Syntax: float greater than 0.1 seconds
:Default: 30.0
:::

::: {envvar} EPICS_CA_BEACON_PERIOD

:Syntax: float greater than 0.1 seconds
:Default: 15.0
:::

::: {envvar} EPICS_CA_REPEATER_PORT

:Syntax: integer greater than 5000
:Default: 5065
:::

::: {envvar} EPICS_CA_SERVER_PORT

:Syntax: integer greater than 5000
:Default: 5064
:::

:::::: {envvar} EPICS_CA_MAX_ARRAY_BYTES

:Syntax: integer greater than 16384
:Default: 16384

::: {versionadded} R3.14
:::

Determines the size of the largest array that may pass through CA. Prior to
this version only arrays smaller than 16k bytes could be transfered. The CA
libraries maintains a free list of 16384 byte network buffers that are used for
ordinary communication. If {envvar}`EPICS_CA_MAX_ARRAY_BYTES` is larger than
16384 then a second free list of larger data buffers is established and used
only after a client send its first large array request.

The CA client library uses {envvar}`EPICS_CA_MAX_ARRAY_BYTES` to determines the
maximum array that it will send or receive. Likewise, the CA server uses
{envvar}`EPICS_CA_MAX_ARRAY_BYTES` to determine the maximum array that it may send
or receive. The client does not influence the server's message size
quotas and visa versa. In fact the value of {envvar}`EPICS_CA_MAX_ARRAY_BYTES`
need not be the same in the client and the server. If the server
receives a request which is too large to read or respond to in entirety
then it sends an exception message to the client. Likewise, if the CA
client library receives a request to send an array larger than
{envvar}`EPICS_CA_MAX_ARRAY_BYTES` it will return ECA_TOLARGE.

A common mistake is to correctly calculate the maximum datum size in
bytes by multiplying the number of elements by the size of a single
element, but neglect to add additional bytes for the compound data types
(for example `DBR_GR_DOUBLE`) commonly used by the more sophisticated
client side applications.

::: {seealso}
{envvar}`EPICS_CA_AUTO_ARRAY_BYTES`
:::

::::::

:::::: {envvar} EPICS_CA_AUTO_ARRAY_BYTES

:Syntax: `{YES, NO}`
:Default: `YES`

::: {versionadded} R3.16.1
:::

Ignore {envvar}`EPICS_CA_MAX_ARRAY_BYTES` and attempt to allocate network
buffer space as needed by the particular client connection using `malloc`.
Setting `EPICS_CA_AUTO_ARRAY_BYTES=NO` will configure the software to respect
the {envvar}`EPICS_CA_MAX_ARRAY_BYTES` setting as described below instead.

::::::

::: {envvar} EPICS_CA_MAX_SEARCH_PERIOD

:Syntax: float greater than 60 seconds
:Default: 300
:::

::: {envvar} EPICS_CA_MCAST_TTL

:Syntax: float greater than 1
:Default: 1
:::

::: {envvar} EPICS_TS_MIN_WEST

:Syntax: integer between -720 and 720 minutes
:Default: 360
:::

## CA and Wide Area Networks

Normally in a local area network (LAN) environment CA discovers the
address of the host for an EPICS process variable by broadcasting frames
containing a list of channel names (CA search messages) and waiting for
responses from the servers that host the channels identified. Likewise
CA clients efficiently discover that CA servers have recently joined the
LAN or disconnected from the LAN by monitoring periodically broadcasted
beacons sent out by the servers. Since hardware broadcasting requires
special hardware capabilities, we are required to provide additional
configuration information when EPICS is extended to operate over a wide
area network (WAN).

## IP Network Administration Background Information

Channel Access is implemented using Internet protocols (IP). IP
addresses are divided into host and network portions. The boundary
between each portion is determined by the IP netmask. Portions of the IP
address corresponding to zeros in the netmask specify the hosts address
within an IP subnet. Portions of the IP address corresponding to binary
ones in the netmask specify the address of a host's IP subnet. Normally
the scope of a broadcasted frame will be limited to one IP subnet.
Addresses with the host address portion set to all zeros or all ones are
special. Modern IP kernel implementations reserve destination addresses
with the host portion set to all ones for the purpose of addressing
broadcasts to a particular subnet. In theory we can issue a broadcast
frame on any broadcast capable LAN within the interconnected Internet by
specifying the proper subnet address combined with a host portion set to
all ones. In practice these "directed broadcasts" are frequently
limited by the default router configuration. The proper directed
broadcast address required to reach a particular host can be obtained by
logging into that host and typing the command required by your local
operating environment. Ignore the loop back interface and use the
broadcast address associated with an interface connected to a path
through the network to your client. Typically there will be only one
Ethernet interface.

:UNIX: `ifconfig -a`
:vxWorks: `ifShow`
:Windows: `ipconfig`

IP ports are positive integers. The IP address, port number, and
protocol type uniquely identify the source and destination of a
particular frame transmitted between computers. Servers are typically
addressed by a well known port number. Clients are assigned a unique
ephemeral port number during initialization. IP ports below 1024 are
reserved for servers that provide standardized facilities such as mail
or file transfer. Port number between 1024 and 5000 are typically
reserved for ephemeral port number assignments.

## IP port numbers

The two default IP port numbers used by Channel Access may be
reconfigured. This might occur when a site decides to set up two or more
completely independent control systems that will share the same network.
For instance, a site might set up an operational control system and a
test control system on the same network. In this situation it is
desirable for the test system and the operational system to use
identical PV names without fear of collision. A site might also
configure the CA port numbers because some other facility is already
using the default port numbers. The default Channel Access port numbers
have been registered with IANA.

| Purpose                                 | Default | Environment Variable             |
|-----------------------------------------|---------|----------------------------------|
| CA Server                               | 5064    | {envvar}`EPICS_CA_SERVER_PORT`   |
| CA Beacons (sent to CA repeater daemon) | 5065    | {envvar}`EPICS_CA_REPEATER_PORT` |

If a client needs to communicate with two servers that are residing at
different port numbers then an extended syntax may be used with the
{envvar}`EPICS_CA_ADDR_LIST` environment variable. See [](#wan-environment) below.

## Firewalls

If you want channel access clients on a machine to be able to see
beacons and replies to broadcast PV search requests, you need to permit
inbound UDP packets with source port {envvar}`EPICS_CA_SERVER_PORT` (default is
5064) or destination port {envvar}`EPICS_CA_REPEATER_PORT` (default is 5065). On
systems using iptables this can be accomplished by rules like

         -A INPUT -s 192.168.0.0/22 -p udp --sport 5064 -j ACCEPT
         -A INPUT -s 192.168.0.0/22 -p udp --dport 5065 -j ACCEPT

If you want channel access servers (e.g. "soft IOCs") on a machine to
be able to be seen by clients, you need to permit inbound TCP or UDP
packets with destination port {envvar}`EPICS_CA_SERVER_PORT` (default is 5064). On
systems using iptables this can be accomplished by rules like

         -A INPUT -s 192.168.0.0/22 -p udp --dport 5064 -j ACCEPT
         -A INPUT -s 192.168.0.0/22 -p tcp --dport 5064 -j ACCEPT

In all cases the `-s 192.168.0.0/22` specifies the range of addresses
from which you wish to accept packets.

## WAN Environment

When the CA client library connects a channel it must first determine
the IP address of the server the channels Process Variable resides on.
To accomplish this the client sends name resolution (search) requests to
a list of server destination addresses. These server destination
addresses can be IP unicast addresses (individual host addresses) or IP
broadcast addresses. Each name resolution (search) request contains a
list of Process Variable names.If one of the servers reachable by this
address list knows the IP address of a CA server that can service one or
more of the specified Process Variables, then it sends back a response
containing the server's IP address and port number.

During initialization CA builds the list of server destination addresses
used when sending CA client name resolution (search) requests. This
table is initialized by introspecting the network interfaces attached to
the host. For each interface found that is attached to a broadcast
capable IP subnet, the broadcast address of that subnet is added to the
list. For each point to point interface found, the destination address
of that link is added to the list. This automatic server address list
initialization can be disabled if the EPICS environment variable
{envvar}`EPICS_CA_AUTO_ADDR_LIST` exists and its value is either `no` or `NO`.
The typical default is to enable network interface introspection driven
initialization with {envvar}`EPICS_CA_AUTO_ADDR_LIST` set to `YES` or `yes`.

Following network interface introspection, any IP addresses specified in
the EPICS environment variable {envvar}`EPICS_CA_ADDR_LIST` are added to the list
of destination addresses for CA client name resolution requests. In an
EPICS system crossing multiple subnets the {envvar}`EPICS_CA_ADDR_LIST` must be
set so that CA name resolution (search requests) frames pass from CA
clients to the targeted CA servers unless a CA proxy (gateway) is
installed. The addresses in {envvar}`EPICS_CA_ADDR_LIST` may be dotted IP
addresses or host names if the local OS has support for host name to IP
address translation. When multiple names are added to {envvar}`EPICS_CA_ADDR_LIST`
they must be separated by white space. There is no requirement that the
addresses specified in the {envvar}`EPICS_CA_ADDR_LIST` be broadcast addresses,
but this will often be the most convenient choice.

For any IP addresses specified in the EPICS environment variable
{envvar}`EPICS_CA_NAME_SERVERS`, TCP connections are opened and used for CA client
name resolution requests. (Thus, broadcast addresses are not allowed in
{envvar}`EPICS_CA_NAME_SERVERS`.) When used in combination with an empty
{envvar}`EPICS_CA_ADDR_LIST` and {envvar}`EPICS_CA_AUTO_ADDR_LIST` set to `NO`, Channel
Access can be run without using UDP for name resolution. Such an
TCP-only mode allows for Channel Access to work e.g. through SSH
tunnels.

:C shell: `setenv EPICS_CA_ADDR_LIST "1.2.3.255 8.9.10.255"`
:bash: `export EPICS_CA_ADDR_LIST="1.2.3.255 8.9.10.255"`
:vxWorks: `putenv ( "EPICS_CA_ADDR_LIST=1.2.3.255 8.9.10.255" )`

If a client needs to communicate with two servers that are residing at
different port numbers then an extended syntax may be used with the
{envvar}`EPICS_CA_ADDR_LIST` environment variable. Each host name or IP address in
the {envvar}`EPICS_CA_ADDR_LIST` may be immediately followed by a colon and an IP
port number without intervening whitespace. Entries that do not specify
a port number will default to {envvar}`EPICS_CA_SERVER_PORT`.

:C shell: `setenv EPICS_CA_ADDR_LIST "1.2.3.255 8.9.10.255:10000"`

### Routing Restrictions on vxWorks Systems

Frequently vxWorks systems boot by default with routes limiting access
only to the local subnet. If a EPICS system is operating in a WAN
environment it may be necessary to configure routes into the vxWorks
system which enable a vxWorks based CA server to respond to requests
originating outside its subnet. These routing restrictions can also
apply to vxWorks base CA clients communicating with off subnet servers.
An EPICS system manager can implement an rudimentary, but robust, form
of access control for a particular host by not providing routes in that
host that reach outside of a limited set of subnets. See "routeLib" in
the vxWorks reference manual.

## Disconnect Time Out Interval

If the CA client library does not see a beacon from a server that it is
connected to for {envvar}`EPICS_CA_CONN_TMO` seconds then an state-of-health
message is sent to the server over TCP/IP. If this state-of-health
message isn't promptly replied to then the client library will conclude
that channels communicating with the server are no longer responsive and
inform the CA client side application via function callbacks. The
parameter {envvar}`EPICS_CA_CONN_TMO` is specified in floating point seconds. The
default is typically 30 seconds. For efficient operation it is
recommended that {envvar}`EPICS_CA_CONN_TMO` be set to no less than twice the
value specified for {envvar}`EPICS_CA_BEACON_PERIOD`.

Prior to EPICS R3.14.5 an unresponsive server implied an immediate TCP
circuit disconnect, immediate resumption of UDP based search requests,
and immediate attempts to reconnect. There was concern about excessive
levels of additional activity when servers are operated close to the
edge of resource limitations. Therefore with version R3.14.5 and greater
the CA client library continues to inform client side applications when
channels are unresponsive, but does not immediately disconnect the TCP
circuit. Instead the CA client library postpones circuit shutdown until
receiving indication of circuit disconnect from the IP kernel. This can
occur either because a server is restarted or because the IP kernel's
internal TCP circuit inactivity keep alive timer has expired after a
typically long duration (as is appropriate for IP based systems that
need to avoid thrashing during periods of excessive load). The net
result is less search and TCP circuit setup and shutdown activity during
periods of excessive load.

## Dynamic Changes in the CA Client Library Search Interval

The CA client library will continuously attempt to connect any CA
channels that an application has created until it is successful. The
library periodically queries the server destination address list
described above with name resolution requests for any unresolved
channels. Since this address list frequently contains broadcast
addresses, and because nonexistent process variable names are frequently
configured, or servers may be temporarily unavailable, then it is
necessary for the CA client library internals to carefully schedule
these requests in time to avoid introducing excessive load on the
network and the servers.

When the CA client library has many channels to connect, and most of its
name resolution requests are responded to, then it sends name resolution
requests at an interval that is twice the estimated round trip interval
for the set of servers responding, or at the minimum delay quantum for
the operating system - whichever is greater. The number of UDP frames
per interval is also dynamically adjusted based on the past success
rates.

If a name resolution request is not responded to, then the client
library doubles the delay between name resolution attempts and reduces
the number of requests per interval. The maximum delay between attempts
is limited by {envvar}`EPICS_CA_MAX_SEARCH_PERIOD`
(see [](#configuring-the-maximum-search-period)).
Note however that prior to R3.14.7, if
the client library did not receive any responses over a long interval it
stopped sending name resolution attempts altogether until a beacon
anomaly was detected (see below).

The CA client library continually estimates the beacon period of all
server beacons received. If a particular server's beacon period becomes
significantly shorter or longer then the client is said to detect a
beacon anomaly. The library boosts the search interval for unresolved
channels when a beacon anomaly is seen or when *any* successful search
response is received, but with a longer initial interval between
requests than is used when the application creates a channel. Creation
of a new channel does *not* (starting with EPICS R3.14.7) change the
interval used when searching for preexisting unresolved channels. The
program "casw" prints a message on standard out for each CA client
beacon anomaly detect event.

::: {seealso}
[](troubleshooting.md#client-does-not-see-servers-beacons)
:::

## Configuring the Maximum Search Period

The rate at which name resolution (search) requests are sent
exponentially backs off to a plateau rate. The value of this plateau has
an impact on network traffic because it determines the rate that clients
search for channel names that are miss-spelled or otherwise don't exist
in a server. Furthermore, for clients that are unable to see the beacon
from a new server, the plateau rate may also determine the maximum
interval that the client will wait until discovering a new server.

Starting with EPICS R3.14.7 this maximum search rate interval plateau in
seconds is determined by the {envvar}`EPICS_CA_MAX_SEARCH_PERIOD` environment
variable.

::: {seealso}
[](troubleshooting.md#client-does-not-see-servers-beacons)
:::

## The CA Repeater

When several client processes run on the same host it is not possible
for all of them to directly receive a copy of the server beacon messages
when the beacon messages are sent to unicast addresses, or when legacy
IP kernels are still in use. To avoid confusion over these restrictions
a special UDP server, the CA Repeater, is automatically spawned by the
CA client library when it is not found to be running. This program
listens for server beacons sent to the UDP port specified in the
{envvar}`EPICS_CA_REPEATER_PORT` parameter and fans any beacons received out to
any CA client program running on the same host that have registered
themselves with the CA Repeater. If the CA Repeater is not already
running on a workstation, then the {program}`caRepeater` program must be in
your path before using the CA client library for the first time.

If a host based IOC is run on the same workstation with standalone CA
client processes, then it is probably best to start the caRepeater
process when the workstation is booted. Otherwise it is possible for the
standalone CA client processes to become dependent on a CA repeater
started within the confines of the host based IOC. As long as the host
based IOC continues to run there is nothing wrong with this situation,
but problems could arise if this host based IOC process exits before the
standalone client processes which are relying on its CA repeater for
services exit.

Since the repeater is intended to be shared by multiple clients then it
could be argued that it makes less sense to set up a CA repeater that
listens for beacons on only a subset of available network interfaces. In
the worst case situation the client library might see beacon anomalies
from servers that it is not interested in. Modifications to the CA
repeater forcing it to listen only on a subset of network interfaces
might be considered for a future release if there appear to be
situations that require it.

## Configuring the Time Zone

::: {note}
Starting with EPICS R3.14 all of the libraries in the EPICS base
distribution rely on facilities built into the operating system to
determine the correct time zone. Nevertheless, several programs commonly
used with EPICS still use the original "tssubr" library and therefore
they still rely on proper configuration of {envvar}`EPICS_TS_MIN_WEST`.
:::

While the CA client library does not translate between the local time
and the time zone independent internal storage of EPICS time stamps,
many EPICS client side applications call core EPICS libraries which
provide these services. To set the correct time zone users must compute
the number of positive minutes west of GMT (maximum 720 inclusive) or
the negative number of minutes east of GMT (minimum -720 inclusive).
This integer value is then placed in the variable {envvar}`EPICS_TS_MIN_WEST`.

| Time Zone      | EPICS_TS_MIN_WEST |
|----------------|-------------------|
| USA Eastern    | 300               |
| USA Central    | 360               |
| USA Mountain   | 420               |
| USA Pacific    | 480               |
| Alaska         | 540               |
| Hawaii         | 600               |
| Japan          | -540              |
| China          | -420              |
| Germany        | -120              |
| United Kingdom | 0                 |

(ca-server-env-vars)=
## Configuring a CA Server

::: {envvar} EPICS_CAS_SERVER_PORT

:Syntax: integer greater than 5000
:Default: {envvar}`EPICS_CA_SERVER_PORT`
:::

::: {envvar} EPICS_CAS_AUTO_BEACON_ADDR_LIST

:Syntax: `{YES, NO}`
:Default: {envvar}`EPICS_CA_AUTO_ADDR_LIST`
:::

::: {envvar} EPICS_CAS_BEACON_ADDR_LIST

:Syntax: `{N.N.N.N N.N.N.N:P ...}`
:Default: {envvar}`EPICS_CA_ADDR_LIST`
:::

::: {envvar} EPICS_CAS_BEACON_PERIOD

:Syntax: float greater than 0.1 seconds
:Default: {envvar}`EPICS_CA_BEACON_PERIOD`
:::

::: {envvar} EPICS_CAS_BEACON_PORT

:Syntax: integer greater than 5000
:Default: {envvar}`EPICS_CA_REPEATER_PORT`
:::

::: {envvar} EPICS_CAS_INTF_ADDR_LIST

:Syntax: `{N.N.N.N N.N.N.N:P ...}`
:Default: None
:::

::: {envvar} EPICS_CAS_IGNORE_ADDR_LIST

:Syntax: `{N.N.N.N N.N.N.N:P ...}`
:Default: None
:::

### Server Port

The server configures its port number from the {envvar}`EPICS_CAS_SERVER_PORT`
environment variable if it is specified. Otherwise the
{envvar}`EPICS_CA_SERVER_PORT` environment variable determines the server's port
number. Two servers can share the same UDP port number on the same
machine, but there are restrictions - see a [discussion of unicast
addresses and two servers sharing the same UDP port on the same
host](#unicast).

### Server Beacons

The {envvar}`EPICS_CAS_BEACON_PERIOD` parameter determines the server's beacon
period and is specified in floating point seconds. The default is
typically 15 seconds. See also [](#disconnect-time-out-interval) and
[](#dynamic-changes-in-the-ca-client-library-search-interval).

CA servers build a list of addresses to send beacons to during
initialization. If {envvar}`EPICS_CAS_AUTO_BEACON_ADDR_LIST` has the value `YES`
(the default) this list will be automatically populated with the
broadcast addresses of all network interfaces. However, if the user also
defines {envvar}`EPICS_CAS_INTF_ADDR_LIST` then beacon address list automatic
configuration is constrained to the network interfaces specified
therein, and therefore only the broadcast addresses of the specified LAN
interfaces, will be automatically configured.

If {envvar}`EPICS_CAS_BEACON_ADDR_LIST` is defined then its contents will be used
to augment any automatic configuration of the beacon address list.
Individual entries in {envvar}`EPICS_CAS_BEACON_ADDR_LIST` may override the
destination port number if `:nnn` follows the host name or IP address
there.

The {envvar}`EPICS_CAS_BEACON_PORT` parameter specifies the destination port for
server beacons. The only exception to this occurs when ports are
specified in {envvar}`EPICS_CAS_BEACON_ADDR_LIST` or possibly in
{envvar}`EPICS_CA_ADDR_LIST`. If {envvar}`EPICS_CAS_BEACON_PORT` is not specified then
beacons are sent to the port specified in {envvar}`EPICS_CA_REPEATER_PORT`.

### Binding a Server to a Limited Set of Network Interfaces

The parameter {envvar}`EPICS_CAS_INTF_ADDR_LIST` allows a ca server to bind itself
to, and therefore accept messages received by, a limited set of the
local host's network interfaces (each specified by its IP address). On
UNIX systems type `netstat -ie` (type `ipconfig` on windows) to see
a list of the local host's network interfaces. By default, the CA
server is accessible from all network interfaces configured into its
host.

Until R3.15.4 the CA server employed by iocCore did not implement the
{envvar}`EPICS_CAS_INTF_ADDR_LIST` feature.

Prior to R3.15.4 CA servers would build the beacon address list using
{envvar}`EPICS_CA_ADDR_LIST` if {envvar}`EPICS_CAS_BEACON_ADDR_LIST` was no set.

### Ignoring Process Variable Name Resolution Requests From Certain Hosts

Name resolution requests originating from any of the IP addresses
specified in the {envvar}`EPICS_CAS_IGNORE_ADDR_LIST` parameter are not replied
to. *In R3.14 and previous releases the CA server employed by iocCore
does not implement this feature.*

### Client Configuration that also Applies to Servers

::: {seealso}
- {envvar}`EPICS_CA_MAX_ARRAY_BYTES`
- [](#routing-restrictions-on-vxworks-systems).
:::
