'''Functions used in columnGeneration.py'''
import sys
sys.path.append('./subProblem')
from classes import *
import datetime
import csv

'''Generate initial columns such that RMP is feasible (e.g. 5*M and 2*O repeatedly) and add columns to Lambda.'''
def initializeSubSolutions(data):
    subSolutions = {}
    subSolution = []
    for d in data['Days']:
        if d % 7 in range(1,6):
            subSolution.append(data['ShiftTypesWorking'][0]) #First shift type working on weekdays
        else:
            subSolution.append(data['ShiftTypesOff'][0]) #Firt off shift type in weekend
    subSolutions['1'] = subSolution
    return subSolutions

'''Write columns to text file with Mosel parameters'''
def columnWriter(data, subSolution = None, forbiddenColumn: int = None, columns = None, filename: str = 'columns.txt'):
    if columns == None: # If columns do not already exist
        del columns
        columns = {'R': "Rosterlines: [", 'C': "C: [", 'A': "A: [", 'A_g': "A_g: [", 'A_W': "A_W: [", 'A_O': "A_O: [",'B' : "B: [", 'DD': "DD: [", 'V': "V: [", 'F': "ForbiddenRosterlines: ["}
    if subSolution != None: # If SP solution to be added to columns
        for k in subSolution:
            columns['R'] += str(k) + " "
            cost = 0 # C
            for d in data['Days']:
                for s in data['ShiftTypes']:
                    if subSolution[k][d-1] == s:
                        cost += data['C'][str(d)+' '+str(s)] #Add cost of shift
            for d in data['Days']:
                reducedRest = 0
                if d > 1: # Disregard day 1, assume no reduced rest first day (comes from off shift)
                    if str(subSolution[k][d-2]) in data['FollowingShiftsPenalty']:
                        if subSolution[k][d-1] in data['FollowingShiftsPenalty'][str(subSolution[k][d-2])]:
                            cost += data['C_R'] #Add cost of reduced rest
                            reducedRest += 1
                columns['V'] += "(" + str(d) + " " + str(k) + ") " + str(reducedRest) + " "
            if 'TL' in Resources.resourceVec(): #Add cost of overtime
                for d in data['NormPeriodStartDays']:
                    workload = 0
                    for dd in range(d,d + data['N_N']):
                        if str(subSolution[k][dd-1]) in data['T']: #If has workload greather than 0
                            workload += data['T'][str(subSolution[k][dd-1])]
                    overtime = max(0 , workload - data['W_N']*data['H_W'])
                    cost += data['C_plus']*overtime
            columns['C'] += "(" + str(k) + ") " + str(cost) + " "
            for d in data['Days']:
                for s in data['ShiftTypes']: # A
                    if subSolution[k][d-1] == s:
                        columns['A'] += "(" + str(d) + " " + str(s) + " " + str(k) + ") " + str(1) + " "
                    else:
                        columns['A'] += "(" + str(d) + " " + str(s) + " " + str(k) + ") " + str(0) + " "
                for g in data['ShiftGroups']: # A_g
                    sum = 0
                    for s in data['ShiftTypesGroup'][str(g)]:
                        if subSolution[k][d-1] == s:
                            sum += 1
                    columns['A_g'] += "(" + str(d) + " " + str(k) + " " + str(g) + ") " + str(sum) + " "
                sum = 0 # A_W
                for s in data['ShiftTypesWorking']:
                    if subSolution[k][d-1] == s:
                        sum += 1
                columns['A_W'] += "(" + str(d) + " " + str(k) + ") " + str(sum) + " "
                sum = 0 # A_O
                for s in data['ShiftTypesOff']:
                    if subSolution[k][d-1] == s:
                        sum += 1
                columns['A_O'] += "(" + str(d) + " " + str(k) + ") " + str(sum) + " "
            for w in data['Weeks']: # B
                sum = 0
                for s in data['ShiftTypesOff']:
                    for d in data['DaysOnWeekdayInWeek']['SAT '+str(w)]:
                        if subSolution[k][d-1] == s:
                            sum += 1
                columns['B'] += "(" + str(w) + " " + str(k) + ") " + str(sum) + " "
            for d in data['NormPeriodStartDays']: # DD
                sum = 0
                for dd in range(d, d + data['N_N']):
                    for s in data['ShiftTypesWorking']:
                        if subSolution[k][dd-1] == s:
                            sum += data['T'][str(s)]
                columns['DD'] += "(" + str(d) + " " + str(k) + ") " + str(sum) + " "
    if forbiddenColumn != None:
        columns['F'] += str(forbiddenColumn) + " "
    with open(filename, 'w') as file:
        line = ""
        for parameter in columns:
            if columns[parameter][-1] == "[": # Check that set not empty
                line += columns[parameter][:] + "]\n"
            else:
                line += columns[parameter][:-1] + "]\n"
        file.write(line)
    return columns

