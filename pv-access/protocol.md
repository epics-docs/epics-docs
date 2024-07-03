# pvAccess Protocol Specification

## EPICS v4 Working Group

This document was converted from the
[Public Working Draft, 16-October-2015](https://github.com/epics-base/pvDataWWW/blob/ca3848712682132d67b63c7be0fc63e5b0256f6c/mainPage/pvAccess_Protocol_Specification.html)
and continues to be updated.

  - Editors:  
    * Matej Sekoranja, Cosylab
    * Marty Kraimer, BNL
    * Greg White, SLAC, PSI
    * Andrew Johnson, APS (Invited Expert)
    * Benjamin Franksen, HZB (Invited Expert)
    * Michael Abbott, DLS (Invited Expert)
    * Philip Duval, DESY (Invited Expert)

-----

## Abstract

This document defines the EPICS communication protocol called
"pvAccess". pvAccess is a high-performance network communication
protocol for signal monitoring and scientific data services
interconnect. It also encompasses a structured data encoding
referred to as "pvData".

The connection setup requirements and individual message constructs of
pvAccess are described. It is intended that sufficient detail is given
for a reader to create an interoperable pvAccess implementation.

EPICS is a computer platform for building the control systems of large
scientific instruments. For more information about EPICS, please refer
to the home page of the [Experimental Physics and Industrial Control
System.](http://epics-controls.org)

## Status of this Document

The terms MUST, MUST NOT, SHOULD, SHOULD NOT, REQUIRED, and MAY when
highlighted (through style sheets, and in uppercase in the source) are
used in accordance with [RFC 2119](http://www.ietf.org/rfc/rfc2119.txt). 
The term NOT REQUIRED (not defined in RFC 2119) indicates exemption.

## Protocol Versions

This section describes protocol variations based on negotiated version.
The remote peer should be assumed to be Version 1 until the first message is received and decoded.
After this point, the negotiated version is the lesser of the local and peer versions.

As a special exception, a TCP peer must be disconnected if it does not send a valid message within ``$EPICS_PVA_CONN_TMO`` seconds.

### Version 2

 * v2 server's 'Echo' reply must include the request payload.
 * v2 peers must close TCP connections when no data has been received in ``$EPICS_PVA_CONN_TMO`` seconds (default 30 sec.).
 * v2 clients must send 'Echo' more often than ``$EPICS_PVA_CONN_TMO`` seconds.  The recommended interval is half of ``$EPICS_PVA_CONN_TMO`` (default 15 sec.).

### Version 1
 * v1 servers reply to 'Echo' with empty payload.
 * v1 clients never send 'Echo'.
 * v1 peers never timeout inactive TCP connections.

### Version 0
 * Obsolete version code used by early clients/servers.  Messages are not compatible with >=v1.

## Table of Contents

<div class="toc">

1.  [Overview](#overview)
2.  [Data Encoding](Protocol-Encoding)
3.  [Connection Management](Protocol-Prose.md#connection-management)
4.  [Channel Life-cycle](Protocol-Prose.md#channel-life-cycle)
5.  [Channel Request Life-cycle](Protocol-Prose.md#channel-request-life-cycle)
6.  [Flow Control](Protocol-Prose.md#flow-control)
7.  [Channel Discovery](Protocol-Prose.md#channel-discovery)
8.  [Communication Example](Protocol-Prose.md#communication-example)
9.  [Protocol Messages](Protocol-Messages.md#protocol-messages)
    1.  [Message header](Protocol-Messages.md#message-header)
10. [Application Messages](Protocol-Messages.md#application-messages)
11. [Control Messages](Protocol-Messages.md#controlMessages)
12. [Future Protocol Changes/Updates](#futureProtocolChanges)
13. [Missing Aspects](#missing)

</div>

-----

<div id="contents" class="contents">

## Overview

pvAccess is a high-performance network communication protocol. It is
designed for efficient signal monitoring and the data
requirements of a service oriented architecture.

pvAccess is a successor of [EPICS](http://epics-controls.org)
[Channel Access](../internal/ca_protocol.rst).

TCP/IP is used for data transmission. UDP/IP is normally used for
discovery, although discovery over TCP/IP is also allowed. The discovery
mechanism allows the use of other implementations (e.g. UDP/IP for data
transmission).

Port number 5076 is used for UDP traffic by default.
Port number 5075 is preferred for TCP connections, but a random port can be used.

To support multiple local sockets at port 5076 to able all to receive
unicast messages over the UDP a multicast group on local network
interface at address 224.0.0.128, port 5076, is used. Any UDP message
flagged as unicast received at port 5076 MUST be forwarded to the
multicast group with unicast flag cleared.

The pvAccess protocol definition consists of three major parts:

  - A set of data encoding rules that determine how the various data
    types are encoded and deserialized
  - A set of rules that determine how client and server agree on a
    particular encoding
  - A number of message types, that define the interchange between
    endpoints, together with rules which specify what message is to be
    sent under what circumstances.

## Future Protocol Changes/Updates

The following are known items that should be specified in future
revisions:

  - "one-phase" get/put/get-put/process
  - immutable fields support, cache implemented for values (useful for
    enums)
  - optimized packed Monitor responses
  - bulk message transfer/trottle public API
  - access rights
  - etc.

## Missing Aspects

The following aspects are missing in the current revision of the
specification and will be specified in future revisions:

  - structure/content of pvRequestIF/pvRequest fields
  - offset and count fields of channelArray request should be of type
    'size', however 'size' cannot be negative
  - update Communication Example section to show messages

## Bibliography

bib:caref

EPICS R3.14 Channel Access Reference Manual, J.O. Hill, R. Lange, 2002,
<http://www.aps.anl.gov/epics/base/R3-14/8-docs/CAref.html>

bib:pvdatarefcpp

EPICS pvDataCPP \[pvData C++ Programmers Reference Manual\], M. Kraimer,
2011 under development,
<http://epics-pvdata.sourceforge.net/docbuild/pvDataCPP/tip/documentation/pvDataCPP.html>

bib:pvdatarefjava

EPICS pvDataJava \[pvData Java Programmers Reference Manual\], M.
Kraimer, 2011 under development,
<http://epics-pvdata.sourceforge.net/docbuild/pvDataJava/tip/documentation/pvDataJava.html>

bib:ieee754wiki

IEEE 754-2008, Wikipedia article, April 2012,
<http://en.wikipedia.org/wiki/IEEE_754-1985>
