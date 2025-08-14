# Protocol messages specification

```{contents}
```

The pvAccess protocol uses two protocol message types:

  - Control messages. These include flow control and have no payload
  - Application messages. These are the requests and their responses.

Each message consists of a message header and for Application messages, a message payload immediately following the header.
Messages MUST BE aligned on a 64-bit boundary (TODO really?).

Every implementation of the protocol which purports to support this
specification version of the protocol, MUST also support all prior
specification versions of the protocol. Every implementation of the
protocol MUST clearly indicate the most recent specification version to
which it is conformant, using the version URLs above.

## Message Header

Each protocol message has a fixed 8-byte header that MUST be encoded as
if it were expressed by the following structure:

```c
struct pvAccessHeader {
    byte magic;
    byte version;
    byte flags;
    byte messageCommand;
    int payloadSize;
};
```

The semantics of these message header components are given in the
following table.

:::{table} pvAccess Header Members
:align: center

|         Member | Description                                             |
| -------------: | ------------------------------------------------------- |
|          magic | pvAccess protocol magic code. This MUST always be 0xCA. |
|        version | Protocol version.                                       |
|          flags | Message flags.                                          |
| messageCommand | Message command (i.e. create, get, put, process, etc.). |
|    payloadSize | Message payload size (non-aligned, in bytes).           |
:::


:::{table} pvAccess Header Flags Description
:align: center

| bit   | Value | Description                            |
| ---   | ----- | -----------                            |
| 0     |  0    | Application message                    |
| 0     |  1    | Control message                        |
| 1,2,3 | 0     | Unused, **MUST** be 0                  |
| 5, 4  | 00    | Not segmented message                  |
| 5, 4  | 01    | First message (of segmented messages)  |
| 5, 4  | 10    | Last message (of segmented messages)   |
| 5, 4  | 11    | Middle message (of segmented messages) |
| 6     | 0     | Message sent by client                 |
| 6     | 1     | Message sent by server                 |
| 7     | 0     | Little endian byte order               |
| 7     | 1     | Big endian byte order                  |
:::

Between two segmented messages of the same set there MUST NOT be any
other application message than the segmented message of the same set.
Control messages are allowed to be in-between.

Alignment offset MUST be preserved between segmented messages, i.e. if
the last sent byte of a segmented message is misaligned by 6 bytes to
the 64-bit aligned start of the message reference point, then the next
segmented message needs to insert 6 padding bytes at the start of the
next segmented message payload.

## Application Messages

This section describes the message payloads for application messages.
Each subsection describes a single message command
(*pvAccessHeader.messageCommand*).

"request" means a message sent by a client, and "response" means a
message sent by a server. <span class="ed priv"> Is this specifically in
response to the client request? If so, as written "response" does not
say that\!</span>

