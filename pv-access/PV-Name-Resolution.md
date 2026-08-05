# PVAccess PV Name Resolution

This document specifies the PV name resolution (search) algorithm
as implemented by PVXS,
in enough detail to be re-implemented compatibly in another language.
It is written for EPICS developers implementing or auditing a PVAccess peer.

Key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY"
are used as in RFC 2119\.
Statements marked **\[protocol\]** are required for interoperability
with other PVA implementations.
Statements marked **\[policy\]** describe the behavior PVXS chose;
another peer MAY choose differently without breaking the protocol,
but the scaling properties in [Scaling](#scaling) depend on them.
Statements marked **\[contract\]** are promises of the PVXS API
that application and `Source` authors are entitled to rely on.

All constants cited are collected in [Constants](#constants).

---

## 1\. Model

Name resolution answers one question:
*Which server claims to provide this PV name?*
It is a distinct phase from data transfer.
Its output is a TCP endpoint plus a server identity (GUID),
after which operations proceed over TCP.
In a secure implementation, TCP may be wrapped in TLS.
In the following, TCP is used to represent both TCP and TLS.

The unit of resolution is the **Channel**:
one PV name within one client,
identified by a **CID** (32-bit client-chosen ID).
Resolution is *many-to-one* with respect to application requests —
every operation on the same name shares one Channel
and therefore one search sequence.
Search traffic is proportional to the number of distinct unresolved names,
never to the number of operations.

Three properties define the contract; every other rule follows from them.

**Resolution is unbounded.**
A search repeats indefinitely until some server claims the name
or the application drops all interest.
There is no "PV not found" error and no negative caching.
A name that does not exist yet resolves as soon as it appears.

**Resolution is unreliable but self-healing.**
Searches and replies are datagrams and MAY be lost.
Correctness never depends on any single message arriving —
only on retries continuing.

**Resolution is first-reply-wins.**
The first positive reply resolves the Channel.
There is no election, ranking, or failover among servers claiming the same name.

---

## 2\. Wire messages

Four messages participate.
All carry the standard 8-byte PVA header
(magic, version, flags, command, payload length);
multi-byte fields use the byte order indicated by the header flags.

### `CMD_SEARCH` (0x03) — client to server, UDP or TCP

| Field | Content |
| :---- | :---- |
| `searchSequenceID` | uint32. **\[policy\]** PVXS always sends the constant `0x66696e64` ("find"). |
| `flags` | uint8: `0x01` MustReply, `0x80` Unicast. Other bits reserved, zero. |
| reserved | 3 bytes, zero. |
| `replyAddress` | 16 bytes, IPv6 or IPv4-mapped. All-zero means "reply to the source address of this datagram". PVXS sends all-zero over UDP. For TCP, the reply address is ignored. If the PVA server sends a CMD\_SEARCH\_RESPONSE, it will do so via the TCP connection where it received the CMD\_SEARCH. |
| `replyPort` | uint16 UDP port on which the client expects replies. Zero over TCP. |
| `protocols` | Size-prefixed list of strings. PVXS sends `["tcp"] or ["tls","tcp"]`. An empty list marks a discovery ping (§7). |
| `count` | uint16 number of names following. |
| `names` | `count` × (uint32 CID, size-prefixed name string). |

### `CMD_SEARCH_RESPONSE` (0x04) — server to client, UDP or TCP

| Field | Content |
| :---- | :---- |
| `GUID` | 12 bytes. Stable identity of the responding server instance. |
| `searchSequenceID` | uint32. **\[protocol\]** MUST echo the value from the request. |
| `serverAddress` | 16 bytes. All-zero means "the source address of this reply". |
| `serverPort` | uint16 TCP port. Over TCP, zero means "the port of this connection". |
| `protocol` | String, `"tcp"`. |
| `found` | uint8 boolean. |
| `count` | uint16, followed by `count` × uint32 claimed CIDs. |

### `CMD_BEACON` (0x00) — server to client, UDP

Beacons announce existence and carry no PV names.

| Field | Content |
| :---- | :---- |
| `GUID` | 12 bytes. Stable identity of the announcing server instance. |
| `flags` | uint8, historically named QoS, undefined. PVXS sends zero and ignores the field on receipt. |
| `sequence` | uint8. Incremented per beacon sent. PVXS ignores it on receipt. |
| `changeCount` | uint16. **\[policy\]** PVXS increments it whenever the set of registered Sources changes (§4), but ignores it on receipt: a restarted server is detected from a changed GUID or protocol version, not from this field. |
| `serverAddress` | 16 bytes, IPv6 or IPv4-mapped. All-zero means "the source address of this datagram". PVXS sends all-zero. |
| `serverPort` | uint16 TCP port. |
| `protocol` | String, `"tcp"`. |
| server status | Optional value. PVXS writes the NULL type code `0xff` and ignores this field on receipt. |

### `CMD_ORIGIN_TAG` (0x16) — server to server, UDP over loopback

Prepended to a forwarded `CMD_SEARCH` (§6):
the optional CMD\_ORIGIN\_TAG starts the UDP packet,
followed by the forwarded CMD\_SEARCH within the same UDP packet.

| Field | Content |
| :---- | :---- |
| `originAddress` | 16 bytes, IPv6 or IPv4-mapped. The destination address of the original search datagram, before forwarding. |

---

## 3\. Client algorithm

### 3.1 Channel cache

A client-side cache is optional.
In the PVXS client, an in-memory cache is implemented.
Channels are cached by (name, forced-server).
A request for a cached name reuses the existing Channel
and creates no new search state.

**\[contract\]** An unreferenced Channel is discarded
after two consecutive sweeps of a 10s garbage-collection timer,
so search traffic for an abandoned name stops
within 10–20s of the last reference being released.
After that,
a new client request will create a new search state and restart search traffic.

The CID is assigned at Channel creation
and is stable for the Channel's cache lifetime.
**\[policy\]** PVXS uses the CID as the sole search correlation key
and sends a constant `searchSequenceID`.
Two consequences a re-implementation MUST respect:

- A reply MAY arrive at any time,
  over UDP or over any name-server TCP connection, correlated only by CID.
  It need not correspond to any recently sent request.
- An implementation MUST NOT require replies
  to carry a per-request sequence number,
  and MUST NOT discard a reply because its `searchSequenceID` is unrecognized.

A Channel is in one of four states:
`Searching`,
`Connecting` (TCP being established),
`Creating` (`CMD_CREATE_CHANNEL` sent, reply pending),
or `Active`.
Only `Searching` Channels are searched.

### 3.2 The search ring

Retry scheduling is a timer wheel, not a per-Channel timer.
This is the core of the design and the reason it scales.

**\[policy\]** The client keeps a ring of 30 buckets — each a list of Channels —
plus a cursor.
A repeating timer fires every 1s.
On each tick the bucket under the cursor is emptied,
every `Searching` Channel it held is packed into outgoing search messages,
and each is reinserted into the bucket *n* positions ahead,
where *n* is that Channel's search attempt count,
incremented once per attempt and clamped to the ring size.
Channels no longer `Searching` (or destroyed —
the ring holds weak references) are dropped as the bucket drains;
there is no separate removal step.

Because reinsertion is *n* buckets ahead
and exactly one bucket is drained per second,
the per-Channel retry interval is *n* seconds
and grows by one second per attempt
until it saturates at one full revolution:

| Attempt | Delay since previous | Elapsed |
| :---- | :---- | :---- |
| 1 | 10ms (batch coalescing) | \~0 |
| 2 | 0–1s | \~1s |
| 3 | 1s | \~2s |
| 4 | 2s | \~4s |
| 5 | 3s | \~7s |
| … | … | … |
| 31 | 29s | \~436s |
| 32 and later | 30s | one search per 30s, indefinitely |

A Channel is therefore searched \~12 times in its first minute,
31 times in its first \~7.3 minutes, and twice per minute thereafter.
This is *linear* (arithmetic) backoff, not exponential:
it reacts quickly to a server that is merely slow to start,
while bounding steady-state broadcast load.

Two refinements matter for large clients:

**Initial coalescing.**
A newly created Channel goes not into the ring
but into a separate *initial* list,
and a one-shot 10ms timer is armed.
Every Channel created within that window is searched together in shared packets.
**\[policy\]** This is what makes a tight application loop
creating thousands of operations emit full packets
instead of one packet per name.

**Cohort splitting.**
Channels created together advance in lockstep
and would pile into a single bucket.
On reinsertion,
if the target bucket holds more than 100 entries *more*
than the following bucket,
the Channel is deferred by one extra tick.
This bleeds oversized cohorts into neighbouring buckets
and smooths per-tick bursts.

### 3.3 Packet construction

Names from one drained bucket are packed into as many datagrams as needed.

**\[policy\]** A search datagram is limited to 1400 bytes total,
chosen to stay under a 1500-byte MTU including Ethernet/IP/UDP headers —
IP fragmentation of broadcast traffic is expensive for every host on the subnet.

Fixed overhead is 41 bytes
(8 header
\+ 4 sequence
\+ 4 flags/reserved
\+ 16 reply address
\+ 2 reply port
\+ 5 protocol list
\+ 2 count).
Each name costs `5 + strlen(name)` bytes
(4 CID \+ 1 size prefix, for names shorter than 254 bytes).
Capacity is therefore `floor(1359 / (5 + L))` names per datagram
for mean name length *L* — 54 names at L=20, 38 at L=30, 30 at L=40.

A name that does not fit in the current datagram is deferred to the next.
A single name too long to fit an empty datagram is sent anyway and MAY fragment;
a name too long for the 64 KiB buffer is dropped with an error log.

The initial pvAccessCPP implementation limits channel names to 500 chars
in both the client and server code.

Every constructed datagram is sent to *every* configured destination
and appended to *every* ready name-server TCP connection.
Destination count is a direct multiplier on egress traffic.

### 3.4 Expedited search

Two events shorten latency without altering the ring's structure.
Both use one mechanism: the tick interval switches to 200ms
for exactly one revolution (30 ticks, \~6s),
during which drained Channels are reinserted into the *same* bucket
and their attempt counts are **not** advanced.
Every `Searching` Channel is thus searched once more within \~6s,
and each Channel's position in the backoff schedule is preserved.

**Beacon-triggered.**
A `CMD_BEACON` from a previously unseen (address, protocol) pair,
or one reporting a changed GUID or protocol version for a known pair,
means a server started or restarted.
Beacons are tracked with a 20000-entry cap —
a server in a restart loop cannot evict tracking of other servers —
and entries expire after 360s under a 180s timer.

**Application-triggered.**
`Context::hurryUp()`.
**\[contract\]** It is advisory and idempotent:
it changes only latency, never the outcome,
and is ignored if called more than once per 30s
or while a fast revolution is already in progress.
An application MAY call it after submitting a batch of operations;
an implementation MUST NOT require it for correctness.

### 3.5 Reply processing

On `CMD_SEARCH_RESPONSE` the client resolves the endpoint
(all-zero address means the reply's source address;
over TCP, port 0 means the connection's peer port),
then:

1. If the GUID is in the configured ignore list, discard the reply.
2. If `found` is false with zero claimed names,
   treat it as a discovery announcement (§7) and otherwise ignore it.
   **\[policy\]** A negative reply never suppresses or delays further searching.
3. Ignore protocols other than `"tcp" or "tls"`.
4. For each claimed CID matching a `Searching` Channel: record GUID and
   endpoint, reset the Channel's attempt count to zero, move to `Connecting`,
   and share or create a TCP/TLS connection to that endpoint.
   Connections are pooled per endpoint,
   so resolving 10000 names on one server yields one TCP/TLS connection.
5. For each claimed CID matching a Channel that is *not* `Searching`:
   if the GUID differs from the one recorded,
   log a duplicate-PV-name error and ignore the reply.
   **\[policy\]** No failover and no re-resolution occurs —
   duplicate names across servers are a configuration error to report,
   not to resolve.

**\[policy\]** The UDP receive callback processes at most 40 datagrams
before returning to the reactor, preserving fairness with TCP I/O.
`SO_RXQ_OVFL` is used where available to detect and log dropped replies:
with large name counts, reply bursts can overrun the socket receive buffer,
and an implementation SHOULD size that buffer generously.

### 3.6 Failure and re-entry into search

A claim is a promise about the future, so it can be broken.
Re-entry into `Searching` is damped by *where* in the ring
the Channel is placed:

| Event | Reinserted at | Effective delay |
| :---- | :---- | :---- |
| Channel closed / TCP lost while `Active` | cursor | next tick |
| Transport failure before channel create | cursor \+ 10 | \~10s |
| `CMD_CREATE_CHANNEL` refused after a claim | cursor − 1 | \~30s |

In all three cases the attempt count was reset when the name last resolved,
so backoff restarts from the beginning.
The last row is the important one: a server that claims a name
and then refuses to create it
would otherwise drive a tight search/create/refuse loop,
so such a Channel is placed in the bucket that will be drained *last*.

Channels created with an explicit server address bypass search entirely —
they connect directly, never enter the ring,
and on refusal are retried only when the connection is re-established.

---

## 4\. Server algorithm

A server holds no per-search state.
For each received `CMD_SEARCH`:

1. Drop it if the source address matches the configured ignore list
   (a listed entry with port 0 matches any port from that address).
2. Present *all* names in the message to *every* registered `Source`,
   in Source order, as a single search operation.
   Each Source MAY claim any subset.
3. If no name was claimed **and** the MustReply flag is clear, send nothing.
   **\[protocol\]** If MustReply is set,
   reply even with `found=false` and zero names —
   `pvlist`\-style tools depend on this.
4. Otherwise reply with the server GUID, the echoed `searchSequenceID`,
   an all-zero address, the server's TCP port, `"tcp" or "tls"`, `found=true`,
   and the claimed CIDs.

**\[protocol\]**
A UDP reply MUST be sent to the client's declared reply address and port,
transmitted through the interface the request arrived on,
and sourced from the address the request was sent *to*.
On a multi-homed host,
replying from an arbitrary local address makes replies unusable,
because clients match on the endpoint they can reach.
A TCP reply always returns on the same connection.

The `Source::onSearch()` contract:

- **\[contract\]** A Source MUST claim a name only if it is prepared
  to accept `onCreate()` for that name *immediately*.
  If it cannot, it MUST stay silent and let the client retry —
  silence costs one retry interval, a broken claim costs \~30s (§3.6).
  For example,
  a gateway may react to a search request by attempting to resolve the name,
  but it must only claim the name
  once it is able to successfully proxy the channel.
- **\[contract\]** `onCreate()` MAY be called for a name that was never claimed,
  and a claimed name MAY never be created.
  Search and create are independent.
- **\[contract\]** `onSearch()` is invoked on the UDP receive worker,
  under a read lock on the Source list, for every search reaching the host.
  It MUST NOT block and MUST NOT do I/O.
  On a busy subnet it is among the hottest paths in the process;
  treat it as a hash-table lookup.
- Names are presented as NUL-terminated pointers into the receive buffer,
  valid only for the duration of the call.

**\[policy\]** Beacons are sent to the configured beacon destinations
every 15s for the first 10, then every 180s.
The change-count field is incremented
whenever the set of registered Sources changes.
It is emitted only for the benefit of peers that use it;
the PVXS client ignores it
and detects a restarted server from a changed GUID or protocol version (§3.4).

---

## 5\. Multiple servers per host: unicast forwarding

Broadcast reaches every server on a subnet,
but a *unicast* search reaches only one process per host —
yet several PVA servers commonly share a host, all bound to the same UDP port,
with only one receiving any given unicast datagram.
PVA solves this with loopback multicast forwarding.

**\[protocol\]** A client sets the Unicast flag when, and only when,
the destination is a genuine unicast address:
not multicast, and not a local interface's broadcast address.
A server receiving a search
whose destination is one of its own interface addresses:

1. rewrites the body's reply address to the resolved client reply endpoint —
   the forwarded copy has lost the original UDP source address,
   so the recipient must trust the body;
2. clears the Unicast flag, so the message is not forwarded again;
3. prepends a `CMD_ORIGIN_TAG` carrying the original destination address; and
4. sends the result to `224.0.0.128` with TTL 1 via `127.0.0.1`, assuming IPv4.
   Use \[ff02::42:1\],1@::1 for IPv6.

Every PVA server joins that IPv4 or IPv6 multicast group on loopback,
so all servers on the host see the search and reply directly to the client.

The receiving side accepts an origin tag
only when the datagram arrived on loopback addressed to that multicast group,
accepts at most one tag per datagram,
refuses to forward an already-forwarded message,
and ignores datagrams with a multicast source address.
These four rules together stop the mechanism
from becoming an off-host traffic amplifier;
an implementation MUST keep all of them.
A forwarded search whose reply address is all-zero
is unusable and MUST be dropped.

---

## 6\. TCP name servers

Where UDP is unavailable
(routed WANs, restrictive firewalls, containers)
a client MAY be configured with a list of TCP name servers.
The client maintains persistent connections, retrying every 10s,
and appends every constructed search message to each ready connection
in addition to the UDP destinations.
The same ring, batching, and reply handling apply — only the transport differs.
**\[policy\]** A connection whose transmit buffer already holds more than 64KiB
is skipped for that tick, on the assumption
that a backlogged link is better retried on a later revolution.

Any PVA server can act as a name server: it answers `CMD_SEARCH`
on an established TCP connection exactly as over UDP,
but reports the port of the receiving listener.
The endpoint it names in a reply need not be itself.

---

## 7\. Discovery

A search with an *empty* protocol list, zero names, and MustReply set
is a discovery ping: it asks every server to identify itself.
Servers answer with `found=false` and zero claimed names.
A client with discovery registered
treats such a reply exactly like a received beacon,
unifying active discovery and passive announcement into one code path.
Discovery pings are not driven by the ring —
they are sent once per registration, plus whenever the application asks.
Loss of a server is inferred from beacon timeout,
never from a negative response.

---

## 8\. Scaling

Let *N* be the number of unresolved names,
*L* the mean name length,
*D* the number of search destinations,
and `C = floor(1359 / (5 + L))` the names per datagram.

**Steady state.**
Each name is searched once per 30s,
so the aggregate rate is `N/30` names/s
regardless of how the names were created:

packets/s per destination \= N / (30 \* C)

bytes/s per destination \= N \* (5 \+ L) / 30 (plus \~3% framing)

| *N* | packets/s (L=30) | bit/s per destination | per-tick burst |
| :---- | :---- | :---- | :---- |
| 1 000 | 0.9 | \~11kbit/s | \~1 packet |
| 10 000 | 8.8 | \~110kbit/s | \~9 packets |
| 100 000 | 88 | \~1.1Mbit/s | \~88 packets |
| 1 000 000 | 877 | \~11Mbit/s | \~877 packets |

Multiply by *D*.
A million unresolved names on a broadcast subnet costs
\~11Mbit/s per destination —
which is exactly why the ring saturates rather than backing off further:
the cost becomes bounded and predictable,
and every host on the subnet must parse all of it.

**Cost per resolved name is zero.**
A resolved Channel leaves the ring entirely.
Search load is proportional to the *unresolved* set, not the connected set,
so a client holding a million working Channels emits no search traffic at all.

**Why a ring instead of per-Channel timers.**
For *N* names the ring costs O(1) timers and O(N/30) work per tick,
with per-Channel state of one list node plus a small counter.
Per-Channel timers would cost *N* timer registrations
and an O(log N) priority-queue operation per retry —
and, worse, would emit uncoordinated single-name datagrams
instead of the \~38-name batches that make the packet rates above achievable.
Batching buys two orders of magnitude,
and batching requires many Channels to become due at the same instant.
The ring makes "due at the same instant" the default,
then deliberately spreads the result
(cohort splitting, one bucket per tick)
to avoid bursts.

**Server-side cost** is O(names per message × Sources) per datagram,
entirely on the UDP worker thread,
with no per-search allocation and no retained state.
A server does not track which clients are searching for what,
so a growing client population costs it only the arriving packet rate.

**Load asymmetry.**
Broadcast search is the one PVA operation
whose cost is borne by hosts with no interest in it.
Every rule marked **\[policy\]** above —
the 1400-byte cap, 30s saturation, batching, coalescing, cohort splitting —
exists to reduce that externality rather than to benefit the searching client.
An implementation that short-circuits them will interoperate correctly
and still be a bad neighbour.

---

## 9\. Constants

| Quantity | Value | Role |
| :---- | :---- | :---- |
| Ring size | 30 buckets | Bounds the retry interval |
| Normal tick | 1s | One bucket drained per tick |
| Fast tick (expedited) | 200ms | One revolution ≈ 6s |
| Initial coalescing delay | 10ms | Batches newly created Channels |
| Max steady-state search interval | 30s | Ring size × normal tick |
| Cohort split threshold | 100 entries | Bucket imbalance triggering deferral |
| Max search datagram | 1400 bytes | MTU-safe |
| Max datagrams per receive callback | 40 | Reactor fairness |
| `hurryUp()` holdoff | 30s | Rate limit on expedited search |
| Channel cache sweep | 10s | Two consecutive sweeps discard |
| Beacon tracking limit | 20000 entries | Restart-loop containment |
| Beacon expiry / check interval | 360s / 180s | Server-lost detection |
| Beacon send interval | 15s ×10, then 180s | Fast announce, then steady |
| Name-server reconnect check | 10s | TCP search transport |
| Name-server TX backlog skip | 64KiB | Skip this tick, retry next revolution |
| Default search (UDP) port | 5076 | `$EPICS_PVA_BROADCAST_PORT` |
| Default server (TCP) port | 5075 | `$EPICS_PVA_SERVER_PORT` |

Configuration inputs: `$EPICS_PVA_ADDR_LIST` and `$EPICS_PVA_AUTO_ADDR_LIST`
(search destinations), `$EPICS_PVA_NAME_SERVERS` (TCP transport),
`$EPICS_PVA_BROADCAST_PORT` (search port),
`$EPICS_PVA_SERVER_PORT` (default TCP port),
`$EPICS_PVAS_IGNORE_ADDR_LIST` (server-side source filter),
and `$EPICS_PVAS_BEACON_ADDR_LIST` / `$EPICS_PVAS_AUTO_BEACON_ADDR_LIST` (beacon
destinations).

---

## 10\. What is not promised

An implementation MUST NOT depend on any of the following;
PVXS provides none of them.

- **No completion signal.**
  There is no event, error, or timeout for "this name does not exist".
  Application-level timeouts are the only bound.
- **No ordering.**
  Names submitted together resolve in an unspecified order,
  and later ones MAY resolve first.
- **No fairness between names.**
  All names in a bucket share one tick;
  which datagram a given name lands in is unspecified.
- **No at-most-once search.**
  A name MAY be searched again after being claimed (a reply may be lost,
  or arrive after a retry was already sent),
  and a server MAY receive the same name repeatedly.
  Servers MUST be idempotent with respect to search.
- **No negative caching, no failover, no load balancing,
  no preference among servers.**
  The first positive reply wins for the Channel's lifetime.
- **No guarantee that a claim leads to a channel**,
  and no guarantee that a created channel was ever claimed.
- **No relationship between `searchSequenceID` and correlation.**
  CIDs correlate;
  the sequence number is echoed only for the benefit of peers that do use it.
