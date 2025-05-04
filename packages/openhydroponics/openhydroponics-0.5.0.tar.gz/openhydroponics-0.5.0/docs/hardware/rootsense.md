(rootsense)=

# RootSense

<a href="https://lectronz.com/products/rootsense" alt="Buy it on Lectronz" target="_blank"><img src="https://lectronz-images.b-cdn.net/static/badges/buy-it-on-lectronz-small.png" /></a>

```{image} /_static/hw/rootsense/rootsense.png
:alt: RootSense
:width: 650
:align: center
```


The RootSense is a add-on development board designed to be used togheter with RootMaster when the built in sensing capabilities is not enough.

Key Features:
 - Atlas Scientific Sensor Integration: Effortlessly monitor pH, Electrical Conductivity (EC), Dissolved Oxygen (DO), Temperature, and more with the industry’s most trusted sensors.
  ```{note}
  EZO™ pH Circuit must be purchased separately.
  ```
- Customizable: The swapable sensing hat allows to use anything from low cost pH probes to Atlas Scientific ranges of probes.

## Power

The RootSense is be powered with 12V through its XT30PW(2+2) connector.

## STM32G473

At the core there is a STM32G473 that is connected to the sensor interface.

### CAN-FD

There is a CANbus connecting the STM32 to the OpenHydroponics network.
This is CAN-FD compatible with a speed of 1 Mbit/s. It is connected to the
`FDCAN3` peripheral in the MCU.

On the board there is a 2 pin pinsocket for termination. Adding a jumper to this will connect a 120 Ω resistor to the CAN bus.

| **Pin Number** | **Pin Name** | **Connected To** | **Note**            |
|----------------|--------------|------------------|---------------------|
| 40             | PB3          | CAN-TX           |                     |
| 41             | PB4          | CAN-RX           |                     |

### LEDs

RootSense has two leds for status and debug. Both yellow.

| **Pin Number** | **Pin Name** | **Connected To** | **Note**            |
|----------------|--------------|------------------|---------------------|
| 2              | PC13         | LED1             | Active Low          |
| 3              | PC14         | LED2             | Active Low          |

### pH

The pH sensor interface must be used togheter with one of the {doc}`sensor hats </hardware/sensorhats>`.
This interface is connected to the i2c bus `I2C1`. Please see the respecive documentation for each on how to intefrate them into the software.

There is a GPIO on RootSense that enables the pH peripheral that must be enabled before any readings can be performed.

| **Pin Number** | **Pin Name** | **Connected To** | **Note**            |
|----------------|--------------|------------------|---------------------|
| 14             | PA6          | Disable          | Active high, must be low to turn on sensor readings |
| 44             | PB7          | I2C1 SDA         |                     |
| 39             | PA15         | I2C1 SCL         |                     |
