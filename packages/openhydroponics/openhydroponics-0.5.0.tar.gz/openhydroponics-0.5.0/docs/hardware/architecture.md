# Architecture

## General

The hardware architecture is loosely based on the architecture from [Klipper3D](https://www.klipper3d.org). There is one
main high level CPU that is running the main software. To this one there is one or several smaller MCUs connected with
more specialized tasks. This connection is made using the CANbus.

Up to 127 smaller secondary MCUs may be connected to one main CPU.

```{graphviz}
digraph CANbusDiagram {
    node [shape=box]; // Default node shape

    RPi [label="RPi", shape=box];
    CANbus [label="CAN adapter", shape="box"];
    CANbus1 [label="", shape=point, width=0.01];

    MCU1 [label="<f0> MCU1|{sensors|actuators}", shape=record];
    MCU2 [label="<f0> MCU2|actuators", shape=record];
    MCU3 [label="<f0> MCU3|sensors", shape=record];

    RPi -> CANbus -> CANbus1 [dir=none]; // Connect RPi to the CAN bus start

    CANbus1 -> MCU1:f0;
    CANbus1 -> MCU2:f0;
    CANbus1 -> MCU3:f0;
}
```

## RootMaster

Using the architecture above we can see that the RootMaster board is a Raspberry Pi + CANbus adapter and one smaller
secondary MCU combined into one board for convenience.

```{graphviz}
digraph CANbusDiagram {
    rankdir=LR;
    node [shape=box];

    subgraph cluster_RootMaster {
        rankdir=LR;
        label = "RootMaster";
        style = "dashed";
        fontname = "bold";

        RPi [label="RPi", shape=box];
        CANbus [label="CAN adapter", shape="box"];
        MCU1 [label="<f0> MCU1|{sensors|actuators}", shape=record];
        CANbus1 [label="", shape=point, width=0.01];
    }

    CANbus2 [label="", shape=point, width=0.01];

    MCU2 [label="<f0> MCU2|actuators", shape=record];
    MCU3 [label="<f0> MCU3|sensors", shape=record];

    RPi -> CANbus -> CANbus1 -> CANbus2 [dir=none];

    CANbus1 -> MCU1:f0 [dir=none];
    CANbus2 -> MCU2:f0;
    CANbus2 -> MCU3:f0;
}
```
