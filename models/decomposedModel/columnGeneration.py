'''Column generation algorithm'''
import sys
sys.path.append('./program/subProblem')
import functionsCG as cg
import functionsSPPRC as spprc
from solveSPPRC import *
from classes import *
import datetime
import time
import copy
import os

def columnGeneration(instance: str, dateStamp: str, run: int, maxTime: int = 100000):
    '''Delete previous dictionaries'''
    try:
        del times
    except:
        pass
    try:
        del masterSolutions
    except:
        pass
    try:
        del masterObjectives
    except:
        pass
    try:
        del reducedCosts
    except:
        pass
    try:
        del columnCount
    except:
        pass
    try:
        del intSolutions
    except:
        pass
    try:
        del heuristicColumn
    except:
        pass

    '''Setup'''
    nSol = 5 # SPPRC return up to nSol most optimal, feasible solutions in each iteration
    nIntSol = 3 # Return up to nIntSol best integer solutions
    threshold = 1e-3 # Threshold marginal improvement over last stepsize iterations (add. stop criterion)
    stepsize = 10 # Additional stop criterion stepsize
    timePrint = False # Print output in command prompt while running
    waitFrequency = 1e-10000 # small float
    rmpSolverFile = "rosterlineMaster_win64.exe" # RMP self-executable file
    rmpSolverFile_integer = "rosterlineMaster_win64_integer.exe" # RMP (with binary requirement) self-executable file
    instanceFile = instance+'_'+str(run)+'.txt' # Instance file
    masterSolutionFile = 'masterProblem/masterSolution.txt' # Temporary file for communication with Mosel Xpress (lambdas)
    masterDualsFile = 'masterProblem/masterDuals.txt' # Temporary file for communication with Mosel Xpress (dual variables)
    columnsFile = 'columns.txt' # Temporary file for communication with Mosel Xpress (columns)
    solutionFile = '../../data/solutions/'+instance+'/decomposed model ' + dateStamp  + '_'+str(run)+'.csv' # File to store solution of CG algorithm

    '''Assorted times for logging'''
    times = {}
    times['Start'] = time.time()
    times['RMP'], times['SPPRC'], times['Total'] = {}, {}, {}
    timeInSPPRC = 0 #Counter for total time in SPPRC
    timeInRMP = 0 #Counter for total time in RMP
    timeInMP = 0 #Counter for total time in binary restricted RMP
    timeTotal = 0 #Counter for total time of algorithm
    startAlgorithm = time.time() #Set starting time

    '''Create initial graph for SPPRC'''
    if timePrint:
        print('\n\t\t\t\tColumn Generation\n'+'_'*79+'\n\n i Process\t\t\t'+
        '\t   Diff\t     Total\tReduced cost/\n\t\t\t\t\t\t\t\tObjective value\n'+'_'*79)
    data = spprc.dataLoader(filename = '../../data/instances/'+instance+'/'+instanceFile) # Load data
    nodes, arcs = spprc.graphMaker(data) # Create graph

    '''Generate initial columns'''
    subSolutions = cg.initializeSubSolutions(data) # Generate initial extreme points
    subSolution = subSolutions
    columns = cg.columnWriter(subSolution = subSolution, data = data, filename = columnsFile) # Write columns to file
    k = len(subSolution) # Number of columns

    '''Column generation loop'''
    proceed = True # Logival for loop control
    masterSolutions, masterObjectives, reducedCosts, columnCount, heuristicColumn = {}, {}, {}, {}, {} # Initializing dictionaries
    i = 0 # CG iteration count
    UBD = {'0': float('inf')} # dict to store iteration upper bound, first iteration UBD arbitrarily large
    while proceed:
        '''Iteration updates'''
        i += 1
        start = time.time()
        columnCount[str(i)] = k

        '''Obtain new upper bound by solving RMP_integer with available columns'''
        startMP = time.time()
        rename = True
        while rename: # File handling
            try:
                os.rename('../../data/instances/'+instance+'/'+instanceFile, 'masterProblem/instanceFile.txt')
                rename = False
            except:
                time.sleep(waitFrequency)
        os.chdir('masterProblem')
        os.startfile(rmpSolverFile_integer) # Solve binary restricted RMP
        os.chdir('..')
        while not (os.path.exists(masterSolutionFile) and os.path.exists(masterDualsFile)):
            time.sleep(waitFrequency) # Wait for RMP solution
        rename = True
        while rename: # File handling
            try:
                os.rename('masterProblem/instanceFile.txt', '../../data/instances/'+instance+'/'+instanceFile)
                rename = False
            except:
                time.sleep(waitFrequency)
        timeInMP += time.time() - startMP
        masterSolution, masterObjective = cg.readMoselSolution(masterSolutionFile) # Read from mosel text file output
        rmpSolved = False
        for l in masterSolution:
            if masterSolution[l] == 1: #RMP found a solution
                UBD[str(i)] = min(masterObjective, UBD[str(i-1)]) #Either new best UBD found or keep previous
                rmpSolved = True
                break
        if not rmpSolved: # If no new integer feasible columns, keep prev. UBD
            UBD[str(i)] = UBD[str(i-1)]
        os.remove(masterSolutionFile) # File handling
        os.remove(masterDualsFile) # File handling

        '''Run RMP'''
        startRMP = time.time()
        rename = True
        while rename: # File handling
            try:
                os.rename('../../data/instances/'+instance+'/'+instanceFile, 'masterProblem/instanceFile.txt')
                rename = False
            except:
                time.sleep(waitFrequency)
        os.chdir('masterProblem')
        os.startfile(rmpSolverFile) # Solve RMP
        os.chdir('..')
        while not (os.path.exists(masterSolutionFile) and os.path.exists(masterDualsFile)):
            time.sleep(waitFrequency) # Wait for RMP solution
        times['RMP'][str(i)] = time.time() - start
        timeInRMP += time.time() - startRMP
        rename = True
        while rename: # File handling
            try:
                os.rename('masterProblem/instanceFile.txt', '../../data/instances/'+instance+'/'+instanceFile)
                rename = False
            except:
                time.sleep(waitFrequency)
        masterSolution, masterObjective = cg.readMoselSolution(masterSolutionFile) # Read from mosel text file output
        masterSolutions[str(i)] = masterSolution # Add solution to master solutions
        masterObjectives[str(i)] = masterObjective # Add solution to master objectives
        bestRMPSolution = cg.solutionTransform(masterSolution, subSolutions, data) # Current best LP solution in x

        dualVariables = cg.readMoselDuals(masterDualsFile) # Read from mosel text file output
        os.remove(masterSolutionFile) # File handling
        os.remove(masterDualsFile) # File handling
        if timePrint:
            print('\n{:>2} RMP solved\t\t\t\t{:>6.2f}s\t   {:>6.2f}s\t\t{:>7.0f}'.format(i, times['RMP'][str(i)], time.time() - times['Start'], masterObjective))
        '''Run SPPRC'''
        start = time.time()
        subSolution, reducedCost, k = solveSPPRC(dualVariables, data, nodes, arcs, k = k, nSol = nSol) #Solve sub problem as SPPRC and obtain x-solution
        times['SPPRC'][str(i)] = time.time() - start
        timeInSPPRC += time.time() - start #Add to total time in SPPRC
        reducedCosts[str(i)] = reducedCost[str(list(reducedCost.keys())[0])] # Save best (most negative) reduced cost
        if timePrint:
            print('\n{:>2} SPPRC solved\t\t\t\t{:>6.2f}s\t   {:>6.2f}s\t\t{:>7.0f}'.format(i, times['SPPRC'][str(i)], time.time() - times['Start'], reducedCosts[str(i)]))
        timeTotal = time.time() - startAlgorithm
        if (cg.stopCriterion(reducedCost = reducedCost, k = k) or # Additional stop criterion - if lower bound stagnating and not vanilla weight is 1
            (masterSolution['1'] < 1 and
            (str(i - stepsize) in masterObjectives and
            (-masterObjectives[str(i)] + masterObjectives[str(i-stepsize)])/abs(masterObjectives[str(i-stepsize)]) < threshold)) or #Additional criterion if too much time has passed
            timeTotal > maxTime):
            UBD[str(i)] = UBD[str(i-1)]
            proceed = False
        else:
            subSolutions.update(subSolution) # Add newest subSolution to subSolutions
            os.remove(columnsFile) # File handling
            columns = cg.columnWriter(columns = columns, subSolution = subSolution, data=data, filename = columnsFile) # Write columns to file

        times['Total'][str(i)] = time.time() - times['Start']

    if timePrint:
        print('_'*79+'\n\n\t\t\t\t\t\t   {:>6.2f}s'.format(time.time() - times['Start']))

    '''Obtain and print solution'''
    solution = cg.solutionTransform(masterSolution, subSolutions, data) #Transform solution from lambda to x
    LBD = masterObjective # save lower bound
    if timePrint:
        print(masterObjective)
        print('\n', masterSolution)
        cg.printSolution(solution, data)

    '''Obtain best nIntSol feasible integer solutions'''
    intSolutions = {}
    for x in range(1, nIntSol+1):
        start = time.time()
        startMP = time.time()
        rename = True
        while rename: # rename rather than copy file
            try:
                os.rename('../../data/instances/'+instance+'/'+instanceFile, 'masterProblem/instanceFile.txt')
                rename = False
            except:
                time.sleep(waitFrequency)
        # os.system('copy ..\\..\\data\\instances\\'+instance+'\\'+instanceFile+' masterProblem\\instanceFile.txt') # copy rather than rename file
        os.chdir('masterProblem')
        os.startfile(rmpSolverFile_integer) # Solve RMP
        os.chdir('..')
        while not (os.path.exists(masterSolutionFile) and os.path.exists(masterDualsFile)):
            time.sleep(waitFrequency) # Wait for RMP solution
        times['RMP']['X'+str(x)] = time.time() - start
        if x != 1:
            timeInMP += time.time() - startMP
        rename = True
        while rename: # rename rather than copy file
            try:
                os.rename('masterProblem/instanceFile.txt', '../../data/instances/'+instance+'/'+instanceFile)
                rename = False
            except:
                time.sleep(waitFrequency)
        # os.remove('masterProblem/instanceFile.txt') # copy rather than rename file
        masterSolution, masterObjective = cg.readMoselSolution(masterSolutionFile) #Read from mosel text file output
        masterSolutions['X'+str(x)] = masterSolution #Add solution to master solutions
        masterObjectives['X'+str(x)] = masterObjective #Add solution to master objectives
        times['SPPRC']['X'+str(x)], reducedCosts['X'+str(x)] = 'n.a.', 'n.a.'
        columnCount['X'+str(x)], UBD['X'+str(x)] = k, 'n.a.'
        if timePrint:
            print('\n{:>2} RMP solved\t\t\t\t{:>6.2f}s\t   {:>6.2f}s\t\t{:>7.0f}'.format(i, times['RMP']['X'+str(x)], time.time() - times['Start'], masterObjective))
        os.remove(masterSolutionFile)
        os.remove(masterDualsFile)
        intSolutions['X'+str(x)] = cg.solutionTransform(masterSolution, subSolutions, data) #Transform solution from lambda to x
        if timePrint:
            print(masterObjective)
            cg.printSolution(intSolutions['X'+str(x)], data)
        times['Total']['X'+str(x)] = time.time() - times['Start']
        rmpSolved = False
        for l in masterSolutions['X'+str(x)]:
            if masterSolutions['X'+str(x)][l] == 1:
                rmpSolved = True
                os.remove(columnsFile)
                columns = cg.columnWriter(columns = columns, forbiddenColumn=int(l), data=data, filename = columnsFile) # Write columns to file
                break
        if not rmpSolved:
            break
    try:
        os.remove(columnsFile) # File handling
    except:
        pass

    '''Write to file'''
    cg.solutionWriter(instanceFile=instanceFile, solutionFile=solutionFile,
    nSol=nSol, threshold=threshold, stepsize=stepsize, i=i, times=times, columnCount=columnCount,
    masterSolutions=masterSolutions, masterObjectives=masterObjectives, UBD=UBD,
    reducedCosts=reducedCosts, solution=solution, intSolutions=intSolutions, data=data)

    return LBD, UBD[str(i)], times['Total'][list(times['Total'].keys())[-1]], i, timeInSPPRC, timeInRMP, timeInMP # Return metrics of interest