In order to understand specific application messages it is helpful to be
familiar with the EPICS V4
[pvAccess](http://epics-pvdata.sourceforge.net/docbuild/pvAccessJava/tip/documentation/pvAccessJava.html)
Programmers Reference.

Most application messages below relate to the management of process
variable channels. A process variable, or PV, is a dynamical quantity
and its associated local processing semantics, as understood by process
control systems. pvAccess has been designed to specifically integrate
with process control systems to provide an
efficient interconnect for systems involved in the exchange of PV
related information. Agent systems connect to a process control computer
(via pvAccess) hosting PVs, by opening a "Channel" to each PV of
interest. A channel is the temporal connection between pvAccess agents,
with respect to one process variable.

All application message MUST be sent over the data transmission
transport unless explicitly specified. TCP/IP is the transport in the
reference implementation. A response message MUST be sent over the same
transport as that on which the request was received.

### CMD_BEACON (0x00)

Servers MUST broadcast or multicast beacons over UDP.
Beacons are be used to announce the appearance and continued presence of servers.
Clients may use Beacons to detect when new servers appear,
and may use this information to more quickly retry unanswered CMD_SEARCH messages.

```c
struct beaconMessage {
    byte[12] guid;
    byte flags;
    byte beaconSequenceId;
    short changeCount;
    byte[16] serverAddress;
    short serverPort;
    string protocol;
    FieldDesc serverStatusIF;
    [if serverStatusIF != NULL_TYPE_CODE] PVField serverStatus;
};
```

:::{table} Beacon Message Members
:align: center

|            Member | Description                                                                                       |
| ----------------: | ------------------------------------------------------------------------------------------------- |
|              guid | Server GUID (Globally Unique Identifier). MUST change every restart.                              |
|             flags | reserved                                                                                          |
|  beaconSequenceId | Beacon sequence ID (counter w/ rollover). Can be used to detect UDP routing problems.             |
|       changeCount | Count (w/ rollover) that changes every time server's list of channels changes.                    |
| serverAddressIPv6 | Server address (e.g. for IP transports IPv6 or IPv6 encoded IPv4 address).                        |
|        serverPort | Server port (e.g. for IP transport socket port where server is listening).                        |
|          protocol | Protocol/transport name (e.g. "tcp" for standard pvAccess TCP/IP communication).                  |
|    serverStatusIF | Optional server status Field description, NULL\_TYPE\_CODE MUST be used indicate absence of data. |
|      serverStatus | Optional server data.                                                                             |
:::

When a pvAccess server is started it MUST begin emitting beacons.
Clients MUST monitor all beacons. A beacon received from an as yet
unknown serverAddress:serverPort MUST be interpreted as indicating that
a new server has come online. A beacon with the same
serverAdddress:serverPort address as one already received but has
different globally unique ID (guid), MUST be interpreted as indicating
that the server was restarted. In both cases a client SHOULD boost
searching of not yet found channels. A client SHOUD also boost searching
of not yet found channels when changeCount changes (this indicates that
the server might host new channels). A client MAY disconnect old
connections or wait until connection loss is detected (on failed Echo
message send).

Each server transport instance SHOULD emit its own beacons. For example,
if a server supports data transmission over TCP/IP and UDP/IP then these
SHOULD both emit beacons. If the instances are tightly coupled, i.e.
they have the same lifecycle and share the same channels, then only one
server MAY emit beacons.

Due to the fact that UDP does not guarantee delivery, a server MUST send
several beacons to notify that it is alive (e.g. 15 beacons with 1Hz
period). After a longer period it MAY stop sending them, however it is
recommended that it SHOULD continue merely with a low rate (e.g. one
beacon per minute) to report serverStatus.

Existing PVA server implementations send one beacon every 15 seconds
for the first 5 minutes after startup. After running for 5 minutes, they
lower the beacon period to once every 180 seconds (3 minutes). 

Beacons SHOULD not be used to report connection-valid status.

### CMD_CONNECTION_VALIDATION (0x01)

The Connection Validation message has two different formats depending on
`Flags[Direction]`.

A Connection Validation Request message MUST be the first application message
sent from the server to a client when a TCP/IP connection is
established (after a Set byte order Control message).
The client MUST NOT send any messages on the connection until
it has received a connection validation message from the server.

The connection validation request and connection validation response
messages are defined as follows:

```c
// Server to Client
struct connectionValidationRequest {
    int serverReceiveBufferSize;
    short serverIntrospectionRegistryMaxSize;
    string[] authNZ;                        // list of supported authNZ;
};

// Client to Server
struct connectionValidationResponse {
    int clientReceiveBufferSize;
    short clientIntrospectionRegistryMaxSize;
    short connectionQos;
    string authNZ;                          // selected authNZ plugin;
    // Optional, content depends on authNZ
    FieldDesc dataIF;
    PVField data;
};
```

In the connectionValidationRequest, the server lists the support authentication methods.
Currently supported are "anonymous", "ca", "x509".
In the connectionValidationResponse, the client selects one of these.
For "anonymous" or "x509", no further detail is required and the `FieldDesc` is 0xFF for the 'null' type code with no `PVField`.
For "ca", a structure with string elements "user" and "host" needs to follow.

:::{table} Connection Validation Request Message Members
:align: center

|                             Member | Description                                                                |
| ---------------------------------: | -------------------------------------------------------------------------- |
|            serverReceiveBufferSize | Server receive buffer size in bytes.                                       |
|      serverReceiveSocketBufferSize | Server socket buffer size in bytes.                                        |
| serverIntrospectionRegistryMaxSize | Maximum number of introspection registry entries server is able to handle. |
|                             authNZ | List of supported authentication modes                                     |
:::

:::{table} Connection Validation Response Message Members
:align: center

|                             Member | Description                                                                |
| ---------------------------------: | -------------------------------------------------------------------------- |
|            clientReceiveBufferSize | Client receive buffer size in bytes.                                       |
|      clientReceiveSocketBufferSize | Client socket buffer size in bytes.                                        |
| clientIntrospectionRegistryMaxSize | Maximum number of introspection registry entries client is able to handle. |
|                      connectionQoS | Connection QoS parameters.                                                 |
:::

:::{table} Connection QoS Parameters Description
:align: center

|   bit | Description               |
| ----: | ------------------------- |
|   0-6 | Priority level \[0-100\]. |
|     7 | Unused, MUST be 0.        |
|     8 | Low-latency priority.     |
|     9 | Throughput priority.      |
|    10 | Enable compression.       |
| 11-15 | Unused, MUST be 0.        |
:::

Each Quality of Service (QoS) parameter value REQUIRES a separate TCP/IP
connection. If the Low-latency priority bit is set, this indicates
clients should attempt to minimize latency if they have the capacity to
do so. If the Throughput priority bit is set, this indicates a client
similarly should attempt to maximize throughput. How this is achieved is
implementation defined. The Compression bit enables compression for the
connection _(Which compression? From which support layer?)_. 
A matter for a future version of the specification should
be whether a streaming mode algorithm should be specified.

### CMD_ECHO (0x02)

An Echo diagnostic message is usually sent to check if TCP/IP connection
is still valid.

```c
struct echoRequest {
    byte[] somePayload;
};

struct echoResponse {
    byte[] samePayloadAsInRequest;
};
```

:::{table} Echo request message members
:align: center

|      Member | Description                              |
| ----------: | ---------------------------------------- |
| somePayload | Arbitrary payload content, can be empty. |
:::

:::{table} Echo response message members
:align: center

|                 Member | Description                         |
| ---------------------: | ----------------------------------- |
| samePayloadAsInRequest | Same paylaod as in request message. |
:::

Version 1 servers do not support the payload and will always send an empty reply.
Version 2 servers return the payload.

### CMD_SEARCH (0x03)

A channel "search request" message SHOULD be sent over UDP/IP, however
UDP congestion control SHOULD be implemented in this case. A server MUST
accept this message also over TCP/IP.

```c
struct searchRequest {
    int searchSequenceID;
    byte flags; // 0-bit for replyRequired, 7-th bit for "sent as unicast" (1)/"sent as broadcast/multicast" (0)

    byte[3] reserved;

    // if not provided (or zero), the same transport is used for responses
    // needs to be set when local broadcast (multicast on loop interface) is done
    byte[16] responseAddress; // e.g. IPv6 address in case of IP based transport, UDP
    short responsePort;       // e.g. socket port in case of IP based transport

    string[] protocols;

    struct {
        int searchInstanceID;
        string channelName;
    } channels[];
};
```

:::{table} Search request message members
:align: center

|           Member | Description                                                                             |
| ---------------: | --------------------------------------------------------------------------------------- |
| searchSequenceID | Search sequence ID (counter w/ rollover), can be used by congestion control algorithms. |
|    replyRequired | 0x01 to force server to respond even if it does not host channel(s), 0x00 otherwise.    |
|         protocol | A set of allowed protocols to respond ("tcp", "tls"). Unrestricted if array is empty.   |
| searchInstanceID | ID to be used to associate response with the following channel name.                    |
|      channelName | Non-empty channel name, maximum length of 500 characters.                               |
:::

The protocol "tcp" indicates that the client would like to then continue the data communication via a plain TCP connection.
"tls" indicates that the client can also support an SSL/TLS TCP connection.

Note that the element count for protocol uses the normal size encoding, i.e. unsigned 8-bit integer 1 for one
supported protocol.
The element count for the channels array, however, always uses an unsigned 16 bit integer.
This choice is based on the reference implementations which append channel names to the network buffer and
update the count. With normal size encoding, an increment to 254 would change the count from requiring 1 byte to 3 bytes, shifting already added channel names.

The response to a search request is defined as messageCommand 0x04, see
below.

As mentioned, servers always accept CMD_SEARCH via TCP.
The environment variable EPICS_PVA_NAME_SERVERS configures a client to use
a list of IP addresses for name lookup via TCP.
The client connects to each IP (and optional ":port") listed as a name server.
Upon connection, the server will send the byte order and validation request messages.
After the server and client complete this exchange, the client may send CMD_SEARCH.
If the channel is known, the server will reply with CMD_SEARCH_RESPONSE via the same
TCP connection.

### CMD_SEARCH_RESPONSE (0x04)

A search response message MUST be sent as the response to a specific
search request (0x03) message.

```c
struct searchResponse {
    byte[12] guid;          
    int searchSequenceID;
    byte[16] serverAddress; // e.g. IPv6 address in case of IP based transport 
    short serverPort;       // e.g. socket port in case of IP based transport
    string protocol;
    boolean found;
    int[] searchInstanceIDs;
};
```

:::{table} Search response message members
:align: center

|            Member | Description                                                                       |
| ----------------: | --------------------------------------------------------------------------------- |
|  searchSequenceID | Search sequence ID, same as specified in search request.                          |
|             found | Flag indicating whether response contains IDs of found or not found channels.     |
| serverAddressIPv6 | Server address (e.g. in case of IP transport IP or IPv6 encoded IPv4 address).    |
|        serverPort | Server port (e.g. in case of IP transport socket port where server is listening). |
|          protocol | Protocol name, "tcp" for standard pvAccess TCP/IP communication, "tls" for secure TCP |
| searchInstanceIDs | IDs, associated with names in the request, relevant to this response.             |
:::

A client MUST examine the protocol member field to verify it supports
the given exchange protocol; if not, the search response is ignored.

The count for the number of searchInstanceIDs elements is always sent as an unsigned 16 bit integer,
not using the default size encoding.

If the serverAddressIPv6 is non-zero, it specifies the TCP connection information
that the client should use for further communication, i.e., to create a channel
and perform get/put/.. operations.
If the address is all zero, and the exchange is via UDP,
the client should use the address from which the UDP reply was received as the server address. 
If the address is all zero, and the exchange is via TCP,
the client should use that same TCP connection for further communication.


### CMD_AUTHNZ (0x05)

```c
struct authNZRequest {
    FieldDesc dataIF;
    [if dataIF != NULL_TYPE_CODE] PVField data;
};

struct authNZResponse {
    FieldDesc dataIF;
    [if dataIF != NULL_TYPE_CODE] PVField data;
};
```

### CMD_ACL_CHANGE (0x06)

A server sends this message to inform the client about
write permissions for a channel.

```c
struct aclChange {
    int clientChannelID;
    // Permission bits:
    // Bit 0: Client may write via PUT
    // Bit 1: Client may perform a PUT-GET
    // Bit 2: Client may call RPC
    byte permissions;
};
```

The server sends an inital `CMD_ACL_CHANGE` right before
the `CMD_CREATE_CHANNEL` `createChannelResponse` described
in the next section, and whenever the write permissions
change.

This message is a hint.
The key use case for this message is graphical user interfaces
that need to indicate if a channel is "read only",
for example by disabling associated GUI elements.

For normative types, permission bit 0 (`PUT`) indicates
that the client can write to the "value" field of the data structure.
It does not imply that the client can write to the "units",
"timeStamp", "severity" or other fields.
For custom data types, `PUT` access will similarly indicate
that the client has write access to at least one field.
Clients may always perform a `PUT` and then learn from the
response status if it was successful.

Permission bit 1 (`PUT-GET`) indicates that the channel supports
`PUT-GET` operations.

Permission bit 2 (`RPC`) indicates that the channel supports
`RPC` calls.

Note that `aclChange` had a different earlier definition
which was never implemented. Older servers never sent `aclChange`.
Some older clients went as far as recognizing the `CMD_ACL_CHANGE` message command code
but never parsed the `aclChange` body nor reacted in any way.

For compatibility of new clients with older servers,
clients should assume write access until they receive `CMD_ACL_CHANGE`.


### CMD_CREATE_CHANNEL (0x07)

A channel provides a communication path between a client and a server
hosted "process variable."

Each channel instance MUST be bound only to one connection.

```c
struct createChannelRequest {
    short count;
    struct {
        int clientChannelID;
        string channelName;
    } channels[];
};

struct createChannelResponse {
    int clientChannelID;
    int serverChannelID;
    Status status;
    // [if status.type == OK | WARNING] short accessRights; // never used
};
```

:::{table} Create channel request message members
:align: center

|          Member | Description                                                                        |
| --------------: | ---------------------------------------------------------------------------------- |
| clientChannelID | Client generated channel ID.                                                       |
|     channelName | Name of the channel to be created, non-empty and maximum length of 500 characters. |
:::

The `createChannelRequest.channels` array starts with a `short` count,
not using the normal size encoding.
Current PVA server implementations only support requests for creating
a single channel, i.e. the `count` must be 1.

Note that the server may send a `CMD_ACL_CHANGE` message right before the
`CMD_CREATE_CHANNEL` response.

:::{table} Create channel response (per channel) message members
:align: center

|          Member | Description                                     |
| --------------: | ----------------------------------------------- |
| clientChannelID | Client generated channel ID, same as in request |
| serverChannelID | Server generated channel ID.                    |
|          status | Completion status.                              |
|    accessRights | Access rights (TBD).                            |
:::

:::{note}
A server MUST store the clientChannelID and respond with its value
in a destroyChannelMessage when a channel destroy request is requested,
see below. A client uses the serverChannelID value for all subsequent
requests on the channel. Agents SHOULD NOT make any assumptions about
how given IDs are generated. IDs MUST be unique within a connection and
MAY be recycled after a channel is disconnected.
:::

### CMD_DESTROY_CHANNEL (0x08)

A "destroy channel" message is sent by a client to a server to destroy a channel
that was previously created (with a create channel message).

A server may also send this message to the client when the channel is no longer
available. Examples include a PVA gateway that sends this message from its server
side when it lost a channel on its client side.

```c
struct destroyChannelRequest {
    int serverChannelID;
    int clientChannelID;
};

struct destroyChannelResponse {
    int serverChannelID;
    int clientChannelID;
};
```

:::{table} Destroy channel request
:align: center

|          Member | Description                                              |
| --------------: | -------------------------------------------------------- |
| serverChannelID | Server generated channel ID, same as in create response. |
| clientChannelID | Client generated channel ID, same as in create request.  |
:::

:::{table} Destroy channel response
:align: center

|          Member | Description                                              |
| --------------: | -------------------------------------------------------- |
| serverChannelID | Server generated channel ID, same as in create response. |
| clientChannelID | Client generated channel ID, same as in create request.  |
:::

If the request (clientChannelID, serverChannelID) pair does not match,
the server MUST respond with an error status. The server MAY break its
response into several messages.

:::{note}
A server MUST send this message to a client to notify the client
about server-side initiated channel destruction. Subsequently, a client
MUST mark such channels as disconnected. If the client's interest in the
process variable continues, it MUST start sending search request
messages for the channel.
:::

### CMD_CONNECTION_VALIDATED (0x09)

Sent from Client to Server to indicate the completion of an Authentication handshake.

```c
struct connectionValidated {
    Status status;
};
```

### CMD_GET (0x0A)

A "channel get" set of messages are used to retrieve (get) data from the
channel.

```c
struct channelGetRequestInit {
    int serverChannelID;
    int requestID;
    byte subcommand = 0x08 for INIT;
    FieldDesc pvRequestIF;
    PVField pvRequest;
};

struct channelGetResponseInit {
    int requestID;
    byte subcommand;
    Status status;
    [if status.type == OK | WARNING] FieldDesc pvStructureIF;
};
```

:::{table} Channel get init request
:align: center

|          Member | Description                                                      |
| --------------: | ---------------------------------------------------------------- |
| serverChannelID | Server generated channel ID, same as in create channel response. |
|       requestID | Client generated request ID.                                     |
|      subcommand | 0x08                                                             |
|     pvRequestIF | pvRequest Field description.                                     |
|       pvRequest | pvRequest structure.                                             |
:::

:::{table} Channel get init response
:align: center

|        Member | Description                                     |
| ------------: | ----------------------------------------------- |
|     requestID | Request ID, same as in request message.         |
|    subcommand | 0x08, same as in request message.               |
|        status | Completion status.                              |
| pvStructureIF | pvStructure (data container) Field description. |
:::

After a get request is successfully initialized, the client can issue
actual get request(s).

```c
struct channelGetRequest {
    int serverChannelID;
    int requestID;
    byte subcommand = 0x00 or 0x40 for GET; additional 0x10 mask for DESTROY;
};

struct channelGetResponse {
    int requestID;
    byte subcommand;
    Status status;
    [if status.type == OK | WARNING] BitSet changedBitSet;
    [if status.type == OK | WARNING] PVField pvStructureData;
};
```

:::{table} Channel get request
:align: center

|          Member | Description                                                      |
| --------------: | ---------------------------------------------------------------- |
| serverChannelID | Server generated channel ID, same as in create channel response. |
|       requestID | Request ID, same as in init message.                             |
|      subcommand | 0x00 for GET, additional 0x10 mask for DESTROY.                  |
:::

:::{table} Channel get response
:align: center

|          Member | Description                             |
| --------------: | --------------------------------------- |
|       requestID | Request ID, same as in request message. |
|      subcommand | Same as in request message.             |
|          status | Completion status.                      |
|   changedBitSet | Changed BitSet for pvStructureData.     |
| pvStructureData | Data structure.                         |
:::

Most implementations send a 0x00 subcommand to GET data,
but based on the original protocol documentation 0x40
is also in use.

:::{note}
If the DESTROY mask is applied, the server MUST destroy the
request after the get response and the client MUST do the same after it
receives the response.
:::

### CMD_PUT (0x0B)

A "channel put" set of messages are used to set (put) data to the
channel.

```c
struct channelPutRequestInit {
    int serverChannelID;
    int requestID;
    byte subcommand = 0x08;
    FieldDesc pvRequestIF;
    PVField pvRequest;
};

struct channelPutResponseInit {
    int requestID;
    byte subcommand;
    Status status;
    [if status.type == OK | WARNING] FieldDesc pvPutStructureIF;
};
```

:::{table} Channel put init request
:align: center

|          Member | Description                                                      |
| --------------: | ---------------------------------------------------------------- |
| serverChannelID | Server generated channel ID, same as in create channel response. |
|       requestID | Client generated request ID.                                     |
|      subcommand | 0x08                                                             |
|     pvRequestIF | pvRequest Field description.                                     |
|       pvRequest | pvRequest structure.                                             |
:::

:::{table} Channel put init response
:align: center

|           Member | Description                                        |
| ---------------: | -------------------------------------------------- |
|        requestID | Request ID, same as in request message.            |
|       subcommand | 0x08, same as in request message.                  |
|           status | Completion status.                                 |
| pvPutStructureIF | pvPutStructure (data container) Field description. |
:::

After a put request is successfully initialized, the client can issue
actual put request(s) on the channel.

```c
struct channelPutRequest {
    int serverChannelID;
    int requestID;
    byte subcommand = 0x00 for PUT; 0x10 mask for DESTROY;
    BitSet toPutBitSet;
    PVField pvPutStructureData;
};

struct channelPutResponse {
    int requestID;
    byte subcommand;
    Status status;
};
```

:::{table} Channel put request
:align: center

|             Member | Description                                                      |
| -----------------: | ---------------------------------------------------------------- |
|    serverChannelID | Server generated channel ID, same as in create channel response. |
|          requestID | Request ID, same as in init message.                             |
|         subcommand | 0x00 for PUT, additional 0x10 mask for DESTROY.                  |
|        toPutBitSet | To-put BitSet for pvPutStructureData.                            |
| pvPutStructureData | Data to put structure.                                           |
:::

:::{table} Channel put response
:align: center

|     Member | Description                             |
| ---------: | --------------------------------------- |
|  requestID | Request ID, same as in request message. |
| subcommand | Same as in request message.             |
|     status | Completion status.                      |
:::

A "get-put" request retrieves the remote put structure. This MAY be used
by user applications to show data that was set the last time by the
application.

```c
struct channelGetPutRequest {
    int serverChannelID;
    int requestID;
    byte subcommand = 0x40;
};

struct channelGetPutResponse {
    int requestID;
    byte subcommand;
    Status status;
    [if status.type == OK | WARNING]
        BitSet returnedDataBitSet;
        PVField pvStructureData;
};
```

:::{table} Channel get put request
:align: center

|          Member | Description                                                      |
| --------------: | ---------------------------------------------------------------- |
| serverChannelID | Server generated channel ID, same as in create channel response. |
|       requestID | Request ID, same as in init message.                             |
|      subcommand | 0x40.                                                            |
:::

:::{table} Channel get put response
:align: center

|             Member | Description                             |
| -----------------: | --------------------------------------- |
|          requestID | Request ID, same as in request message. |
|         subcommand | Same as in request message.             |
|             status | Completion status.                      |
| returnedDataBitSet | Which fields are provided in data.      |
| pvStructureData    | The returned data.                      |
:::

### CMD_PUT_GET (0x0C)

A "channel put-get" set of messages are used to set (put) data to the
channel and then immediately retrieve data from the channel. Channels
are usually "processed" or "updated" by their host between put and get,
so that the get reflects changes in the process variable's state.

```c
struct channelPutGetRequestInit {
    int serverChannelID;
    int requestID;
    byte subcommand = 0x08;
    FieldDesc pvRequestIF;
    PVField pvRequest;
};

struct channelPutGetResponseInit {
    int requestID;
    byte subcommand;
    Status status;
    [if status.type == OK | WARNING] FieldDesc pvPutStructureIF;
    [if status.type == OK | WARNING] FieldDesc pvGetStructureIF;
};
```

:::{table} Channel put-get init request
:align: center

|          Member | Description                                                      |
| --------------: | ---------------------------------------------------------------- |
| serverChannelID | Server generated channel ID, same as in create channel response. |
|       requestID | Client generated request ID.                                     |
|      subcommand | 0x08                                                             |
|     pvRequestIF | pvRequest Field description.                                     |
|       pvRequest | pvRequest structure.                                             |
:::

:::{table} Channel put-get init response
:align: center

|           Member | Description                                        |
| ---------------: | -------------------------------------------------- |
|        requestID | Request ID, same as in request message.            |
|       subcommand | 0x08, same as in request message.                  |
|           status | Completion status.                                 |
| pvPutStructureIF | pvPutStructure (data container) Field description. |
| pvGetStructureIF | pvGetStructure (data container) Field description. |
:::

After a put-get request is successfully initialized, the client can
issue actual put-get request(s) on the channel.

```c
struct channelPutGetRequest {
    int serverChannelID;
    int requestID;
    byte subcommand = 0x00 for PUT_GET; 0x10 mask for DESTROY;
    BitSet toPutBitSet;
    PVField pvPutStructureData;
};

struct channelPutGetResponse {
    int requestID;
    byte subcommand;
    Status status;
    [if status.type == OK | WARNING] PVField pvGetStructureData;
};
```

:::{table} Channel put-get request
:align: center

|             Member | Description                                                      |
| -----------------: | ---------------------------------------------------------------- |
|    serverChannelID | Server generated channel ID, same as in create channel response. |
|          requestID | Request ID, same as in init message.                             |
|         subcommand | 0x00 for PUT\_GET, additional 0x01 mask for DESTROY.             |
|        toPutBitSet | To-put BitSet for pvPutStructureData.                            |
| pvPutStructureData | Data to put structure.                                           |
:::

:::{table} Channel put-get response
:align: center

|             Member | Description                             |
| -----------------: | --------------------------------------- |
|          requestID | Request ID, same as in request message. |
|         subcommand | Same as in request message.             |
|             status | Completion status.                      |
| pvGetStructureData | Get data structure.                     |
:::

A "get-put" request retrieves the remote put structure. This MAY be used
by user applications to show data that was set the last time by the
application.

```c
struct channelGetPutRequest {
    int serverChannelID;
    int requestID;
    byte subcommand = 0x80;
};

struct channelGetPutResponse {
    int requestID;
    byte subcommand;
    Status status;
    [if status.type == OK | WARNING] PVField pvPutStructureData;
};
```

:::{table} Channel get put request
:align: center

|          Member | Description                                                      |
| --------------: | ---------------------------------------------------------------- |
| serverChannelID | Server generated channel ID, same as in create channel response. |
|       requestID | Request ID, same as in init message.                             |
|      subcommand | 0x80.                                                            |
:::

:::{table} Channel get put response
:align: center

|             Member | Description                             |
| -----------------: | --------------------------------------- |
|          requestID | Request ID, same as in request message. |
|         subcommand | Same as in request message.             |
|             status | Completion status.                      |
| pvPutStructureData | Remote put data structure.              |
:::

A "get-get" request retrieves remote get structure. This MAY be used by
user applications to show data that was retrieved the last time.

```c
struct channelGetGetRequest {
    int serverChannelID;
    int requestID;
    byte subcommand = 0x40;
};

struct channelGetGetResponse {
    int requestID;
    byte subcommand;
    Status status;
    [if status.type == OK | WARNING] PVField pvGetStructureData;
};
```

:::{table} Channel get get request
:align: center

|          Member | Description                                                      |
| --------------: | ---------------------------------------------------------------- |
| serverChannelID | Server generated channel ID, same as in create channel response. |
|       requestID | Request ID, same as in init message.                             |
|      subcommand | 0x40.                                                            |
:::

:::{table} Channel get get response
:align: center

|             Member | Description                             |
| -----------------: | --------------------------------------- |
|          requestID | Request ID, same as in request message. |
|         subcommand | Same as in request message.             |
|             status | Completion status.                      |
| pvGetStructureData | Remote get data structure.              |
:::

```{include} ./Protocol-Operation-Monitor.md
:heading-offset: 2
```

### CMD_ARRAY (0x0E)

A "channel array" set of messages are used to handle remote array
values. Requests allow a client agent to: retrieve (get) and set (put)
data from/to the array, and to change the array's length (number of
valid elements in the array).

