# How to Make Channel Access Reach Multiple Soft IOCs on a Linux Host


```{tags} developer, advanced
```

## UDP Name Resolution: Broadcast vs. Unicast

Running multiple IOCs on one host has an annoying side effect: Clients that are using that host's IP address in their `EPICS_CA_ADDR_LIST` with `EPICS_CA_AUTO_ADDR_LIST=NO` will only reach one of the IOCs – usually the one that was started last. All clients have to use broadcasts to reach all IOCs.

The same is true for CA Gateway machines that are set up in a way that makes multiple Gateway processes serve channels into the same network.

The reason is that the kernel delivers UDP broadcasts to _all_ processes that are listening to the IP port, while UDP unicast messages will only be delivered to _one_ of those processes.

## Fix Using iptables

Here's a little helper (for Linux hosts) that I recently was playing around with – based on an idea by Rodrigo Bongers (CNPEM, Brazil).

If you drop the right script in the right place (depending on your Linux distribution, see further down), it will automatically create/delete an iptables rule that replaces the destination address of all incoming CA UDP traffic on each interface with the broadcast address of that interface.

A simple and effective trick: the kernel will see all incoming name resolution requests as broadcasts, and delivers them to all IOCs instead of one.

Note: This will not work for clients on the same host. (Adding that feature makes things a lot more complicated, and I like things to be simple.)

If you need connections between IOCs on one host, I would suggest adding the broadcast address of the loopback interface (usually `127.255.255.255`) to each IOC's `EPICS_CA_ADDR_LIST` setting.

### On Debian and Derivatives

Drop/link the following script into `/etc/network/if-up.d/` and `/etc/network/if-down.d/`.
If your system does not have the ip command, consider updating it (or install package iproute2 from backports).

``` sh
#!/bin/sh -e
# Called when an interface goes up / down

# Author: Ralph Lange <Ralph.Lange@gmx.de>

# Make any incoming Channel Access name resolution queries go to the broadcast address
# (to hit all IOCs on this host)

# Change this if you run CA on a non-standard port
PORT=5064

[ "$METHOD" != "none" ] || exit 0
[ "$IFACE" != "lo" ] || exit 0

line=`ip addr show $IFACE`
addr=`echo $line | grep -Po 'inet \K[\d.]+'`
bcast=`echo $line | grep -Po 'brd \K[\d.]+'`
[ -z "$addr" -o -z "$bcast" ] && return 1

if [ "$MODE" = "start" ]
then
    iptables -t nat -A PREROUTING -d $addr -p udp --dport $PORT -j DNAT --to-destination $bcast
elif [ "$MODE" = "stop" ]
then
    iptables -t nat -D PREROUTING -d $addr -p udp --dport $PORT -j DNAT --to-destination $bcast
fi

exit 0
```

### On RedHat and Derivatives

On systems using NetworkManager, drop the script below into `/etc/NetworkManager/dispatcher.d/`. The rules for these files are:

> NetworkManager will execute scripts in the /etc/NetworkManager/dispatcher.d directory in alphabetical order in response to network events. Each script should be (a) a regular file, (b) owned by root, \(c\) not writable by group or other, (d) not set-uid, (e) and executable by the owner. Each script receives two arguments, the first being the interface name of the device just activated, and second an action.

``` sh
#!/bin/sh -e
# Called when an interface goes up / down

# Author: Ralph Lange <Ralph.Lange@gmx.de>

# Make any incoming Channel Access name resolution queries go to the broadcast address
# (to hit all IOCs on this host)

# Change this if you run CA on a non-standard port
PORT=5064

IFACE=$1
MODE=$2

[ "$IFACE" != "lo" ] || exit 0

line=`/sbin/ip addr show $IFACE`
addr=`echo $line | grep -Po 'inet \K[\d.]+'`
bcast=`echo $line | grep -Po 'brd \K[\d.]+'`

[ -z "$addr" -o -z "$bcast" ] && return 1

if [ "$MODE" = "up" ]
then
    /sbin/iptables -t nat -A PREROUTING -d $addr -p udp --dport $PORT -j DNAT --to-destination $bcast
elif [ "$MODE" = "down" ]
then
    /sbin/iptables -t nat -D PREROUTING -d $addr -p udp --dport $PORT -j DNAT --to-destination $bcast
fi

exit 0
```

Enjoy!  
Ralph