'''Load dual variables from file generated in rosterlineMaster.mos'''
def readMoselDuals(filename: str = 'masterDuals.txt'):

    def loadValue(line: str, divider: int):
        return float(line[divider+2:].replace('\n', ''))

    def loadIndexedValue(line: str, divider: int): # From dataLoader()
        '''loadIndexedValue can likely be cleaned'''
        seek = divider
        keyStart = line.find('(', seek)
        indexedValue = {}
        while True:
            if keyStart == -1: #search is complete, all indexes identified
                break
            keyEnd = line.find(')', seek+1)
            seek = keyEnd
            index = str(line[keyStart+1:keyEnd].replace('\n', ''))
            keyStart = line.find('(', seek+1)
            indexedValue[index] = float(line[keyEnd+2:keyStart].replace(']', ''))
        return indexedValue

    with open(filename, 'r') as file:
        dualVariables = {}
        # initializing loading
        dualsLine = file.readline()
        divider = dualsLine.find(":")
        for line in file: # Read through file and extract dual variables
            # if find new divided, means prev line was read throughout
            if line.find(':') != -1:
                identity = dualsLine[5:divider] # Ignore 'dual_' with 5
                if identity == 'Convexity':
                    dualVariables[identity] = loadValue(dualsLine, divider)
                else:
                    dualVariables[identity] = loadIndexedValue(dualsLine, divider)
                dualsLine = line
                divider = line.find(':')
            else:
                dualsLine += line

    '''Read final line, unresolved how to include this in above loop'''
    identity = dualsLine[5:divider] # Ignore 'dual_' with 5
    dualVariables[identity] = loadIndexedValue(dualsLine, divider)

    return dualVariables

'''Load solution lambdas from file generated in rosterlineMaster.mos'''
def readMoselSolution(filename: str = 'masterSolution.txt'):

    def loadValue(line: str, divider: int):
        return float(line[divider+2:].replace('\n', ''))

    def loadIndexedValue(line: str, divider: int): # From dataLoader()
        '''loadIndexedValue can likely be cleaned'''
        seek = divider
        keyStart = line.find('(', seek)
        indexedValue = {}
        while True:
            if keyStart == -1: #search is complete, all indexes identified
                break
            keyEnd = line.find(')', seek+1)
            seek = keyEnd
            index = str(line[keyStart+1:keyEnd].replace('\n', ''))
            keyStart = line.find('(', seek+1)
            indexedValue[index] = float(line[keyEnd+2:keyStart].replace(']', ''))
        return indexedValue

    with open(filename, 'r') as file:
        dataline = file.readline()
        divider = dataline.find(":")
        for line in file:
            if line.find(':') != -1:
                identity = dataline[:divider]
                if identity == 'lambda':
                    masterSolution = loadIndexedValue(dataline, divider)
                elif identity == 'objective':
                    masterObjective = loadValue(dataline, divider)
                dataline = line
                divider = line.find(':')
            else:
                dataline += line
        identity = dataline[:divider]
        if identity == 'lambda':
            masterSolution = loadIndexedValue(dataline, divider)
        elif identity == 'objective':
            masterObjective = loadValue(dataline, divider)

    return masterSolution, masterObjective

'''Solution transform from lambda-solution to rosterline'''
def solutionTransform(masterSolution, subSolutions, data):
    solution = []
    for d in data['Days']:
        solutionDays = [0]*data['ShiftTypes'][-1]
        for s in data['ShiftTypes']:
            for k in subSolutions:
                if subSolutions[k][d-1] == s:
                    solutionDays[s-1] += masterSolution[k]
        solution.append(solutionDays)
    return solution

'''Stop criterion for CG algorithm'''
def stopCriterion(reducedCost: dict, k: int = 0): #True if iterations finished
    for k in reducedCost:
        if reducedCost[k] < -1: # Originally 0, but to avoid error caused by numerical inprecision
            return False
    return True

'''Print solution to screen'''
def printSolution(solution, data):
    print('\n\n\n\t\t     Solution\n______________', end='')
    for s in data['ShiftTypes']:
        print('_________', end='')
    print('\n')
    print('Shift types: |  ', end='')
    for s in data['ShiftTypes']:
        print(' {:>2}   |  '.format(s), end = '')
    print()
    for d in data['Days']:
        print('Day {:>3}:     | '.format(d), end = '')
        for s in data['ShiftTypes']:
            if solution[d-1][s-1] > 0:
                print(' {:>5.3f} | '.format(solution[d-1][s-1]), end = '')
            else:
                print('       | ', end = '')
        print()