```c
struct channelArrayRequestInit {
    int serverChannelID;
    int requestID;
    byte subcommand = 0x08;
    FieldDesc pvRequestIF;
    PVField pvRequest;
};

struct channelArrayResponseInit {
    int requestID;
    byte subcommand;
    Status status;
    [if status.type == OK | WARNING] FieldDesc pvArrayIF;
};
```

:::{table} Channel array init request
:align: center

|          Member | Description                                                      |
| --------------: | ---------------------------------------------------------------- |
| serverChannelID | Server generated channel ID, same as in create channel response. |
|       requestID | Client generated request ID.                                     |
|      subcommand | 0x08                                                             |
|     pvRequestIF | pvRequest Field description.                                     |
|       pvRequest | pvRequest structure.                                             |
:::

:::{table} Channel array init response
:align: center

|     Member | Description                                 |
| ---------: | ------------------------------------------- |
|  requestID | Request ID, same as in request message.     |
| subcommand | 0x08, same as in request message.           |
|     status | Completion status.                          |
|  pvArrayIF | pvArray (data container) Field description. |
:::

After an array request is successfully initialized, the client can issue
the actual array request(s).

```c
struct channelGetArrayRequest {
    int serverChannelID;
    int requestID;
    byte subcommand = 0x40 mask for GET; 0x10 mask for DESTROY;
    size offset;
    size count;
};

struct channelGetArrayResponse {
    int requestID;
    byte subcommand;
    Status status;
    [if status.type == OK | WARNING] PVField pvArrayData;
};
```

