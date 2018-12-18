'''Script to run MIP model'''
import sys
import functionsMIP as mip
import datetime
import time
import csv
import os
times = {}
dateStamp = str(datetime.datetime.now())[:16].replace(':', '-')

'''Setup'''
mipSolverFile = "rosterlineMIP_win64.exe" # Self-executable Mosel Xpress file
instance = "shortSimple" # Instance name (excluding number)
numInstances = 1 # Number of instances
mipSolutionFile = 'solution.txt' # Temporary file
waitFrequency = 1e-10000 # Small float
timePrint = False # Print output in command prompt while running

if timePrint:
    os.system('cls')
    print('\n\t\t\t\t\tMIP\n'+'_'*79+'\n')

dirName = '../../data/solutions/'+instance # Directory name
if not os.path.exists(dirName):
    os.mkdir('../../data/solutions/'+instance) # Make instance directory

filename = dirName + ' mip model ' + dateStamp + '.csv' # Results file name
file = open(filename, 'w') # Open file for writing
writer = csv.writer(file, delimiter = ',') # Prepare CSV format
writer.writerow(['Instance', 'Objective value', 'Total time']) # Write header
file.close() # Save file
for run in range(1, numInstances+1): # Iterate over instances
    times['Start'] = time.time() # File handling
    instanceFile = instance+'_'+str(run)+'.txt' # File handling
    solutionFile = dirName + '/mip model ' + dateStamp  + '_'+str(run)+'.csv' # File handling
    if timePrint:
        print('\nProcess\t\t\t'+
        '\t\t   Diff\t     Total\tObjective value\n'+'_'*79)
    data = mip.dataLoader(filename = '../../data/instances/'+instance+'/'+instanceFile) # Load data
    start = time.time()
    os.rename('../../data/instances/'+instance+'/'+instanceFile, './instanceFile.txt') # File handling
    os.startfile(mipSolverFile) # Solve MIP
    while not (os.path.exists(mipSolutionFile)):
        time.sleep(waitFrequency) # Wait for RMP solution
    times['Total'] = time.time() - start
    os.rename('./instanceFile.txt', '../../data/instances/'+instance+'/'+instanceFile) # File handling
    solution, objective = mip.readMoselSolution(mipSolutionFile) #Read from mosel text file output
    os.remove(mipSolutionFile) # File handling
    solutionTransform = mip.solutionTransform(solution, data) # Transform solution to wanted format
    if timePrint:
        print('\nMIP solved\t\t\t\t{:>6.2f}s\t   {:>6.2f}s\t\t{:>7.0f}'.format(times['Total'], time.time() - times['Start'], objective))
    if timePrint:
        mip.printSolution(solutionTransform, data)

    '''Write to file (run specific)'''
    mip.solutionWriter(instanceFile=instanceFile, solutionFile=solutionFile,
    times=times, solution=solutionTransform, objective=objective, data=data)

    '''Write to file (instance aggregated)'''
    file = open(filename, 'a')
    writer = csv.writer(file, delimiter = ',')
    writer.writerow([instance+'_'+str(run), objective, times['Total']])
    file.close()
