# Troubleshooting

## When Clients Do Not Connect to Their Server

### Client and Server Broadcast Addresses Don't Match

Verify that the broadcast addresses are identical on the server's host and on
the client's host. This can be checked on UNIX with `netstat -i` or `ifconfig
-a`; on vxWorks with `ifShow`; and on windows with `ipconfig`. It is normal for
the broadcast addresses to not be identical if the client and server are not
directly attached to the same IP subnet, and in this situation the
{envvar}`EPICS_CA_ADDR_LIST` must be set. Otherwise, if the client and server are
intended to be on the same IP subnet, then the problem may be that the IP
netmask is incorrectly set in the network interface configuration. On most
operating systems, when the host's IP address is configured, the host's IP
subnet mask is also configured.

### Client Isn't Configured to Use the Server's Port

Verify that the client and server are using the same UDP port. Check the
server's port by running {samp}`netstat -a | grep {nnn}` where *nnn* is the
port number configured in the client. If you do not set
{envvar}`EPICS_CA_SERVER_PORT` or {envvar}`EPICS_CAS_SERVER_PORT` then the
default port will be 5064.

(unicast)=
### Unicast Addresses in the EPICS_CA_ADDR_LIST Does not Reliably Contact Servers Sharing the Same UDP Port on the Same Host

Two servers can run on the same host with the same server port number,
but there are restrictions. If the host has a modern IP kernel it is
possible to have two or more servers share the same UDP port. It is not
possible for these servers to run on the same host using the same TCP
port. If the CA server library detects that a server is attempting to
start on the same port as an existing CA server then both servers will
use the same UDP port, and the 2nd server will be allocated an ephemeral
TCP port. Clients can be configured to use the same port number for both
servers. They will locate the 2nd server via the shared UDP port, and
transparently connect to the 2nd server's ephemeral TCP port. Be aware
however that If there are two server's running on the same host sharing
the same UDP port then they will both receive UDP search requests sent
as broadcasts, but unfortunately (due to a weakness of most IP kernel
implementations) only one of the servers will typically receive UDP
search requests sent to unicast addresses (i.e. a single specific
host's ip address).

### Client Does not See Server's Beacons

Two conclusions deserve special emphasis. *First, if a client does not
see the server's beacons, then it will use additional network and
server resources sending periodic state-of-health messages.* *Second, if
a client does not see a newly introduced server's beacon, then it will
take up to {envvar}`EPICS_CA_MAX_SEARCH_PERIOD` to find that newly introduced
server.* Also, starting with EPICS R3.14.7 the client library does *not*
suspend searching for a channel after 100 unsuccessful attempts until a
beacon anomaly is seen. Therefore, if the client library is from before
version R3.14.7 of EPICS and it timed out attempting to find a server
whose beacon can't be seen by the client library then the client
application might need to be restarted in order to connect to this new
beacon-out-of-range server. The typical situation where a client would
not see the server's beacon might be when the client isn't on the same
IP subnet as the server, and the client's {envvar}`EPICS_CA_ADDR_LIST` was
modified to include a destination address for the server, but the
server's beacon address list was not modified so that its beacons are
received by the client.

### A Server's IP Address Was Changed

When communication over a virtual circuit times out, then each channel
attached to the circuit enters a disconnected state and the disconnect
callback handler specified for the channel is called. However, the
circuit is not disconnected until TCP/IP's internal, typically long
duration, keep alive timer expires. The disconnected channels remain
attached to the beleaguered circuit and no attempt is made to search
for, or to reestablish, a new circuit. If, at some time in the future,
the circuit becomes responsive again, then the attached channels enter a
connected state again and reconnect callback handlers are called. Any
monitor subscriptions that received an update message while the channel
was disconnected are also refreshed. If at any time the library receives
an indication from the operating system that a beleaguered circuit has
shutdown or was disconnected then the library will immediately reattempt
to find servers for each channel and connect circuits to them.

A well known negative side effect of the above behavior is that CA
clients will wait the full (typically long) duration of TCP/IP's
internal keep alive timer prior to reconnecting under the following
scenario (all of the following occur):

-   An server's (IOC's) operating system crashes (or is abruptly
    turned off) or a vxWorks system is stopped by any means
-   This operating system does not immediately reboot using the same IP
    address
-   A duplicate of the server (IOC) is started appearing at a different
    IP address

It is unlikely that any rational organization will advocate the above
scenario in a production system. Nevertheless, there *are* opportunities
for users to become confused during control system *development*, but it
is felt that the robustness improvements justify isolated confusion
during the system integration and checkout activities where the above
scenarios are most likely to occur.

Contrast the above behavior with the CA client library behavior of
releases prior to R3.14.5 where the beleaguered circuit was immediately
closed when communication over it timed out. Any attached channels were
immediately searched for, and after successful search responses arrived
then attempts were made to build a new circuit. This behavior could
result in undesirable resource consumption resulting from periodic
circuit setup and teardown overhead (thrashing) during periods of CPU /
network / IP kernel buffer congestion.

## Put Requests Just Prior to Process Termination Appear to be Ignored

Short lived CA client applications that issue a CA put request and then
immediately exit the process (return from `main` or call `exit`) may
find that there request isn't executed. To guarantee that the request
is sent call `ca_flush_io()` followed by `ca_context_destroy()` prior to
terminating the process.

## ENOBUFS Messages

Many Berkley UNIX derived Internet Protocol (IP) kernels use a memory
management scheme with a fixed sized low level memory allocation quantum
called an "mbuf". Messages about `ENOBUFS` are an indication that
your IP kernel is running low on mbuf buffers. An IP kernel mbuf
starvation situation may lead to temporary IP communications stalls or
reduced throughput. This issue has to date been primarily associated
with vxWorks systems where mbuf starvation on earlier vxWorks versions
is rumored to lead to permanent IP communications stalls which are
resolved only by a system reboot. IP kernels that use mbufs frequently
allow the initial and maximum number of mbufs to be configured. Consult
your OS's documentation for configuration procedures which vary between
OS and even between different versions of the same OS.

### Contributing Circumstances

-   The total number of connected clients is high. Each active socket
    requires dedicated mbufs for protocol control blocks, and for any
    data that might be pending in the operating system for transmission
    to Channel Access or to the network at a given instant. If you
    increase the vxWorks limit on the maximum number of file descriptors
    then it may also be necessary to increase the size of the mbuf pool.

-   The server has multiple connections where the server's sustained
    event (monitor subscription update) production rate is higher than
    the client's or the network's sustained event consumption rate.
    This ties up a per socket quota of mbufs for data that are pending
    transmission to the client via the network. In particular, if there
    are multiple clients that subscribe for monitor events but do not
    call `ca_pend_event()` or `ca_poll()` to process their CA input
    queue, then a significant mbuf consuming backlog can occur in the
    server.

-   The server does not get a chance to run (because some other higher
    priority thread is running) and the CA clients are sending a high
    volume of data over TCP or UDP. This ties up a quota of mbufs for
    each socket in the server that isn't being reduced by the server's
    socket read system calls.

-   The server has multiple stale connections. Stale connections occur
    when a client is abruptly turned off or disconnected from the
    network, and an internal "keepalive" timer has not yet expired for
    the virtual circuit in the operating system, and therefore mbufs may
    be dedicated to unused virtual circuits. This situation is made
    worse if there are active monitor subscriptions associated with
    stale connections which will rapidly increase the number of
    dedicated mbufs to the quota available for each circuit.
-   When sites switch to the vxWorks 5.4 IP kernel they frequently run
    into network pool exhaustion problems. This may be because the
    original vxWorks IP kernel expanded the network pool as needed at
    runtime while the new kernel's pool is statically configured at
    compile time, and does *not* expand as needed at runtime. Also, at
    certain sites problems related to vxWorks network driver pool
    exhaustion have also been reported (this can also result in ENOBUF
    diagnostic messages).

### Related Diagnostics

-   The EPICS command `casr [interest level]` displays information
    about the CA server and how many clients are connected.
-   The vxWorks command `inetstatShow` indicates how many bytes are
    pending in `mbufs` and indirectly (based on the number of circuits
    listed) how many `mbuf` based protocol control blocks have been
    consumed. The vxWorks commands (availability depending on vxWorks
    version) `mbufShow`, `netStackSysPoolShow`, and `netStackDataPoolShow`
    indicate how much space remains in the network stack pool.
-   The RTEMS command `netstat [interest level]` displays network
    information including mbuf consumption statistics.

## Server Subscription Update Queuing

If the subscription update producer in the server produces subscription
updates faster than the subscription update consumer in the client
consumes them, then events have to be discarded if the buffering in the
server isn't allowed to grow to an infinite size. This is a law of
nature -- based on queuing theory of course.

What is done depends on the version of the CA server. All server
versions place quotas on the maximum number of subscription updates
allowed on the subscription update queue at any given time. If this
limit is reached, an intervening update is discarded in favor of a more
recent update. Depending on the version of the server, rapidly updating
subscriptions are or are not allowed to cannibalize the quotas of slow
updating subscriptions in limited ways. Nevertheless, there is always
room on the queue for at least one update for each subscription. This
guarantees that the most recent update is always sent.

Adding further complication, the CA client library also implements a
primitive type of flow control. If the client library sees that it is
reading a large number of messages one after another w/o intervening
delay it knows that it is not consuming events as fast as they are
produced. In that situation it sends a message telling the server to
temporarily stop sending subscription update messages. When the client
catches up it sends another message asking the server to resume with
subscription updates. This prevents slow clients from getting time
warped, but also guarantees that intervening events are discarded until
the slow client catches up.

There is currently no message on the IOC's console when a particular
client is slow on the uptake. A message of this type used to exist many
years ago, but it was a source of confusion (and what we will call
message noise) so it was removed.

There is unfortunately no field in the protocol allowing the server to
indicate that an intervening subscription update was discarded. We
should probably add that capability in a future version. Such a feature
would, for example, be beneficial when tuning an archiver installation.
