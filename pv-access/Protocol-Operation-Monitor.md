# CMD_MONITOR (0x0D)

The "channel monitor" set of messages are used by client agents to
indicate that they wish to be asynchronously informed of changes in the
state or values of the process variable of a channel.

## Setup

Starting with a valid serverChannelID (cf. Create Channel message), a client first
sends a channelMonitorRequest with subcommand==0x08 or 0x88 (if using the pipeline protocol).
The client also chooses a requestID, and provides a pvRequest structure.

The server responds with a channelMonitorResponse having subcommand==0x08 and a Status indicating
whether the Channel supports subscriptions, and that the provided pvRequest is valid.

If the Status is success (OK or WARNING), then a the subscription data Structure is described
and the subscription is established.

The subscription is initially in the Stopped state.
In this state the Server must not send any updates.

## Normal Operation

After a monitor subscription is established either peer may send non-init messages (`subcommand&0xF7`)
asynchronously.

A Client may send a channelMonitorRequest which performs up to three actions.

1. `subcommand&0x80` indicates an acknowledgement (increment) to the pipeline flow control window.

2. `subcommand&0x44==0x44` Changes the subscription state from Stopped to Running.
   `subcommand&0x44==0x04` Changes the subscription state from Running to Stopped.

3. `subcommand&0x10` requests that the subscription be terminated.

A Server subscription update is a channelMonitorResponse with subcommand==0x00 or 0x10.
If 0x10 then this update is the last update, and the subscription has ended.


The changedBitSet lists all elements of the channel data that has changed,
i.e. the following pvStructureData contains only the serialization for those
changed elements.
Note that the changedBitSet may address the same element more than once.
For example, a bitset {0, 1, 2} indicates that the complete structure has changed
(bit 0), and additionally indicates a change in elements 1 and 2, which might be
the first two elements of that structure.
The pvStructureData will only contain the complete structure data once,
it will not repeat data for elements 1 and 2, since they are already contained
in the serialized data addressed by bit 0.

## pvRequest options

standard options

1. `record._options.queueSize`
2. `record._options.pipeline`
3. `record._options.ackAny`

## Pipeline protocol option

Usage of the pipeline protocol option requires both sides to agree
and maintain a flow control window counter indicating the number of
subscription updates which the Server is may send without receiving
another acknowledgement from the Client.

This option is exercised used if the pvRequest includes the field
'record._options.pipeline' having a value convertible to boolean true.
If this field is not present, or not convertible to true, then the Server
may send subscription updates without restriction.

The flow control window counter is established by the client in the initial
channelMonitorRequest message.  If subcommand==0x08, the initial count is zero.
If subcommand==0x88, then the initial count is provided by the 'nfree' message field.

The Server may send a subscription update as long as the flow control counter is non-zero.
Each time an update is sent by the server, and received by the client, the counter is decremented.

The client may send a channelMonitorRequest with subcommand&0x80 and a 'nfree' count
which is added to the counter.

### Acknowledgement Algorithm

In this way, the client can manage the rate at which the server can send update.

A suggested implementation is for the client to maintain a predetermined buffer capacity.
This size is send as the initial window size (counter).
This buffer fills as subscription updates are received, and it is update data is consumed.

Entries in this buffer may be in one of three states.

1. Free.
2. In Use
3. Un-acknowledged

Transitions are:

1. Free -> In Use when a subscription update is received
2. In Use -> Un-acknowledged when the update data has been consumed
3. Un-acknowledged -> Free when an acknowledgement message is sent

The flow control window counter should match the number of Free entries.

The 'nfree' count in an acknowledgement message should never exceed the number
of Un-acknowledged entries.

For reasons of efficiency, it is recommended not to send an acknowledgement
message each time an entries transitions Un-acknowledged -> Free.
A suggested default is to send an acknowledgement when the number of
Un-acknowledged exceeds half of the total buffer capacity.

TODO: describe 'record._options.ackAny' option.

## Request Encoding (Client -> Server)

```c
struct channelMonitorRequest {
    int serverChannelID;
    int requestID;
    byte subcommand;
    if subcommmand&0x08 { // Init
        StructureDesc pvRequestIF;
        PVStructure pvRequest;
        if subcommand&0x80 { // pipeline support
            int nfree; // initial window size
        }
    } else {
        if subcommand&0x80 { // pipeline support
            int nfree; // increment window size
        }
        if subcommand&0x04 {
            if subcommand&0x40 {
                // subscription start
            } else {
                // subscription stop
            }
        }
        if subcommand&0x10 {
            // last request (requestID released)
        }
    }
};
```

## Response Encoding (Server -> Client)

```c
struct channelMonitorResponse {
    int requestID;
    byte subcommand;
    if subcommmand&0x08 { // Init
        Status status;
        if status.type == OK | WARNING {
            FieldDesc pvStructureIF;
        }
    } else {
        if subcommand&0x10 {
            Status status;
            if ! payloadBuffer.empty() {
                BitSet changedBitSet;
                PVField pvStructureData;
                BitSet overrunBitSet;
            }
            // final update (requestID released)
        } else { // normal update
            BitSet changedBitSet;
            PVField pvStructureData;
            BitSet overrunBitSet;
        }
    }
};
```
