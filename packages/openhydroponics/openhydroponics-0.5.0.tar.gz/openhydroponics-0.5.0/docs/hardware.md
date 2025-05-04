# Hardware

```{toctree}
:hidden: true
:maxdepth: 2

hardware/architecture
hardware/rootmaster
hardware/rootsense
hardware/sensorhats
```

<a href="https://lectronz.com/stores/mickeprag" alt="Buy it on Lectronz" target="_blank"><img src="https://lectronz-images.b-cdn.net/static/badges/buy-it-on-lectronz-small.png" /></a>

## Architecture

OpenHydroponics is build using a modular approach using a CANbus as its core network. New nodes can be added to extend the functionality to fit any custom growing needs. Read more about the {doc}`architecture </hardware/architecture>`.

## RootMaster

The {doc}`RootMaster </hardware/rootmaster>` is the central hub of the OpenHydroponics system. It coordinates the activities of all connected devices, ensuring that they work together seamlessly to maintain optimal growing conditions for your plants. The RootMaster collects data from various sensors, processes it, and then sends commands to actuators to adjust environmental parameters such as light, temperature, and humidity.

## RootSense

The {doc}`RootSense </hardware/rootsense>` is an add-on development board designed to be used together with RootMaster when the built-in sensing capabilities are not enough. Currently it can extend RootMaster with pH reading capabilities.

## Sensor hats

RootMaster and RootSense have a modular sensor interface where the type of probe supported can be changed. Each type of sensor probe is supported using a replacable {doc}`sensor hat </hardware/sensorhats>`.
