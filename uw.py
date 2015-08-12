### Module overview
### 

import sys	# for getting command line arguments passed to this script
import string	# for string functions
import random	# for getting random characters (see subpkt)
import pty	# for pseudo teletype
import serial	# for serial ports
import subprocess	# for running shell scripts
import os.path		# for os.path.isfile 
from time import gmtime, strftime	# for timestamping packets

# used for 1. Get form data
import cgi, cgitb	# for form processing
from StringIO import StringIO
import json
from io import BytesIO
import pycurl

### 1. Get form data
### TODO: Get from database instead: http://dev.mysql.com/doc/refman/5.5/en/index.html
### https://docs.python.org/2/howto/webservers.html?highlight=mysql
 
cgitb.enable()
# Create instance of FieldStorage 
form = cgi.FieldStorage() 

# Get data from fields
param_power = form.getvalue('power')
param_mode = form.getvalue('mode')
param_pktlen = form.getvalue('pkt_length')
param_pktnum = form.getvalue('pkt_number')

# print to console? or prints to browser
print param_power, param_mode, param_pktlen, param_pktnum
exit(0)

### 2. Packetize (adapted from SUB_PKT.SH)

# Returns string representing the packet containing a
#   timestamp,
#   power level,
#   transmission mode,
#   packet length,
#   and id number.
def subpkt(rtc, pwr, mod, plt, psn):
  # check number of args (arity check)
  # check argument format
  #  ensure datetime is 10 digits
  #  ensure power is in [-127,0]
  #  ensure txmode is in [1,5]
  #  based on value of txmode, check that pktlen is correct
  #  ensure pktnum is in [0,9999]

  # just do this error checking before passing it to the backend???

  data = ''.join(random.choice(string.ascii_uppercase) for i in range(plt - 38))
  return 'PTD{0}PRW{1}TMD{2}PLT{3}PSN{4}@{5}'.format(str(rtc), str(pwr).zfill(3), str(mod), str(plt).zfill(4), str(psn).zfill(4), data)



print subpkt(1000000003,1,5,385,909)
exit(0)

#port name
pt = '/dev/ttyUSB1'
#pt = '/dev/pts/23'

#baud rate
bd = 38400

#time interval between packets
spl = 10

#cmode - get from radio button
cmode = "e"

#transmission power
mpwr = 0
lpwr = -120
ppwr = 6

#blocks per packet
mbkn = 8
lbkn = 1
pbkn = 7

#transmit mode
mmod = 4
lmod = 1
pmod = 1

### TODO: setup port, see http://pyserial.sourceforge.net/
ser = serial.Serial(0) #what is the pace of reading data
ser.baud = bd
ser.port = pt
#ser = serial.Serial('~/pty_laptop', 38400)
#print ser.name
#ser.write("hello world")

### 3. FORM CHECKING
### TODO: ^. May want to do this in javascript?

### 4. Port of RUN_CHINFO.SH to Python
### TODO: fill in blanks

#configure the serial port by running:
script_to_config = "kermit CFG_OFDM_38400.KSC"
#TODO: run kermit ^^
p_kermit_0 = subprocess.call(["kermit", "CFG_AQUASENT_KERMIT_38400" ,"-c"])#script interacts with kermit
p_kermit_1 = p_kermit_0 = subprocess.call(["kermit", "CFG_AQUASENT_KERMIT_38400_USB1" ,"-c"])
#need to figure out how to make sure I can send 'c' command to kermit to make sure it is online
#need

#check if ./sub_PKT exists
if not os.path.isfile('./SUB_PKT.SH'):
  print 'ERROR: Need file SUB_PKT.SH'
  exit(0)

# if number of arguments is not equal to 1, print usage and exit
if len(sys.argv) != 1:
  print 'ERROR: Must pass exactly one argument to RUN_CHINFO.SH' 
  exit(0)

rptt = 5 # first command line arg, number of times to repeat (repeat time)
psn = 1
mod = lmod
rtc = strftime("%y%m%d%H%M", gmtime())
logn = 'T{0}.LOG'.format(rtc)
print 'Start test: {0}'.format(rtc)
# write whatever is written to the port, to the file given by logn
# spid = get process id
if cmode == "e":
  # echo "\$HHCRW,TXPWR,-6" >> $PT
  print ''
  # sleep 1
  # echo "\$HHTXA,0,0,0,STARTEXPERIMENT$RTC" >> $PT
elif cmode == "p":
  print 'p'
  # print to console
  # printf "\$HHCRW,TXPWR,-6\r\n" >> $PT
  # sleep 1
  # printf "\$HHTXA,0,0,0,STARTEXPERIMENT$RTC\r\n" >> $PT
#this is not for us for we don't have access to this mode. 
elif cmode == "a":
  print 'a'
  # call shell script: aqecho
  # aqecho $PT $BD \$HHCRW,TXPWR,-6
  # sleep 1
  # aqecho $PT $BD \$HHTXA,0,0,0,STARTEXPERIMENT$RTC
else:
  print "ERROR: CMODE should be e/p/a"
  exit(0)

# sleep for spl seconds

#TODO: use mmod + 1, mbkn + 1, lpwr - 1, etc

for i in range(lmod, mmod, pmod):
  print 'Sending in Mode {0}'.format(i)
  for j in range(lbkn, mbkn, pbkn):
    # is this correct? 
    print 'Sending {0} blocks'.format(j)
    # check if block number is in [1,16]


    # COMPOUND IF STATEMENT HERE, checks packet length

    for k in range(mpwr, lpwr, -ppwr):
      # change transmit level
      # if cmode = e/p/a, call echo, printf, or aqecho

      print 'TXPRW changed to {0}'.format(k)

      # repeatedly send out packets
      # if 

print 'End: {0}'.format(rtc)
# kill a process
print "Finished"