:::{table} Channel array get request
:align: center

|          Member | Description                                                                |
| --------------: | -------------------------------------------------------------------------- |
| serverChannelID | Server generated channel ID, same as in create channel response.           |
|       requestID | Request ID, same as in init message.                                       |
|      subcommand | 0x40 for GET, additional 0x10 mask for DESTROY.                            |
|          offset | Offset from the beginning of the array.                                    |
|           count | Number of elements requested, 0 means form offset to the end of the array. |
:::

:::{table} Channel array get response
:align: center

|      Member | Description                             |
| ----------: | --------------------------------------- |
|   requestID | Request ID, same as in request message. |
|  subcommand | Same as in request message.             |
|      status | Completion status.                      |
| pvArrayData | Data array.                             |
:::

```c
struct channelPutArrayRequest {
    int serverChannelID;
    int requestID;
    byte subcommand = 0x00 mask for PUT; 0x10 mask for DESTROY;
    size offset;
    PVField pvArrayData;
};

struct channelPutArrayResponse {
    int requestID;
    byte subcommand;
    Status status;
};
```

:::{table} Channel array put request
:align: center

|          Member | Description                                                      |
| --------------: | ---------------------------------------------------------------- |
| serverChannelID | Server generated channel ID, same as in create channel response. |
|       requestID | Request ID, same as in init message.                             |
|      subcommand | 0x00 for PUT, additional 0x10 mask for DESTROY.                  |
|          offset | Offset from the beginning of the array.                          |
|     pvArrayData | Subarray to be put.                                              |
:::