'''Write instance solution to file'''
def solutionWriter(instanceFile, solutionFile, nSol, threshold, stepsize, i,
times, columnCount, masterSolutions, masterObjectives, UBD, reducedCosts,
solution, intSolutions, data):
    with open(solutionFile, 'w') as file:
        writer = csv.writer(file, delimiter = ',')
        writer.writerow(['Date', str(datetime.datetime.now())])
        writer.writerow(['Instance', instanceFile])
        writer.writerow(['Max number of columns generated per iteration', nSol])
        writer.writerow(['Threshold', threshold])
        writer.writerow(['Stepsize', stepsize])
        writer.writerow([])
        writer.writerow(['Constraint', 'Master', 'Sub'])
        writer.writerow(['OneShiftPerDay', 0, 1])
        if 'TWMax' in Resources.resourceVec():
            writer.writerow(['MaxConsecDaysWorking', 0, 1])
        else:
            writer.writerow(['MaxConsecDaysWorking', 1, 0])
        if 'TWMin' in Resources.resourceVec():
            writer.writerow(['MinConsecDaysWorking', 0, 1])
        else:
            writer.writerow(['MinConsecDaysWorking', 1, 0])
        if 'TWMax_g' in Resources.resourceVec():
            writer.writerow(['MaxConsecDaysWorkingGroup', 0, 1])
        else:
            writer.writerow(['MaxConsecDaysWorkingGroup', 1, 0])
        if 'TWMin_g' in Resources.resourceVec():
            writer.writerow(['MinConsecDaysWorkingGroup', 0, 1])
        else:
            writer.writerow(['MinConsecDaysWorkingGroup', 1, 0])
        writer.writerow(['RequiredRest', 0, 1])
        writer.writerow(['ReducedRest', 0, 1])
        if 'TH' in Resources.resourceVec():
            writer.writerow(['MaxReducedRest', 0, 1])
        else:
            writer.writerow(['MaxReducedRest', 1, 0])
        writer.writerow(['BothDaysWeekend', 0, 1])
        if 'TV' in Resources.resourceVec():
            writer.writerow(['MinWeekendsOff', 0, 1])
        else:
            writer.writerow(['MinWeekendsOff', 1, 0])
        writer.writerow(['StrictDaysOff', 1, 0])
        writer.writerow(['StrictDaysOff1', 1, 0])
        writer.writerow(['StrictDaysOff2', 1, 0])
        writer.writerow(['MinStrictDaysOff', 1, 0])
        if 'TL' in Resources.resourceVec():
            writer.writerow(['WorkLoad_plus', 0, 1])
        else:
            writer.writerow(['WorkLoad_plus', 1, 0])
        writer.writerow(['WorkLoad_minus', 1, 0])
        writer.writerow(['RewardedPatterns', 1, 0])
        writer.writerow(['PenalizedPatterns', 1, 0])
        if 'TI' in Resources.resourceVec():
            writer.writerow(['IllegalPatterns', 0, 1])
        else:
            writer.writerow(['IllegalPatterns', 1, 0])
        writer.writerow(['OverlappingPatterns', 1, 0])
        writer.writerow([])
        writer.writerow(['Iteration', 'RMP solution time', 'Columns',
                        'Lower bound', 'Upper bound', 'SPPRC solution time',
                        'Most negative reduced cost', 'Total time'])
        for x in times['RMP']:
            writer.writerow([x, times['RMP'][x], columnCount[x],
                            masterObjectives[x], UBD[x], times['SPPRC'][x],
                            reducedCosts[x], times['Total'][x]])
        writer.writerow([])
        writer.writerow(['Non-integer lambdas'] + list(masterSolutions[str(i)].values()))
        writer.writerow([])
        intSols, x = True, 1
        while intSols:
            if 'X'+str(x) in masterSolutions:
                writer.writerow(['Integer lambdas (X'+str(x)+')'] + list(masterSolutions['X'+str(x)].values()))
                x += 1
            else:
                intSols = False
        writer.writerow([])
        writer.writerow(['Non-integer solution'] + data['ShiftTypes'])
        for d in data['Days']:
            writer.writerow([d] + solution[d-1])
        for x in intSolutions:
            writer.writerow([])
            writer.writerow(['Integer solution ('+x+')'] + data['ShiftTypes'])
            for d in data['Days']:
                writer.writerow([d] + intSolutions[x][d-1])
