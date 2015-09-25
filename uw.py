import json, math, sys, string, random, subprocess, serial
from time import localtime, strftime, clock, time	# for timestamping packets
import time
import hashlib #for checksum purposes
import mysql.connector # mysql database
import getpass

sys.path.append('/usr/lib/python2.7/dist-packages')

################################################################################
### Auxiliary functions
################################################################################

### Returns the hex value of the xor of all characters in a string.
def xor_string_hash(string):
  ret = 0
  for char in string:
    ret ^= ord(char)
  return hex(ret)[2:] ### return everything but the first two characters, "0x"

### Formats numbers with suffix e.g.: ord(1) -> "1st", ord(2) -> "2nd"
def ord(n):
    return str(n)+("th" if 4<=n%100<=20 else {1:"st",2:"nd",3:"rd"}.get(n%10, "th"))

################################################################################
### 0. Logfile Setup
################################################################################

### TODO: may want to remove logging when debugging is complete, or allow it to be toggled
logfile_name = 'logs/UWNet-{0}.LOG'.format(strftime("20%y-%m-%d--%H:%M:%S", localtime()))
logfile = open(logfile_name, 'w')

################################################################################
### 1. Port configuration
################################################################################

### Setup the port to be read from ( /dev/ttyUSB0 ) with timeout to enable
### recovery from packet loss.

port_ttyUSB0 = serial.Serial(port='/dev/ttyUSB0', baudrate=38400)
port_ttyUSB1 = serial.Serial(port='/dev/ttyUSB1', baudrate=38400, timeout=50)

### For each port, enter command mode (+++A) and enable checksum ($HHCRW,MMCHK,1),
### then check for success.

port_ttyUSB0.write("+++A\r\n")
if ("MMOKY" not in port_ttyUSB0.readline()):
  logfile.write('CRITICAL ERROR: cannot enter command mode for ttyUSB0 ... exiting')
  exit(0) ### TODO: do something better upon failure, maybe try to fix!

### TODO: set MMCHK to 1 if want checksum
'''
port_ttyUSB0.write("$HHCRW,MMCHK,0\r\n")
if ("MMOKY" not in port_ttyUSB0.readline()):
  logfile.write('error in setting the checksum register for ttyUSB0')
  exit(0)
'''

port_ttyUSB1.write("+++A\r\n")
if ("MMOKY" not in port_ttyUSB1.readline()):
  logfile.write('CRITICAL ERROR: cannot enter command mode for ttyUSB1 ... exiting')
  exit(0)

'''
port_ttyUSB1.write("$HHCRW,MMCHK,0\r\n")
if ("MMOKY" not in port_ttyUSB1.readline()):
  logfile.write('error in setting the checksum register for ttyUSB1')
  exit(0)
'''

################################################################################
### 2. Retrieve experiments
################################################################################

### Resources:
###   http://dev.mysql.com/doc/refman/5.5/en/index.html
###   https://docs.python.org/2/howto/webservers.html?highlight=mysql
###   http://dev.mysql.com/doc/connector-python/en/connector-python-example-cursor-select.html

### Connect to the database.

cnx = mysql.connector.connect(user= getpass.getuser(), password='pass', host='localhost', database='UWNet')

### TODO: may need to change parameters for mysql.connector.connect() depending on
### which machine we are using.

### TODO: create a standard user for the database; include script in create.sql

### getpass library extracts information regarding the machine's user name. issue though is with password. Does it have to always be hardwired is there another way?

cursor = cnx.cursor()
cursor_insert = cnx.cursor()

### Retrieve rows from InputQueue table for experiments which have not been run

retrieve_experiments = ("SELECT id, mpwr, lpwr, ppwr, mbkn, lbkn, pbkn, mmod, lmod, pmod, rptt, testData FROM InputQueue WHERE exitStatus IS NULL")
cursor.execute(retrieve_experiments)

### Store each row in a dictionary.

selected_rows = {}
for (id, mpwr, lpwr, ppwr, mbkn, lbkn, pbkn, mmod, lmod, pmod, rptt, testData) in cursor:
  selected_rows[id] = { 'mpwr': mpwr, 'lpwr': lpwr, 'ppwr': ppwr, 'mbkn': mbkn, 'lbkn': lbkn, 'pbkn': pbkn, 'mmod': mmod, 'lmod': lmod, 'pmod': pmod, 'rptt': rptt, 'testData': testData }

