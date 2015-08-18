'''
STEPS:

0. Configure the port on our machine using kermit
1. Query database for experiments that are ready to run
2. Set up experiment logfile
3. Run the experiment on each combination of { pwr, bkn, mod }
4. Handle results (send to database: insert, update, etc.)

'''

import sys, string, random, subprocess #, pty, serial
from time import gmtime, strftime, clock	# for timestamping packets

sys.path.append('/usr/lib/python2.7/dist-packages')

################################################################################
### 0. Configure the port on our machine using kermit
################################################################################

p_kermit_0 = subprocess.call(["kermit", "CFG_AQUASENT_KERMIT_38400" ,"-c", "-C", "+++A, $HHCRW, $TXPWR,10"])#script interacts with kermit

# TODO: why set p_kermit_1 = p_kermit_0 ?
p_kermit_1 = subprocess.call(["kermit", "CFG_AQUASENT_KERMIT_38400_USB1" ,"-c", "-C", "+++A, $HHCRW, $TXPWR,10"])
# TODO: need to figure out how to make sure I can send 'c' command to kermit to make sure it is online

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
      # check if block number is in [1,16]
  
  
      # COMPOUND IF STATEMENT HERE, checks packet length
  
      for transmission_power in range(lpwr, mpwr + 1, ppwr):
        # change transmit level
        print '### TXPRW changed to {0}\n'.format(transmission_power)

        for trial in range(rptt): # repeat the experiment!
          # Packetize testData
  
          print 'sending data now'

          start_time = clock() 

          #####################################################
          # TODO: transmit data here
          # keep track of loss, number of retransmissions, etc.
          #####################################################

          execution_time = clock() - start_time
 
          print "Elapsed time: {} seconds".format(execution_time)
        print
  
 
  # sleep for spl seconds, maybe in order for it to work?

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