:::{table} Channel array put response
:align: center

|     Member | Description                             |
| ---------: | --------------------------------------- |
|  requestID | Request ID, same as in request message. |
| subcommand | Same as in request message.             |
|     status | Completion status.                      |
:::

```c
/// TODO GetLength is missing, fix the codes \!\!\!

struct channelSetLengthRequest {
    int serverChannelID;
    int requestID;
    byte subcommand = 0x80 mask for SET_LENGTH; 0x10 mask for DESTROY;
    size length;
};

struct channelSetLengthResponse {
    int requestID;
    byte subcommand;
    Status status;
};
```

:::{table} Channel array set length request
:align: center

|          Member | Description                                                      |
| --------------: | ---------------------------------------------------------------- |
| serverChannelID | Server generated channel ID, same as in create channel response. |
|       requestID | Request ID, same as in init message.                             |
|      subcommand | 0x40 for GET, additional 0x10 mask for DESTROY.                  |
|          length | New length.                                                      |
:::

:::{table} Channel array set length response
:align: center

|     Member | Description                             |
| ---------: | --------------------------------------- |
|  requestID | Request ID, same as in request message. |
| subcommand | Same as in request message.             |
|     status | Completion status.                      |
:::

### CMD_DESTROY_REQUEST (0x0F)

