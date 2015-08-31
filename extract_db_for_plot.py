import json, math, sys, string, random, subprocess, serial
from time import gmtime, strftime, clock, time  # for timestamping packets
import time
import hashlib #for checksum purposes
import mysql.connector # mysql database
import getpass

sys.path.append('/usr/lib/python2.7/dist-packages')

cnx = mysql.connector.connect(user= getpass.getuser(), password='pass', host='localhost', database='UWNet')

cursor = cnx.cursor()
cursor_insert = cnx.cursor()

data = {}

for exp in [6,7,8,9,10,11,12,13,14,15]:

  query = ("SELECT parameters, results FROM Results WHERE experimentID = {}".format(exp))
  cursor.execute(query)

  # create a list of all the points

  bkns = []
  mods = []
  delays = []

  for (parameters, results) in cursor:
    bkns.append(json.loads(parameters)['bkn'])
    mods.append(json.loads(parameters)['mod'])
    delays.append(json.loads(results)['0']['delay'])

  data[exp] = { 'bkns': bkns, 'mods': mods, "delays": delays }

# to extract data points for each plot:
# example: plot data for experiment 6

plot_data = data[6]
bkn_vals = plot_data['bkns']
mod_vals = plot_data['mods']
delay_vals = plot_data['delays']

print plot_data
print
print bkn_vals
print
print mod_vals
print
print delay_vals
