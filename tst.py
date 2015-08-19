# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import subprocess
import serial

kermit_port_1 = serial.Serial(port, '/dev/ttyUSB0', baudrate = 38400, parity = 'N', stopbits = 1, timeout = None, xonxoff = 0, rtscts = 0)

kermit_port_2 = serial.Serial(port, '/dev/ttyUSB1', baudrate = 38400, parity = 'N', stopbits = 1, timeout = None, xonxoff = 0, rtscts = 0)

kermit_port_1.

commands = ["+++A", "$HHCRW, TXPWR, 10"]

for i in commands:
    kermit_port_1.write(i)
    kermit_port_2.write(i)

kermit_port_1.close()
kermit_port_2.close()


