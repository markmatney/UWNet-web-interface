# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import subprocess
import serial

kermit_port_1 = serial.Serial(port='/dev/ttyUSB0', baudrate=38400, parity=PARITY_NONE, stopbits=STOPBITS_ONE, timeout=None)

kermit_port_2 = serial.Serial(port='/dev/ttyUSB1', baudrate=38400, parity=PARITY_NONE, stopbits=STOPBITS_ONE, timeout=None)

commands = ["+++A", "$HHCRW, TXPWR, 100"]

for i in commands:
    kermit_port_1.write(i)
    kermit_port_2.write(i)

kermit_port_1.close()
kermit_port_2.close()


