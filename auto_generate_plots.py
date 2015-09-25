'''
auto_generate_plots/py

This script generates plots for experimental result data that has not yet
been plotted.

This script uses the matplotlib plotting library, and the mplot3d toolkit,
for generating data plots:

http://matplotlib.org/mpl_toolkits/mplot3d/tutorial.html

TODO: Turn this script to face the web more. Enable interactive use so users can
choose viewing angle, axes labels, title, zoom, projection, etc.
'''

import json, sys, mysql.connector
from matplotlib import pyplot
import pylab
from mpl_toolkits.mplot3d import Axes3D, proj3d
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

'''
orthogonal_proj(zfront, zback)

Transform 3D plots from perspective to orthogonal projection.
But, it breaks automatic axes repositioning! TODO: fix
'''
def orthogonal_proj(zfront, zback):
    a = (zfront+zback)/(zfront-zback)
    b = -2*(zfront*zback)/(zfront-zback)
    return np.array([[1,0,0,0],
                        [0,1,0,0],
                        [0,0,a,b],
                        [0,0,0,zback]])

'''
TODO: the following line breaks automatic axes repositioning!
Fix, then uncomment the following line
'''
# proj3d.persp_transformation = orthogonal_proj

### booleans to determine which plots to generate
scatter = False
wireframe = True

### remove the following line, Mark's system is messed up and required this
sys.path.append('/usr/lib/python2.7/dist-packages')

'''
TODO: change the call to connect()
Pass variables that contain local db login info
'''
cnx = mysql.connector.connect(user='mark', password='pass', host='localhost', database='UWNet')
cursor = cnx.cursor()

data = {}

### find the experiments for which plots still need to be generated
getUnplottedExpIds = ("SELECT id, testData FROM InputQueue WHERE plotsGenerated = FALSE")
cursor.execute(getUnplottedExpIds)

fileSizes = {}

### TODO: do the following two for-loops in one for-loop

### collect file sizes in dictionary keyed by experiment id
for (id, testData) in cursor: 
  ### TODO: calculate file size
  fileSize = 1
  fileSizes[id] = fileSize

  filePath = fileSizes[id]

'''
TODO: fix the following for-loop
Right now it assumes that the user submitted form with:
	mpwr	10
	lpwr	10
	ppwr	10
	mmod	5
	lmod	1
	pmod	1
	mbkn	16
	lbkn	1
	pbkn	1
	rptt	1

Fix to allow arbitrary input
'''

### for each experiment, generate plots and save to files
for key in fileSizes:

  id = int(key)

  getResults = ("SELECT parameters, results FROM Results WHERE experimentID = {}".format(id))
  cursor.execute(getResults)

  ### create a list of all the points
  bkns = []
  mods = []
  delays = []

  ### collect bkns, mods, and delays
  for (parameters, results) in cursor:
    bkns.append(json.loads(parameters)['bkn'])
    mods.append(json.loads(parameters)['mod'])
    delays.append(json.loads(results)['0']['delay'])

  plot_data = { 'bkns': bkns, 'mods': mods, 'delays': delays }

  ### change the following two lines when the user can submit arbitrary parameters
  bkn_vals = range(1, 16 + 1) ### change
  mod_vals = range(1, 5 + 1) ### change

  delay_vals = plot_data['delays']

  X, Y = np.meshgrid(bkn_vals, mod_vals)

  ### change the following lines when the user can submit arbitrary parameters
  Z = np.asarray([np.asarray(delay_vals[0:16]), np.asarray(delay_vals[16:32]), np.asarray(delay_vals[32:48]), np.asarray(delay_vals[48:64]), np.asarray(delay_vals[64:80])]) ### change
  
  ### now create the plots

  el = 15 ### elevation of the viewing camera for plots

  ### scatter plot
  
  if scatter == True:
    fig = plt.figure()
    ax = fig.add_subplot(111, projection ='3d')
    ax.scatter(plot_data['bkns'], plot_data['mods'], delay_vals)
    ax.set_title('{} file transmission'.format(fileSizes[id]))
    ax.set_xlabel('blocks per packet')
    ax.set_ylabel('transmission mode')
    ax.set_zlabel('file transmission delay (s)')
    plt.xticks(np.arange(min(bkn_vals), max(bkn_vals) + 1, 1))
    plt.yticks(np.arange(min(mod_vals), max(mod_vals) + 1, 1))
    ax.view_init(elev=el, azim=45)
    plt.savefig("plots/exp{0}_scat_elev{1}degrees.png".format(id, el))

    ### use plt.show() for the interactive version of this script, see top TODO
    # plt.show()
  
  ### wireframe plot
  if wireframe == True:
    fig = plt.figure()
    ax = fig.add_subplot(111, projection ='3d')
    ax.plot_wireframe(X, Y, Z)
    ax.set_title('{} file transmission'.format(fileSizes[id]))
    ax.set_xlabel('blocks per packet')
    ax.set_ylabel('transmission mode')
    ax.set_zlabel('file transmission delay (s)')
    plt.xticks(np.arange(min(bkn_vals), max(bkn_vals) + 1, 1))
    plt.yticks(np.arange(min(mod_vals), max(mod_vals) + 1, 1))
    ax.view_init(elev=el, azim=45)
    plt.savefig("plots/exp{0}_wire_elev{1}degrees.png".format(id, el))

  ### update InputQueue to notify that plots were generated

  plots_generated = ("UPDATE InputQueue SET plotsGenerated = 1 WHERE id = {0}".format(id))
  cursor.execute(plots_generated)
  cnx.commit()

cursor.close()
cnx.close()
