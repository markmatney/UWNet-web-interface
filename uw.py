import json, math, sys, string, random, subprocess, serial
from time import gmtime, strftime, clock, time	# for timestamping packets
import time
import hashlib #for checksum purposes
import mysql.connector # mysql database

sys.path.append('/usr/lib/python2.7/dist-packages')

################################################################################
### Auxiliary functions
################################################################################

# TODO: do we even need this function? might as well keep it for now
# check number of args (arity check)
# check argument format
# ensure datetime is 10 digits
# ensure power is in [-127,0]
# ensure txmode is in [1,5]
# based on value of txmode, check that pktlen is correct
# ensure pktnum is in [0,9999]
# just do this error checking before passing it to the backend???

# Returns string representing the packet containing a timestamp, power level,
# transmission mode, packet length, and id number.
def subpkt(rtc, pwr, mod, plt, psn):
  data = ''.join(random.choice(string.ascii_uppercase) for i in range(plt - 38))
  return 'PTD{0}PRW{1}TMD{2}PLT{3}PSN{4}@{5}'.format(str(rtc), str(pwr).zfill(3), str(mod), str(plt).zfill(4), str(psn).zfill(4), data)


# Returns the hex value of the xor of all characters in a string.
def xor_string_hash(string):
  ret = 0
  for char in string:
    ret ^= ord(char)
  return hex(ret)[2:] # return everything but the first two characters, "0x"

################################################################################
### 0. Port configuration
################################################################################

# Setup the port to be read from ( /dev/ttyUSB0 ) with timeout to enable
# recovery from packet loss.

port_ttyUSB0 = serial.Serial(port='/dev/ttyUSB0', baudrate=38400)
port_ttyUSB1 = serial.Serial(port='/dev/ttyUSB1', baudrate=38400, timeout=5)

# For each port, enter command mode (+++A) and enable checksum ($HHCRW,MMCHK,1),
# then check for success.

port_ttyUSB0.write("+++A\r\n")
if ("MMOKY" not in port_ttyUSB0.readline()):
  print 'error in entering command mode for ttyUSB0'
  exit(0) # TODO: do something better upon failure


                               # TODO: set to 1 if want checksum
port_ttyUSB0.write("$HHCRW,MMCHK,0\r\n")
if ("MMOKY" not in port_ttyUSB0.readline()):
  print 'error in setting the checksum register for ttyUSB0'
  exit(0)

port_ttyUSB1.write("+++A\r\n")
if ("MMOKY" not in port_ttyUSB1.readline()):
  print 'error in entering command mode for ttyUSB1'
  exit(0)

port_ttyUSB1.write("$HHCRW,MMCHK,0\r\n")
if ("MMOKY" not in port_ttyUSB1.readline()):
  print 'error in setting the checksum register for ttyUSB1'
  exit(0)

################################################################################
### 1. Retrieve experiments
################################################################################

# Resources:
#   http://dev.mysql.com/doc/refman/5.5/en/index.html
#   https://docs.python.org/2/howto/webservers.html?highlight=mysql
#   http://dev.mysql.com/doc/connector-python/en/connector-python-example-cursor-select.html

# Connect to the database.

cnx = mysql.connector.connect(user='mark', password='pass', host='localhost', database='UWNet')
# TODO: may need to change parameters for mysql.connector.connect() depending on
# which machine we are using.

cursor = cnx.cursor()

# Retrieve rows from InputQueue table for experiments which have not been run

query = ("SELECT id, mpwr, lpwr, ppwr, mbkn, lbkn, pbkn, mmod, lmod, pmod, rptt, testData FROM InputQueue WHERE exitStatus IS NULL")
cursor.execute(query)

# Collect results from each trial in this dictionary for insertion into Results
# table. The keys correspond to the 'id' column in the InputQueue table. 

allResults = {}

################################################################################
### 2. TODO: Logfile Setup
################################################################################

# TODO: may want to remove logging when debugging is complete, or allow it to be toggled
rtc = strftime("%y%m%d%H%M", gmtime())
logn = 'T{0}.LOG'.format(rtc)
print 'Start test: {0}'.format(rtc)

################################################################################
### 3. Run each experiment on each combination of { pwr, bkn, mod }, rptt times
################################################################################

# handle each enqueued experiment
# report errors, store in database
# code NULL: exited normally
# code NOT NULL: error
#  - KE: kermit configuration
#  - DB: database access
#  - PT: port configuration
#  - etc...
# TODO: Devise error code scheme

