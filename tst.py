# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import subprocess

#configure the serial port by running:
script_to_config = "kermit CFG_OFDM_38400"
#TODO: run kermit ^^

p = subprocess.call(["kermit", "CFG_AQUASENT_KERMIT_38400" ,"-c","+++A"])

