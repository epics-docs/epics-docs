# How to Configure Channel Access

## Basic Operation, One IOC on same subnet

Assume an IOC has a record `fred`, and you want to use `caget fred` or a similar CA client to read it.

When starting out with one IOC on the network, things are simple:

CA clients will by default broadcast name search requests to UDP port 5064 on the subnet. As long as the IOC is running on on any computer on that subnet, it should receive those search requests. Server and client will then establish a TCP connection, and data is exchanged.

## Multiple IOCs on different computers, but same subnet

If running multiple IOCs, each on their own computer, on the same subnet, the basic broadcast name search will still succeed, no change necessary.

## IOCs on different subnets

The default broadcast name search is limited to the subnet of the computer running the CA client. To reach IOCs on one or more additional subnets, the environment variable `EPICS_CA_ADDR_LIST` needs to be configured. It can list either the specific IP addresses of each IOC, or the broadcast address of their subnet. Note, however, that routers will often not forward broadcast requests, which suggests using specific IP addresses.

## Multiple IOCs on the same computer

When starting the first IOC on a computer, it will listen to name searches on UDP port 5064. When starting a second IOC on the same computer, it will also listen to name searches on UDP port 5064. Due to limitations in most network kernels, however, only the IOC started _last_ will actually receive UDP search requests that are sent to that computer, port 5064. As a workaround, you need to configure the `EPICS_CA_ADDR_LIST` to use the broadcast address of the respective subnet.

Alternatively, you can automatically set up iptables rules that will circumvent the problem. (See [How to Make Channel Access Reach Multiple Soft IOCs on a Linux Host](https://epics-controls.org/resources-and-support/documents/howto-documents/channel-access-reach-multiple-soft-iocs-linux/).)

## Multiple IOCs on the same computer but on a different subnet

Combining the last two points results in a problem: To reach multiple IOCs on the same computer, `EPICS_CA_ADDR_LIST` must be set to the broadcast address of that computer's subnet. If the IOCs' subnet is different from the CA client's subnet however, the broadcast search packets will not usually be forwarded by the intermediate network routers.

There are several options to solve this:

### Channel Access Gateway

The PV gateway, running on the subnet that has the desired IOCs, will use the broadcast address of that subnet in its `EPICS_CA_ADDR_LIST`, so it can reach all IOCs, including multiple IOCs running on the same computer, throughout that subnet. A CA client on a different subnet uses only `EPICS_CA_ADDR_LIST=ip-of-the-gateway` to directly reach the gateway, which is possible via routers.

In addition to establishing the basic connectivity, the gateway also offers IOC load reduction and it can add access security, for example limit write access.

### CA Nameserver

You can run a CA Name Server in the GUI subnet which knows about the IOCs and responds to search requests; in this case you would _not_ set the `EPICS_CA_ADDR_LIST` variables. This is almost equivalent to running a CA Gateway, but is slightly more robust because if the Nameserver process dies it wouldn't kill any existing connections.

### UDP Broadcast Packet Relay

If you have access to a machine with a network interface on both subnets you can run a program on it called [UDP Broadcast Packet Relay](https://www.joachim-breitner.de/udp-broadcast-relay/) to forward UDP broadcast packets between the subnets. For best performance you should run it twice, once for port 5064 and again for 5065. The first one will forward CA search requests between the subnets, while the second redistributes CA beacons which help channels reconnect faster after an IOC has been turned off for some time.

## Firewalls

Firewalls may need to be configured to pass UDP and TCP traffic on both ports 5064 and 5065.

The [Channel Access Reference Manual](https://epics.anl.gov/base/R7-0/7-docs/CAref.html) provides a lot more detail.
