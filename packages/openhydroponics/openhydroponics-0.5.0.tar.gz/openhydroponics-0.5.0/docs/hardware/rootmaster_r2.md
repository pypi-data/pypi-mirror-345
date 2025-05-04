(rootmaster_r2)=

# Rev 2

```{warning}
The Raspberry Pi has been rotated 180° in later revisions. Please note the revision of your board before connecting the
Raspberry Pi since it will be damaged if connected the wrong way!
```

![RootMaster features](/_static/hw/rootmaster/rootmaster.jpg)

## Power

The RootMaster can be powered in two ways: via USB Power Delivery (USB-PD) or through a 12V barrel jack. The USB-PD
input allows for flexible power options and can be used with a variety of USB-C power adapters. Please note that the
USB-C power adapter must be 12 V capable. The 12 V barrel jack provides a more traditional power input method, suitable
for use with standard 12 V power supplies.

## STM32G473

At the core there is a STM32G473 that is connected to all external peripherals.

### Hardware rev

The hardware revision can be read through 3 gpios. On rev 2 all should be read as zero.

| **Pin Number** | **Pin Name** | **Connected To** | **Note**            |
|----------------|--------------|------------------|---------------------|
| 8              | PA0          | HW rev 0         | Should be read as 0 |
| 9              | PA1          | HW rev 1         | Should be read as 0 |
| 10             | PA2          | HW rev 2         | Should be read as 0 |

### CAN-FD

There is a CANbus connecting the STM32 to Raspberry Pi and the external connection.
This is CAN-FD compatible with a maximum speed of 1 Mbit/s. It is connected to the
`FDCAN3` peripheral in the MCU.

| **Pin Number** | **Pin Name** | **Connected To** | **Note**            |
|----------------|--------------|------------------|---------------------|
| 40             | PB3          | CAN-TX           |                     |
| 41             | PB4          | CAN-RX           |                     |

### LEDs

RootMaster has two leds for status and debug. Both yellow.

| **Pin Number** | **Pin Name** | **Connected To** | **Note**            |
|----------------|--------------|------------------|---------------------|
| 2              | PC13         | LED1             | Active Low          |
| 3              | PC14         | LED2             | Active Low          |

### Internal temperature and humidity sensor