for (id, mpwr, lpwr, ppwr, mbkn, lbkn, pbkn, mmod, lmod, pmod, rptt, testData) in cursor:

  # Each element of the following list will be its own row in Results.
  # All elements in this list will have the same experimentID.
  resultsList = []

  for transmission_mode in range(lmod, mmod + 1, pmod):

    ## print '### Sending in Mode {0}'.format(transmission_mode)
    # TODO: Should this be logged instead of printed?

    if transmission_mode == 1:
        bytes_per_block = 38
    elif transmission_mode == 2:
        bytes_per_block = 80
    elif transmission_mode == 3:
        bytes_per_block = 122
    elif transmission_mode == 4:
        bytes_per_block = 164
    elif transmission_mode == 5:
        bytes_per_block = 248
    else:
        print("ERROR:Transmit mode ranges from 1 to 5")
        exit(0) # TODO: handle this better

    for blocks_per_packet in range(lbkn, mbkn + 1, pbkn):
 
      ## print '### Sending {0} blocks per packet'.format(blocks_per_packet)

      packet_length = bytes_per_block * blocks_per_packet

      for transmission_power in range(lpwr, mpwr + 1, ppwr):

        ## print '### TXPWR changed to {0}\n'.format(transmission_power)

        port_ttyUSB0.write("$HHCRW,TXPWR,{0}\r\n".format(transmission_power))

        # Collect data for each trial in a dictionary, keyed by trial number.

        collectionOfTrials = {}

        for trial in range(rptt): # repeat the experiment!

          print 'sending data now'

          # Keep track of packet loss, retransmissions, and execution time.

          n_loss = 0
          n_retx = 0
          start_time = time.time() 

          # Transmit file across network.
          
          # Get file handle for the filepath indicated by testData

          with open(str(testData), 'r') as read_file:

            packet_to_send = read_file.read(packet_length)

            while '' != packet_to_send:

              ## print "Length of packet to send: {}".format(len(packet_to_send))
              ## print packet_to_send

              # TODO: enable toggling of send mode: either in command mode, or data mode
              # TODO: implement checksum

              # Write hex-encoded data to the write port, /dev/ttyUSB0.

              port_ttyUSB0.write("$HHTXD,0,{0},0,{1}\r\n".format(transmission_mode, packet_to_send.encode("hex")))

              # Read from the read port, /dev/ttyUSB1.

              read_buffer = port_ttyUSB1.readline();
              ## print "read buf: {0}".format(read_buffer)

              # Check if packet was transmitted, then
              # extract the data segment from the $MMRXD command.

	      if len(read_buffer) == 0: # TODO: replace with timeout check
                n_loss += 1
              else:
                read_data = ''
                if "$MMRXD," in read_buffer:
                  read_data = read_buffer[11:len(read_buffer)-2] # account for \r\n
                  print "Bytes transferred: {0}".format(len(read_data))
                  print read_data.decode("hex") == packet_to_send # if false, retransmit
                else:
                  n_loss += 1

              # If read_data == '', there is a problem.

              # TODO: extract data from read_buffer
              packet_to_send = read_file.read(packet_length)

          # Report execution time, and add it with the other results to the list.

          execution_time = time.time() - start_time
          collectionOfTrials[trial] = { "delay": execution_time, "loss": n_loss, "retx": n_retx }
          ## print "Elapsed time: {} seconds".format(execution_time)

        ## print

        # Add the trial collection to resultsList.

        resultsList.append( { 'parameters': { 'pwr': transmission_power, 'bkn': blocks_per_packet, 'mod': transmission_mode }, 'results': collectionOfTrials } )

  allResults[id] = resultsList

################################################################################
### 4. Handle results
################################################################################


for experimentID in allResults:
  for param_combo in allResults[experimentID]:

    # Insert results into the Results table.

    add_row = ('INSERT INTO Results VALUES({0}, \'{1}\', \'{2}\')'.format(experimentID, json.dumps(param_combo["parameters"]), json.dumps(param_combo["results"])))
    cursor.execute(add_row)
    cnx.commit()

    # Update exitStatus in InputQueue.

    update_exitStatus = ('UPDATE InputQueue SET exitStatus = 0 WHERE id = {0}'.format(experimentID))
    cursor.execute(update_exitStatus)
    cnx.commit()

# TODO: CORRECTLY record exit status, which will determine if we need to rerun the experiments, require manual intervention, or are ready to be emailed to client

cursor.close()
cnx.close()
exit(0)
