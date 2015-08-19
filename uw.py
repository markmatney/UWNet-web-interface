'''
STEPS:

0. Configure the port on our machine using kermit
1. Query database for experiments that are ready to run
2. Set up experiment logfile
3. Run the experiment on each combination of { pwr, bkn, mod }
4. Handle results (send to database: insert, update, etc.)

'''

import math, sys, string, random, subprocess, serial #, pty
from time import gmtime, strftime, clock	# for timestamping packets
import hashlib #for checksum purposes

sys.path.append('/usr/lib/python2.7/dist-packages')

################################################################################
### 0. Configure the port on our machine using kermit
################################################################################

port_ttyUSB0 = serial.Serial(port='/dev/ttyUSB0', baudrate=38400)
port_ttyUSB1 = serial.Serial(port='/dev/ttyUSB1', baudrate=38400)

port_ttyUSB0.write("+++A")
port_ttyUSB1.write("+++A")

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

# at the end of the for loop, go thru this list and insert elements into the results table
resultsList = []

#time interval between packets
spl = 10

################################################################################
### 2. Set up experiment logfile
################################################################################

# TODO: may want to remove logging when debugging is complete, or allow it to be toggled
rptt = 5 # number of times to repeat experiment
psn = 1 # delay (sleep time), may not need to use

rtc = strftime("%y%m%d%H%M", gmtime())
logn = 'T{0}.LOG'.format(rtc)
print 'Start test: {0}'.format(rtc)

################################################################################
### 3. Run the experiment on each combination of { pwr, bkn, mod }
################################################################################

# record results in variable (resultsList)

for (id, mpwr, lpwr, ppwr, mbkn, lbkn, pbkn, mmod, lmod, pmod, testData) in cursor:
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

      data_size = testData.length()
      n_packets = int(math.ceil(float(data_size)/packet_length))
  
      for transmission_power in range(lpwr, mpwr + 1, ppwr):

        print '### TXPRW changed to {0}\n'.format(transmission_power)
        port_ttyUSB0.write("$HHCRW,TXPWR,{0}\r\n".format(transmission_power))

        for trial in range(rptt): # repeat the experiment!

          print 'sending data now'

          # keep track of packet loss
          n_loss = 0
          start_time = clock() 

          #####################################################
          # TODO: transmit data here
          
          # send each packet
          for i in range(n_packets):
            if i == n_packets - 1:
              packet_to_send = testData[i*packet_length:]
            else:
              packet_to_send = testData[i*packet_length:(i+1)*packet_length]

            # TODO: implement checksum
            port_ttyUSB0.write("$HHTXA,0,0,0,{0}\r\n".format(packet_to_send))
            read_buffer = port_ttyUSB1.readline();

            if read_buffer != packet_to_send:
              n_loss += 1


          # TODO: keep track of loss, number of retransmissions, etc.

          #####################################################

          execution_time = clock() - start_time

          # TODO: store the results of the above experiment in some variable for later use
 
          print "Elapsed time: {} seconds".format(execution_time)
        print # empty line

################################################################################
### 4. Handle results
################################################################################

# TODO: insert results into the results table
# TODO: record exit status, which will determine if we need to rerun the experiments, require manual intervention, or are ready to be emailed to client

cursor.close()
cnx.close()
exit(0)

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

