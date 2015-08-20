'''
STEPS:

0. Configure the port on our machine using kermit
1. Query database for experiments that are ready to run
2. Set up experiment logfile
3. Run the experiment on each combination of { pwr, bkn, mod }
4. Handle results (send to database: insert, update, etc.)

'''

import math, sys, string, random, subprocess, serial #, pty
from time import gmtime, strftime, clock, time	# for timestamping packets
import time
import hashlib #for checksum purposes

sys.path.append('/usr/lib/python2.7/dist-packages')

################################################################################
### Auxiliary functions
################################################################################

### Packetize (adapted from SUB_PKT.SH)
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

#print subpkt(1000000003,1,5,385,909)

def xor_string_hash(string):
  ret = 0
  for char in string:
    ret ^= ord(char)
  return hex(ret)[2:]

################################################################################
### 0. Configure the port on our machine using kermit
################################################################################

port_ttyUSB0 = serial.Serial(port='/dev/ttyUSB0', baudrate=38400)
port_ttyUSB1 = serial.Serial(port='/dev/ttyUSB1', baudrate=38400, timeout=5)

port_ttyUSB0.write("+++A\r\n$HHCRW,MMCHK,1\r\n")
if ("MMOKY" not in port_ttyUSB0.readline()):
  print 'error in entering command mode for ttyUSB0'
  exit(0)
if ("MMOKY" not in port_ttyUSB0.readline()):
  print 'error in setting the checksum register for ttyUSB0'
  exit(0)

port_ttyUSB1.write("+++A\r\n$HHCRW,MMCHK,1\r\n")
if ("MMOKY" not in port_ttyUSB1.readline()):
  print 'error in entering command mode for ttyUSB1'
  exit(0)
if ("MMOKY" not in port_ttyUSB1.readline()):
  print 'error in setting the checksum register for ttyUSB1'
  exit(0)

################################################################################
### 1. Query database: http://dev.mysql.com/doc/refman/5.5/en/index.html
################################################################################

# https://docs.python.org/2/howto/webservers.html?highlight=mysql
# http://dev.mysql.com/doc/connector-python/en/connector-python-example-cursor-select.html
import mysql.connector
cnx = mysql.connector.connect(user='mark', password='pass', host='localhost', database='UWNet')
cursor = cnx.cursor()

# may not need email

# selects those rows in the InputQueue table with experiments that have not yet been run
query = ("SELECT id, mpwr, lpwr, ppwr, mbkn, lbkn, pbkn, mmod, lmod, pmod, testData FROM InputQueue WHERE exitStatus IS NULL")
cursor.execute(query)

print cursor

# at the end of the for loop, go thru this list and insert elements into the results table
allResults = {}

#time interval between packets
spl = 10

################################################################################
### 2. Set up experiment logfile
################################################################################

# TODO: may want to remove logging when debugging is complete, or allow it to be toggled
rptt = 2 # number of times to repeat experiment
psn = 1 # delay (sleep time), may not need to use

rtc = strftime("%y%m%d%H%M", gmtime())
logn = 'T{0}.LOG'.format(rtc)
print 'Start test: {0}'.format(rtc)

################################################################################
### 3. Run the experiment on each combination of { pwr, bkn, mod }
################################################################################

# record results in variable (resultsList)

for (id, mpwr, lpwr, ppwr, mbkn, lbkn, pbkn, mmod, lmod, pmod, testData) in cursor:
  resultsList = []
  testDataString = str(testData)
  # handle each enqueued experiment
  # report errors, store in database
  # code NULL: exited normally
  # code NOT NULL: error
  #  - KE: kermit configuration
  #  - DB: database access
  #  - PT: port configuration
  #  - etc...

  for transmission_mode in range(lmod, mmod + 1, pmod):

    print '### Sending in Mode {0}'.format(transmission_mode)

    for blocks_per_packet in range(lbkn, mbkn + 1, pbkn):
 
      print '### Sending {0} blocks'.format(blocks_per_packet)

      if transmission_mode == 1:
          packet_length = blocks_per_packet * 38
      elif transmission_mode == 2:
          packet_length = blocks_per_packet * 80
      elif transmission_mode == 3:
          packet_length = blocks_per_packet * 122
      elif transmission_mode == 4:
          packet_length = blocks_per_packet * 164
      elif transmission_mode == 5:
          packet_length = blocks_per_packet * 248
      else :
          print("ERROR:Transmit mode ranges from 1 to 5")
          exit(0)

      data_size = len(testDataString)
      n_packets = int(math.ceil(float(data_size)/packet_length))
  
      for transmission_power in range(lpwr, mpwr + 1, ppwr):

        print '### TXPRW changed to {0}\n'.format(transmission_power)
        port_ttyUSB0.write("$HHCRW,TXPWR,{0}\r\n".format(transmission_power))

        collectionOfTrials = {}

        for trial in range(rptt): # repeat the experiment!

          print 'sending data now'

          # keep track of packet loss, retransmissions, and execution time
          n_loss = 0
          n_retx = 0
          start_time = time.time() 

          #####################################################
          # transmit data here
          #####################################################
          
          # send each packet
          for i in range(n_packets):
            if i == n_packets - 1:
              packet_to_send = testDataString[i*packet_length:]
            else:
              packet_to_send = testDataString[i*packet_length:(i+1)*packet_length]

            checksum = xor_string_hash("HHTXA,0,{0},{1},{2}".format(transmission_mode, transmission_power, packet_to_send))

            # TODO: implement checksum
            port_ttyUSB0.write("$HHTXA,0,{0},{1},{2}\r\n".format(transmission_mode, transmission_power, packet_to_send))
            read_buffer = port_ttyUSB1.readline();

            # TODO: extract data from read_buffer
            print "Read buffer: ", read_buffer, "\nsent: ", packet_to_send, "\nhash: ", checksum
	    if len(read_buffer) == 0: # loas a packet TODO: replace with timeout check
              n_loss += 1

          # TODO: keep track of loss, number of retransmissions, etc.

          execution_time = time.time() - start_time
          collectionOfTrials[trial] = { "delay": execution_time, "loss": n_loss, "retx": n_retx }
          print "Elapsed time: {} seconds".format(execution_time)

        print # empty line

        # add the trial collection to resultsList
        resultsList.append( { 'parameters': { 'pwr': transmission_power, 'bkn': blocks_per_packet, 'mod': transmission_mode }, 'results': collectionOfTrials } )

  allResults[id] = resultsList

################################################################################
### 4. Handle results
################################################################################

# insert results into the results table
for experimentId in allResults:
  for param_combo in allResults[experimentId]:
    add_row = ("INSERT INTO Results VALUES({0}, \"{1}\", \"{2}\")".format(experimentId, param_combo["parameters"], param_combo["results"]))
    cursor.execute(add_row)
    cnx.commit()

# TODO: record exit status, which will determine if we need to rerun the experiments, require manual intervention, or are ready to be emailed to client

cursor.close()
cnx.close()
exit(0)