A "destroy request" messages is used destroy any request instance, i.e.
an instance with requestID.

```c
// destroys any request with given requestID
struct destroyRequest {
    int serverChannelID;
    int requestID;
};
```

:::{table} Destroy request
:align: center

|          Member | Description                                                      |
| --------------: | ---------------------------------------------------------------- |
| serverChannelID | Server generated channel ID, same as in create channel response. |
|       requestID | Request ID, same as in request init message.                     |
:::

### CMD_PROCESS (0x10)

A "channel process" set of messages are used to indicate to the server
that the computation actions associated with a channel should be
executed. In the language of EPICS, this means that the channel should
be "processed".

```c
struct channelProcessRequestInit {
    int serverChannelID;
    int requestID;
    byte subcommand = 0x08;
    FieldDesc pvRequestIF;
    [if serverStatusIF != NULL_TYPE_CODE] PVField pvRequest;
};

struct channelProcessResponseInit {
    int requestID;
    byte subcommand;
    Status status;
};
```

:::{table} Channel process init request
:align: center

|          Member | Description                                                      |
| --------------: | ---------------------------------------------------------------- |
| serverChannelID | Server generated channel ID, same as in create channel response. |
|       requestID | Client generated request ID.                                     |
|      subcommand | 0x08                                                             |
|     pvRequestIF | Optional pvRequest Field description, NULL\_TYPE\_CODE is none.  |
|       pvRequest | Optional pvRequest structure.                                    |
:::

