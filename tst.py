# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import subprocess
import serial

kermit_port_1 = serial.serial(port, '/dev/ttyUSB0', baudrate = 38400, parity = 'N', stopbits = 1, timeout = None, xonxoff = 0, rtscts = 0)

kermit_port_2 = serial.serial(port, '/dev/ttyUSB1', baudrate = 38400, parity = 'N', stopbits = 1, timeout = None, xonxoff = 0, rtscts = 0)

commands = ["+++A", "$HHCRW, TXPWR, 10"]

for i in commands:
    ser.write(i)


