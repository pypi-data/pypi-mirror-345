# CAN FD Protocol

## Overview
This document describes the CAN FD (Controller Area Network with Flexible Data-Rate) protocol used in the
OpenHydroponics system. CAN FD is an extension of the classical CAN protocol, allowing for higher data rates and larger
data payloads.

OpenHydroponics is using the extended frame format with 29 bit arbitration bit and communicates at 1 MBit/s.

## Frame Structure
A CAN FD frame consists of the following fields:
- Arbitration Field
- Data Field

### Arbitration Field
The Arbitration Field is a bitfield that builds the header for the message.

The 29 bits are divided into the following subfields:


| Prio  | Destination       | Master | Source | Multiframe | Message type | Message Id   |
|-------|-------------------|--------|--------|------------|--------------|--------------|
| 1 bit | 7 bits            | 1 bit  | 7 bits | 1 bit      | 2 bits       | 10 bits      |

#### Prio

1 bit: 0=high prio, 1=low prio.

#### Destination

The destination node id. 1-127. The maximum nodes on the network is 127 nodes.

#### Master

This bit is set by all messages sent by the master node on the network. By filtering on this bit it is easy for any node to detect if there is a master in the network and get its node id.

#### Source

The source node sending the message. This can be 0 if the node has not been assigned a node id yet.

#### Multiframe

This is 1 if the frame is part of a larger multi frame message.

#### Message type

The type of message. There is three types of messages:
 - Request = 0
 - Response = 1
 - Value = 2

 #### Message id

 The message id of the message. This identifies this message and all messages have predefined ids.

 ## Node id

 All nodes on the network have a 7 bit node id. Nodes must not store or reuse an old node id on reset. The node id is
 assigned by a master node on the network. This is very similar to DHCP in a TCP/IP network.

 ### Node id assignment

 On reset all nodes must use node id 0 for its communication. To request a node id each node sends periodically a [`HeartbeatWithIdRequest(2)`](openhydroponics.net.msg.HeartbeatWithIdRequest) on the network. This message contains a universally unique 32 byte id for the node. The
 master node on the network listen for these kinds of messages and assigns a node id in its node id tables and returns a
 [`IdSet(3)`](openhydroponics.net.msg.IdSet) message containing the same unique id. The destination id for this message is the new node id for the
 node, and the node receiving this message will use the destination node id in the arbitration field to assign itself a
 node id for further communication.

 After receiving a node id the node will continue to send heartbeats periodically but using the [`Heartbeat(1)`](openhydroponics.net.msg.Heartbeat) message instead.