:::{table} Channel process init response
:align: center

|     Member | Description                             |
| ---------: | --------------------------------------- |
|  requestID | Request ID, same as in request message. |
| subcommand | 0x08, same as in request message.       |
|     status | Completion status.                      |
:::

After a process request is successfully initialized, the client can
issue the actual process request(s).

```c
struct channelProcessRequest {
    int serverChannelID;
    int requestID;
    byte subcommand = 0x00 mask for PROCESS; 0x10 mask for DESTROY;
};

struct channelProcessResponse {
    int requestID;
    byte subcommand;
    Status status;
};
```

:::{table} Channel process request
:align: center

|          Member | Description                                                      |
| --------------: | ---------------------------------------------------------------- |
| serverChannelID | Server generated channel ID, same as in create channel response. |
|       requestID | Request ID, same as in init message.                             |
|      subcommand | 0x00 for PROCESS, additional 0x10 mask for DESTROY.              |
:::

:::{table} Channel process response
:align: center

|     Member | Description                             |
| ---------: | --------------------------------------- |
|  requestID | Request ID, same as in request message. |
| subcommand | Same as in request message.             |
|     status | Completion status.                      |
:::

### CMD_GET_FIELD (0x11)

Thus message is used to retrieve a channel's type introspection data,
i.e. a description of all the channel's fields and their data types.

```c
struct channelGetFieldRequest {
    int serverChannelID;
    int requestID;
    string subFieldName;  // entire record if empty
};

struct channelGetFieldResponse {
    int requestID;
    Status status;
    [if status.type == OK | WARNING] FieldDesc subFieldIF;
};
```

:::{table} Get channel introspection data request
:align: center

|          Member | Description                                                      |
| --------------: | ---------------------------------------------------------------- |
| serverChannelID | Server generated channel ID, same as in create channel response. |
|       requestID | Client generated request ID.                                     |
|    subFieldName | Name of the subfield to get or entire record if empty.           |
:::

:::{table} Get channel introspection data response
:align: center

|     Member | Description                             |
| ---------: | --------------------------------------- |
|  requestID | Request ID, same as in request message. |
|     status | Completion status.                      |
| subFieldIF | Requested field introspection data.     |
:::

### CMD_MESSAGE (0x12)

A "message" message is used by a server to provide to a client human
readable text regarding the status of a specific request. This message
MUST NOT be used to report request completion status.

```c
struct message {
    int requestID;
    byte messageType; // info = 0, warning = 1, error = 2, fatalError = 3
    string message;
};
```

:::{table} Message response
:align: center

|      Member | Description        |
| ----------: | ------------------ |
|   requestID | Client generated request ID. |
| messageType | Message type enum. |
|     message | Message.           |
:::

### CMD_MULTIPLE_DATA (0x13)

This message code never used, and considered deprecated.

### CMD_RPC (0x14)

The "channel RPC" set of messages are used to provide remote procedure
call (RPC) support over pvAccess.

```c
struct channelRPCRequestInit {
    int serverChannelID;
    int requestID;
    byte subcommand = 0x08;
    FieldDesc pvRequestIF;
    PVField pvRequest;
};

struct channelRPCResponseInit {
    int requestID;
    byte subcommand;
    Status status;
};
```

:::{table} Channel RPC init request
:align: center

|          Member | Description                                                      |
| --------------: | ---------------------------------------------------------------- |
| serverChannelID | Server generated channel ID, same as in create channel response. |
|       requestID | Client generated request ID.                                     |
|      subcommand | 0x08                                                             |
|     pvRequestIF | pvRequest Field description.                                     |
|       pvRequest | pvRequest structure.                                             |
:::

