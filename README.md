# Haier RS485 🔌❄️

[![GitHub release](https://img.shields.io/github/v/release/DieBambusleitung/haier_rs485)](https://github.com/DieBambusleitung/haier_rs485/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An open-source project for local control, monitoring, and automation of Haier air conditioners and heat pumps via the RS485 interface.

## 📖 Overview

This project allows you to integrate Haier devices equipped with an RS485/Modbus port into HomeAssistant. 
The main benefit: **100% local control without any cloud dependency!** Zero latency, no data tracking, and fully operational even without an internet connection.

## ✨ Features

- **Local Control**: 100% cloud-free, running entirely on your local network.
- **Status Monitoring**: Read current temperature, operation mode, fan speed, error codes, and more in real-time.
- **Command Dispatching**: Change target temperature, switch modes (Cool, Heat, Dry, Auto), and control fan speeds.

## 🛠 Hardware Requirements

To use this project, you will need:
- A compatible Haier HVAC unit with an available RS485 port. (I could only test it with the HAIER AU082FYCRA(HW), but other models may work aswell)
- An RS485-To-Ethernet converter (I'm using one from Waveshare (https://www.waveshare.com/rs485-to-eth-for-eu.htm), but I am sure other ones will work fine aswell).
- Suitable wiring (Twisted pair cabling is highly recommended for the RS485 A/B lines).

## 🔧 Enabling Modbus on the Heatpump

**This is an optional step, as you can also use the pins of the Control Unit (YR-E27)**

If you wish to use the desired Modbus Port on the PCB of the Heat Pump, you must enable it before you can send and receive data to/from it. As of the documentation you have to set the BM2_5 Pin switch to "ON" in order to enable the Modbus Function on Port CN31.

## 🔭​ Configuration of the RS485 to Ethernet controller



## 🔌 Wiring Diagram

Connect either the A and B Pins of the Cable for the Control Unit (YR-E27) OR X and Y on the CN31 connector on the PCB to the RS485 to ETH controller.

⚠️ **Important – These Ports may vary depending on your used RS485 to ETH controller!!! If you run into issues, try switching the pins. This will NOT break your Heat Pump or your controller!**

*When connecting to the YR-E27*

| Haier Device | RS485 Module |
|--------------|--------------|
| `A         ` | `A`          |
| `B         ` | `B`          |
| `GND       ` | EMPTY        |
| `+12V      ` | EMPTY        |

*When connecting to the CN31 Ports*

| Haier Device | RS485 Module |
|--------------|--------------|
| `Y         ` | `A`          |
| `X         ` | `B`          |

## 🩸​ Known Issues

- Unfortunately, the current water temperature is read wrong. This seems to be an issue with the used PyHaier Library, which I will investigate in the future.

## 🧡 Contributing

Contributions are always welcome!


## Disclaimer

This project is not affiliated with or endorsed by Haier. All trademarks are property of their respective owners.