### Collect results from each trial in this dictionary for insertion into Results
### table. The keys correspond to the 'id' column in the InputQueue table. 

allResults = {}

################################################################################
### 3. Run each experiment on each combination of { pwr, bkn, mod }, rptt times
################################################################################

### handle each enqueued experiment

### TODO: report errors, store in database
### code NULL: exited normally
### code NOT NULL: error
###  - KE: kermit configuration
###  - DB: database access
###  - PT: port configuration
###  - etc...
### TODO: Devise error code scheme, or decide that it is unnecessary...

for id in selected_rows:

  row = selected_rows[id]

  logfile.write('===== STARTING EXPERIMENT {0} =====\n\n'.format(id))
  print '===== STARTING EXPERIMENT {0} =====\n'.format(id)

  ### Each element of the following list will be its own row in Results.
  ### All elements in this list will have the same experimentID.
  resultsList = []

  for transmission_mode in range(row['lmod'], row['mmod'] + 1, row['pmod']):

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
        logfile.write('ERROR: Transmit mode of {0} invalid; ranges from 1 to 5 ... skipping\n'.format(transmission_mode))
        continue

    logfile.write('-> transmission_mode := {0}\n'.format(transmission_mode))
    print '-> transmission_mode := {0}'.format(transmission_mode)

    for blocks_per_packet in range(row['lbkn'], row['mbkn'] + 1, row['pbkn']):
 
      logfile.write('-> blocks_per_packet := {0}\n'.format(blocks_per_packet))
      print '-> blocks_per_packet := {0}'.format(blocks_per_packet)

      packet_length = bytes_per_block * blocks_per_packet

      for transmission_power in range(row['lpwr'], row['mpwr'] + 1, row['ppwr']):

        logfile.write('-> transmission_power := {0}\n'.format(transmission_power))
        print '-> transmission_power := {0}'.format(transmission_power)

        port_ttyUSB0.write("$HHCRW,TXPWR,{0}\r\n".format(transmission_power))

        logfile.write('-> TXPWR := transmission_power\n\n')
        print '-> TXPWR := transmission_power\n'

        ### Collect data for each trial in a dictionary, keyed by trial number.

        collectionOfTrials = {}

        for trial in range(row['rptt']): ### repeat the experiment!

          logfile.write('\tTrial {0}\n\n'.format(trial))
          print '\tTrial {0}\n'.format(trial)

          ### Keep track of packet loss, retransmissions, and execution time.

          n_loss = 0
          n_retx = 0
          start_time = time.time() 

          ### Transmit file across network.
          
          ### Get file handle for the filepath indicated by testData

          with open(str(row['testData']), 'r') as read_file:

            packet_to_send = read_file.read(packet_length)
            packet_counter = 0

            # while there is still data to send
            while '' != packet_to_send:

              packet_to_send_hex = packet_to_send.encode("hex")

              packet_counter += 1

              logfile.write('\tSending packet {0}{1} ({2} bytes) ... '.format(packet_counter, ord(packet_counter), len(packet_to_send)))
              print '\tSending packet {0}{1} ({2} bytes) ... '.format(packet_counter, ord(packet_counter), len(packet_to_send))

              ### TODO: enable toggling of send mode: either in command mode, or data mode
              
              ### Write hex-encoded data to the write port, /dev/ttyUSB0.

              max_len = 2500

              ### TODO: see if we can use packet_to_send instead:
              if len(packet_to_send_hex) <= max_len:
                port_ttyUSB0.write("$HHTXD,0,{0},0,{1}\r\n".format(transmission_mode, packet_to_send_hex))
              else:
                offset = 0
                bytes_left = len(packet_to_send_hex)
                while (bytes_left > max_len):
                  port_ttyUSB0.write("$HHTXD,{0}\r\n".format(packet_to_send_hex[offset:offset + max_len]))
                  bytes_left -= max_len
                  offset += max_len
                port_ttyUSB0.write("$HHTXD,0,{0},0,{1}\r\n".format(transmission_mode, packet_to_send_hex[offset:]))
                  
              ### Check if packet was transmitted, then
              ### extract the data segment from the $MMRXD command.

              read_buffer = port_ttyUSB1.readline()

	      if len(read_buffer) == 0: # TODO: replace with timeout check
                n_loss += 1
                logfile.write("packet lost\n")
                print "\t\tpacket lost"
              else:

                ### will hold the data extracted from the read buffer
                read_data = ''

                if "$MMRXA," in read_buffer:

                  ### if receive data in ASCII format, no need to call string.decode("hex")
                  ### 11 to shave off "$MMRXD,#,0,", -2 to account for \r\n

                  read_data = read_buffer[11:len(read_buffer)-2]
                  logfile.write("{0} bytes transferred successfully\n".format(len(read_data)))
                  print "\t\t{0} bytes transferred successfully".format(len(read_data))

                  ### Uncomment the following code block to use checksums
                  ### * Unnecessary at this point since the process running this script
                  ### * still has access to the data via program variables!

                  '''
                  checksum_sent = xor_string_hash(packet_to_send)
                  checksum_received = xor_string_hash(read_data)
                  if checksum_sent == checksum_received:
                    print("Correct File Transmission")
                  else:
                    print("Checksum indicated incorrect transmission.")
                  '''

                  if (read_data != packet_to_send):
                    logfile.write("\t\tCorruption detected!\n")
                    print "\t\t*** Corruption detected!"

                elif "$MMRXD," in read_buffer:

                  ### if receive data in HEX format, call string.decode("hex")
                  ### 11 to shave off "$MMRXD,#,0,", -2 to account for \r\n

                  read_data = read_buffer[11:len(read_buffer)-2].decode("hex")
                  logfile.write("{0} bytes transferred\n".format(len(read_data)))
                  print "\t\t{0} bytes transferred".format(len(read_data))

                  ### Uncomment the following code block to use checksums
                  ### * Unnecessary at this point since the process running this script
                  ### * still has access to the data via program variables!

                  '''
                  checksum_sent = xor_string_hash(packet_to_send)
                  checksum_received = xor_string_hash(read_data)
                  if checksum_sent == checksum_received:
                    print("Correct File Transmission")
                  else:
                    print("Checksum indicated incorrect transmission.")
                  '''

                  if (read_data != packet_to_send):
                    logfile.write("\t\tCorruption detected!\n")
                    print "\t\t*** Corruption detected!"

                else:
                  n_loss += 1
                  logfile.write("packet #{0} lost\n".format(packet_counter))
                  print "\t\tpacket #{0} lost".format(packet_counter)

              packet_to_send = read_file.read(packet_length)

          ### Report execution time, and add it with the other results to the list.

          file_transmission_time = time.time() - start_time
          collectionOfTrials[trial] = { "delay": file_transmission_time, "loss": n_loss, "retx": n_retx }
          logfile.write("\n\tdelay:\t{0} seconds\n\tloss:\t{1}\n\tretx:\t{2}\n".format(file_transmission_time, n_loss, n_retx))
          print "\n\tdelay:\t{0} seconds\n\tloss:\t{1}\n\tretx:\t{2}".format(file_transmission_time, n_loss, n_retx)

        ### Insert row into DB

        add_row = ('INSERT INTO Results VALUES({0}, \'{1}\', \'{2}\')'.format(id, json.dumps({ "pwr": transmission_power, "bkn": blocks_per_packet, "mod": transmission_mode }), json.dumps(collectionOfTrials)))
        cursor.execute(add_row)
        cnx.commit()

        logfile.write('\n')
        print '\n'

  ### Update exitStatus in InputQueue.
  ### TODO: change this from hard-coded exit status to variable

  update_exitStatus = ('UPDATE InputQueue SET exitStatus = 0, dateCompleted = \'{0}\' WHERE id = {1}'.format(time.strftime('%Y-%m-%d %H:%M:%S'), id))
  cursor.execute(update_exitStatus)
  cnx.commit()

  print "Experiment {0} done!".format(id)
  logfile.write("Experiment {0} done!\n\n".format(id))

################################################################################
### 4. Cleanup
################################################################################

cursor.close()
cnx.close()
logfile.close()

exit(0)