:::{table} Channel RPC init response
:align: center

|     Member | Description                             |
| ---------: | --------------------------------------- |
|  requestID | Request ID, same as in request message. |
| subcommand | 0x08, same as in request message.       |
|     status | Completion status.                      |
:::

After a RPC request is successfully initialized, the client can issue
actual RPC request(s).

```c
struct channelRPCRequest {
    int serverChannelID;
    int requestID;
    byte subcommand = 0x00 mask for RPC; 0x10 mask for DESTROY;
    FieldDesc pvStructureIF;
    PVField pvStructureData;
};

struct channelRPCResponse {
    int requestID;
    byte subcommand;
    Status status;
    [if status.type == OK | WARNING] FieldDesc pvResponseIF;
    [if status.type == OK | WARNING] PVField pvResponseData;
};
```

:::{table} Channel RPC request
:align: center

|          Member | Description                                                      |
| --------------: | ---------------------------------------------------------------- |
| serverChannelID | Server generated channel ID, same as in create channel response. |
|       requestID | Request ID, same as in init message.                             |
|      subcommand | 0x00 for RPC, additional 0x10 mask for DESTROY.                  |
|   pvStructureIF | pvStructureData Field description.                               |
| pvStructureData | Argument data structure.                                         |
:::

:::{table} Channel RPC response
:align: center

|         Member | Description                             |
| -------------: | --------------------------------------- |
|      requestID | Request ID, same as in request message. |
|     subcommand | Same as in request message.             |
|         status | Completion status.                      |
|   pvResponseIF | pvResponseDataField description.        |
| pvResponseData | Response data structure.                |
:::

### CMD_CANCEL_REQUEST (0x15)

A "cancel request" messages is used cancel any pending request, i.e. an
instance with requestID.

```c
// cancel any request with given requestID
struct cancelRequest {
    int serverChannelID;
    int requestID;
};
```

:::{table} Cancel request
:align: center

|          Member | Description                                                      |
| --------------: | ---------------------------------------------------------------- |
| serverChannelID | Server generated channel ID, same as in create channel response. |
|       requestID | Request ID, same as in request init message.                     |
:::

### CMD_ORIGIN_TAG (0x16)

When a client or server receives a packet containing a Search message with
flagged "sent as unicast" it may resend this as a multicast to "224.0.0.128"
through the loopback interface ("127.0.0.1").  A forwarded packet must
change Search messages flagged "sent as unicast" to "send as broadcast",
and prefix the packet with an Origin Tag message containing the address to which
the receiving socket was bound.  This may be "0.0.0.0", an interface
address, or a local broadcast address depending on the host OS.

A server which wishes to receive forwarded unicast Search messages should
listen for "224.0.0.128" through the loopback interface.  aka. join group
"224.0.0.128" on interface "127.0.0.1".  Received packets should be handled
in one of three ways.

1. A packet which is prefixed with an Origin Tag message containing a
forwarderAddress which matches one or more of a server's socket bind addresses
shall be processed as if it was received through each matching socket.
At exception to this is that a forwarded message must never be re-forwarded,
even if containing Search messages flagged as "sent as unicast".

2. If the host OS (like Windows) does not support receiving only multicast messages,
then any packet not prefixed with an Origin Tag, and containing a Search message
flagged "sent as unicast" should be forwarded.

3. Other packets must be ignored.

A forwarderAddress is considered to match a server's socket bind address if
a socket bound to either address could have received the original packet.
This is an OS dependent process.  A suggested start point is to consider
a match if either forwarderAddress or socket bind address is "0.0.0.0"
(INADDR_ANY).  Identical forwarderAddress and bind address also match.

```c
// Indicate who forwarded the search request
struct originTag {
    byte[16] forwarderAddress;
};
```

## Control Messages

This section describes the message payloads for control messages. Each
subsection describes a single message command
(*pvAccessHeader.messageCommand*).

Control messages have no payload and are used internally by the
protocol, for instance to handle byte order management and flow control.

The payload size field contains control message specific values.

### Mark Total Byte Sent (0x00)

Note that this message type has so far not been used.

The payload size field holds the value of the total bytes sent. The
client SHOULD respond with an acknowledgment control message (0x01) as
soon as possible.

### Acknowledge Total Bytes Received (0x01)

Note that this message type has so far not been used.

The payload size field holds the acknowledge value of total bytes
received. This must match the previously received marked value as
described above.

### Set byte order (0x02)

The 7-th bit of a header flags field indicates the server's selected
byte order for the connection on which this message was received. Client
MUST encode all the messages sent to the server via this connection using this byte
order.  
The client's decoding byte order for messages received from the server depends on the payload size field value as
follows:

:::{table} Client Decoding
:align: center

| Payload Size Field Value | Meaning                                                                                                         |
| ------------------------ | --------------------------------------------------------------------------------------------------------------- |
| 0x00000000               | Client MUST decode all the messages received via this connection using server's selected byte order.            |
| 0xFFFFFFFF               | Client MUST decode all the messages sent received this connection as indicated by each message byte order flag. |
:::

:::{note}
Existing implementations have been found to ignore the "payload size".
They decode each received message based on the byte order bit in the message header flags field,
i.e., they always behave as per "payload size" = 0xFFFFFFFF.
:::

This MUST be the first message sent by a server when connection is
established. For connection-less protocols this message is not sent and
byte order is determined per message using its byte order flag.

:::{note}
This message is byte order independent.
:::

### Echo request (0x03)

Diagnostic/test echo message. The receiver should respond with an Echo
response (0x04) message with the same payload size field value.

### Echo response (0x04)

Response to a echo request. The payload size field contains the same
value as in the request message.