There is an internal temperature and humidity sensor [HDC1080](https://www.ti.com/product/HDC1080) connected to `I2C0`.

Note: The i2c bus is also shared with the EC/temp sensor.

| **Pin Number** | **Pin Name** | **Connected To** | **Note**            |
|----------------|--------------|------------------|---------------------|
| 39             | PA15         | I2C0 SCL         |                     |
| 44             | PB7          | I2C0 SDA         |                     |

### Temperature

```{image} /_static/hw/rootmaster/ntc.png
:alt: NTC thermistor
:width: 150px
:align: right
```

The NTC temperature sensor is connected to the STM32G473 on pin 12 (PA4). This sensor is used to measure the temperature
of the nutrient solution. The resistance of the NTC decreases as the temperature increases, and this change in
resistance is measured by the ADC to determine the temperature.

The NTC temperature sensor is connected as part of a voltage divider circuit. The voltage divider is formed by the NTC
thermistor and a fixed 49.9kΩ resistor. The output voltage of the divider, which varies with temperature, is fed into
the ADC of the STM32G473 to measure the temperature.

| **Pin Number** | **Pin Name** | **Connected To** | **Note**            |
|----------------|--------------|------------------|---------------------|
| 12             | PA4          | NTC Temperature  | Analog input        |

### pH

The pH sensor interface is using an [ADS1115](https://www.ti.com/product/ADS1115) ADC connected to `I2C1`. The input
signal is an analog input ranging from -2.035 V to +2.035 V where -2.035 V is 0 pH, 0 V is 7 pH, and +2.035 V is 14 pH.
To read this the ADC must be configured to read AIN0 and AIN1 as a differential input. There is also a GPIO that enables
the pH peripheral that must be enabled before any readings can be performed. The 7 bit i2c address is `0x49`.

| **Pin Number** | **Pin Name** | **Connected To** | **Note**            |
|----------------|--------------|------------------|---------------------|
| 14             | PA6          | pH disable       | Active high, must be low to turn on sensor readings |
| 30             | PA8          | I2C1 SDA         |                     |
| 31             | PA9          | I2C1 SCL         |                     |

### EC and temperature

| **Pin Number** | **Pin Name** | **Connected To** | **Note**            |
|----------------|--------------|------------------|---------------------|
| 13             | PA5          | EC disable       | Active high, must be low to turn on sensor readings |
| 39             | PA15         | I2C0 SCL         | Shared with temp/hum |
| 44             | PB7          | I2C0 SDA         | Shared with temp/hum |

#### EC

The EC interface is using an [ADS1115](https://www.ti.com/product/ADS1115) ADC connected to `I2C0`. The 7 bit i2c
address is `0x48`. The EC value will be converted to a voltage on the `AIN0` pin on the ADC. To work with as many probes
as possible it is possible to set the gain using a [MCP4017](https://www.microchip.com/wwwproducts/en/MCP4017) digital
potentiometer at the 7 bit address `0x2F`. There is also a GPIO that enables the EC peripheral that must be enabled
before any readings can be performed.

#### Temperature

```{image} /_static/hw/rootmaster/ntc.png
:alt: NTC thermistor
:width: 150px
:align: right
```

There is a NTC interface connected to the same ADC as the EC on the `AIN2` pin. The temperature NTC is connected as the
bottom part of a voltage divider connected between 5 V and GND. The upper resistor is 49.9kΩ and must be taken into
account when calculating the temperature.

<br style="clear: both;" />

### Flow

The flow meter is connected to a GPIO pin and sends pulses proportional to the flow rate. Each pulse represents a fixed
volume of liquid passing through the meter. The STM32G473 counts these pulses to measure the flow rate and total volume.

| **Pin Number** | **Pin Name** | **Connected To** | **Note**            |
|----------------|--------------|------------------|---------------------|
| 11             | PA3          | Flow meter       | Pulse input         |

### Digital in

There are 3 digital inputs that can be connected to various NC/NO sensors such as water level sensor or similar. All
three inputs have pull ups connected to 3.3 V.

| **Pin Number** | **Pin Name** | **Connected To** | **Note**            |
|----------------|--------------|------------------|---------------------|
| 46             | PB9          | IN 1             |                     |
| 43             | PB6          | IN 2             |                     |
| 42             | PB5          | IN 3             |                     |

### 12V high side switches

There are 6 high side switch outputs that can be used to connect valves or pumps. These outputs are capable of switching
0-12 V and are controlled using PWM signals from the STM32G473. Each switch can be individually controlled to regulate
the power supplied to the connected devices.

| **Pin Number** | **Pin Name** | **Connected To** | **Note**            |
|----------------|--------------|------------------|---------------------|
| 29             | PB15         | Valve 1          |                     |
| 28             | PB14         | Valve 2          |                     |
| 27             | PB13         | Valve 3          |                     |
| 15             | PA7          | Pump 1           | TIM3 CH2            |
| 17             | PB1          | Pump 2           | TIM3 CH4            |
| 25             | PB11         | Pump 3           | TIM2 CH4            |

## Raspberry Pi

The Raspberry Pi is used as the main controller for the RootMaster. To enable CAN on the Raspberry Pi, you need
to modify the device tree overlay settings.

### Enabling CAN

To enable the CANbus on the Raspberry Pi, follow these steps:

1. Open the boot configuration file:
    ```sh
    sudo nano /boot/firmware/config.txt
    ```

2. Add the file `rootmaster.dtb` to `/boot/firmware/overlay`

3. Open the systemd network configuration file:
    ```sh
    sudo nano /etc/systemd/network/80-can.network
    ```

4. Add the following:
    ```sh
    [Match]
    Name=can*

    [CAN]
    BitRate=1000000
    DataBitRate=1000000
    FDMode=yes
    ```

5. Save the file and exit the editor.

6. Reboot the Raspberry Pi to apply the changes:
    ```sh
    sudo reboot
    ```

### 1-Wire

To 1-Wire interface will be activated automatically by the `rootmaster.dtb` overlay

Verify that the 1-Wire devices are detected:

```sh
ls /sys/bus/w1/devices/
```

You should see a directory for each connected 1-Wire device.

## Compatible peripherals

This is a list of peripherals that has been tested.

| **Peripheral**       | **Link**                                                            |
|----------------------|---------------------------------------------------------------------|
| Water pump 12V       | [AliExpress](https://www.aliexpress.com/item/1005006004929453.html) |
| EC + temperature     | [AliExpress](https://www.aliexpress.com/item/1005004315383393.html) |
