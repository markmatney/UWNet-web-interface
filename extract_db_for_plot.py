import json, math, sys, string, random, subprocess, serial
from time import gmtime, strftime, clock, time  # for timestamping packets
import time
import hashlib #for checksum purposes
import mysql.connector # mysql database
import getpass
from matplotlib import pyplot
import pylab
from mpl_toolkits.mplot3d import Axes3D
import random
import numpy as np
import matplotlib.pyplot as plt

sys.path.append('/usr/lib/python2.7/dist-packages')

cnx = mysql.connector.connect(user= 'root', password='sylmar123', host='localhost', database='UWNet')

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

plot_data = data[11]
bkn_vals = plot_data['bkns']
mod_vals = plot_data['mods']
delay_vals = plot_data['delays']

fig = plt.figure()
#ax2 = Axes3D(fig)
ax = fig.add_subplot(111, projection ='3d')
#X, Y = np.meshgrid(bkn_vals, mod_vals)
ax.plot_contourf(bkn_vals, mod_vals, delay_vals)
#ax2.view_init(28, -144) 
plt.show()
#ax.plot_wireframe(bkn_vals, mod_vals, delay_vals, rstride =1, cstride =1)
#ax.axis
#pyplot.show()
#fig = plt.figure()
