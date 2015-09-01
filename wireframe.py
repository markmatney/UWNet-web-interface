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
from scipy.interpolate import griddata

sys.path.append('/usr/lib/python2.7/dist-packages')

cnx = mysql.connector.connect(user='mark', password='pass', host='localhost', database='UWNet')

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


plot_data = data[15]
bkn_vals = range(1, 16 + 1)
mod_vals = range(1, 5 + 1)
delay_vals = plot_data['delays']

X, Y = np.meshgrid(bkn_vals, mod_vals)
Z = np.asarray([np.asarray(delay_vals[0:16]), np.asarray(delay_vals[16:32]), np.asarray(delay_vals[32:48]), np.asarray(delay_vals[48:64]), np.asarray(delay_vals[64:80])])

fig = plt.figure()
ax = fig.add_subplot(111, projection ='3d')
ax.plot_wireframe(X, Y, Z)
plt.show()