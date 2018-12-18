'''Decomposed Model'''
import sys
from columnGeneration import *
import datetime
import time
import csv
import os
times = {}
dateStamp = str(datetime.datetime.now())[:16].replace(':', '-')

'''Setup'''
instance = 'shortSimple' # instance name (without number)
numInstances = 1 # number of instances

'''Run'''
dirName = '../../data/solutions/'+instance # Directory name
if not os.path.exists(dirName): # Create dir if does not exist
    os.mkdir('../../data/solutions/'+instance)
filename = dirName + ' decomposed model ' + dateStamp + '.csv' # Set file name
file = open(filename, 'w') # Open file for writing
writer = csv.writer(file, delimiter = ',') # Prepare CSV formatting
writer.writerow(['Instance', 'Lower bound', 'Upper bound', 'Total time']) # Write header
file.close() # Save file
for run in range(1, numInstances+1): # Iterate over instances
    L, U, totalTime, numIterations, timeInSPPRC, timeInRMP, timeInMP = columnGeneration(instance=instance, dateStamp=dateStamp, run=run) # Solve CG with instance
    file = open(filename, 'a') # Open file
    writer = csv.writer(file, delimiter = ',') # Prepare CSV formatting
    writer.writerow([instance+'_'+str(run), L, U, totalTime]) # Append results to file
    file.close() # File handling
