import mysql.connector
import math
import matplotlib.pyplot as plt
import numpy as np
import numpy.fft as fft
from pylab import *
import csv
import json
db = mysql.connector.connect(user = 'root', password = 'sylmar123', host = 'localhost', database = 'UWNet')
cursor = db.cursor()

cursor.execute("SELECT * FROM Results")

data  = cursor.fetchall()

#numrows = int(cursor.rowcount)
#i = 0

file = open ('/home/eseguraca6/cslab/UWNet-web-interface/data.txt', 'w')

f_1 = open("data.txt", "w")
f_2 = open("raw_data.txt", "w")

for row in data:
	print >> f_1, row

f_1.close()
x = json.loads('data.txt')
f = open('data.csv')
for item in data:
	f.writerow(item)
f.close
