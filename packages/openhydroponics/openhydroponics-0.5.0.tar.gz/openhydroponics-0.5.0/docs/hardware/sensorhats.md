(sensorhats)=

# Sensor hats

Both RootMaster and RootSense can have different type of sensing modules depending on what or how to measure the connected sensor or probe.

## OpenHydroponics pH

```{image} /_static/hw/hats/rootsense-ph.png
:alt: OpenHydroponics pH sensor HAT
:align: right
:width: 200px
```

This is our own in-house developed pH sensor module. If can work with either generic pH probes or probes from Atlas Scientific.

The pH sensor interface is using an [ADS1115](https://www.ti.com/product/ADS1115) ADC connected to the i2c bus. The input
signal is an analog input ranging from -2.035 V to +2.035 V where -2.035 V is 14 pH, 0 V is 7 pH, and +2.035 V is 0 pH.
To read this the ADC must be configured to read AIN0 and AIN1 as a differential input. The 7 bit i2c address is `0x49`.

Temperature compensation and calibration must be implemented by the firmware using the module.
<br style="clear: both" />

## Atlas Scientific EZO™ PH

```{image} /_static/hw/hats/ezo-ph.png
:alt: Atlas Scientific EZO pH
:align: right
:width: 200px
```

The Atlas Scientific [EZO™ pH Circuit](https://atlas-scientific.com/embedded-solutions/ezo-ph-circuit) is a highly accurate and versatile pH sensor module and connected to the i2c bus. The EZO™ pH Circuit can work with any standard pH probe and provides readings in the range of 0 to 14 pH with an accuracy of ±0.002 pH.

The module features temperature compensation, which ensures accurate readings even when the temperature of the solution changes. It also has a flexible calibration system that allows for single-point, two-point, or three-point calibration.

The 7 bit i2c address is `0x63`.

<br style="clear: both" />
