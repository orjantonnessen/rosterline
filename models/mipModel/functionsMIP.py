'''Functions used in mip.py'''
import sys
import datetime
import csv

'''Load data from file generated in rosterlineDataMaker.mos'''
def dataLoader(filename: str): # Single dot if called from parent folder (columnGeneration.py)

    def loadValue(line: str, divider: int, format: type):
        if format == int:
            return int(line[divider+2:].replace('\n', ''))
        if format == float:
            return float(line[divider+2:].replace('\n', ''))
        return None

    def loadSet(line: str, divider: int, format: type):
        if format == int:
            return [int(i) for i in line[divider+3:].replace(']\n', '').split(' ')]
        if format == str:
            return [i for i in line[divider+3:].replace(']\n', '').split(' ')]
        return None

    def loadIndexedSet(line: str, divider: int, format: type):
        '''loadIndexedSet can likely be cleaned'''
        seek = divider
        keyStart = line.find('(', seek)
        indexedSet = {}
        while True:
            if keyStart == -1: #search is complete, all indexes identified
                break
            keyEnd = line.find(')', seek+1)
            seek = keyEnd
            index = str(line[keyStart+1:keyEnd].replace('\n', ''))
            keyStart = line.find('(', seek+1)
            if format == int:
                indexedSet[index] = [int(i) for i in line[keyEnd+3:keyStart-2].replace(']', '').split(' ') if i != '']
            elif format == str:
                indexedSet[index] = [i for i in line[keyEnd+3:keyStart-2].replace(']', '').split(' ') if i != '']
            elif format == float:
                indexedSet[index] = [float(i) for i in line[keyEnd+3:keyStart-2].replace(']', '').split(' ') if i != '']
        return indexedSet

    def loadIndexedValue(line: str, divider: int, format: type):
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
            if format == int:
                indexedValue[index] = int(line[keyEnd+2:keyStart].replace(']', ''))
            elif format == str:
                indexedValue[index] = line[keyEnd+2:keyStart.replace(']', '')]
            elif format == float:
                indexedValue[index] = float(line[keyEnd+2:keyStart].replace(']', ''))
        return indexedValue

    with open(filename, 'r') as file:
        data = {}
        # initializing loading
        dataline = file.readline()
        divider = dataline.find(":")
        for line in file: # Read through file and extract data
            # if find new divided, means prev line was read throughout
            if line.find(':') != -1:
                # load set/parameter
                identity = dataline[:divider]
                if identity in [
                    'T_R',
                    'T_RS',
                    'H',
                    'C_R',
                    'C_plus',
                    'C_minus',
                    'Nmax',
                    'Nmin',
                    'W_W',
                    'Nmin_W',
                    'D_S',
                    'Nmin_S',
                    'D_R',
                    'Nmax_R',
                    'H_S1',
                    'H_S2',
                    'N_N',
                    'W_N'
                ]:
                    data[identity] = loadValue(dataline, divider, int)
                elif identity in ['H_W', 'WMax_plus', 'WMax_minus']:
                    data[identity] = loadValue(dataline, divider, float)
                elif identity in [
                    'ShiftTypes',
                    'ShiftGroups',
                    'ShiftTypesWorking',
                    'ShiftTypesOff',
                    'PatternsRewarded',
                    'PatternsPenalized',
                    'PatternsIllegal',
                    'Weeks',
                    'Days',
                    'NormPeriodStartDays',
                ]:
                    data[identity] = loadSet(dataline, divider, int)
                elif identity in ['Weekdays']:
                    data[identity] = loadSet(dataline, divider, str)
                elif identity in [
                    'ShiftTypesGroup',
                    'FollowingShiftsIllegal',
                    'FollowingShiftsPenalty',
                    'StrictDayOff1',
                    'StrictDayOff2',
                    'DaysInWeek',
                    'WeekendDaysInWeek',
                    'DaysOnWeekday',
                    'DaysOnWeekdayInWeek'
                ]:
                    data[identity] = loadIndexedSet(dataline, divider, int)
                elif identity in ['WeekdaysStartPattern']:
                    data[identity] = loadIndexedSet(dataline, divider, str)
                elif identity in [
                'C',
                'P',
                'R',
                'T_S',
                'T_E',
                'T'
                ]:
                    data[identity] = loadIndexedValue(dataline, divider, float)
                elif identity in [
                'D',
                'NmaxGroup',
                'NminGroup',
                'M'
                ]:
                    data[identity] = loadIndexedValue(dataline, divider, int)
                # Move to next dataline
                dataline = line
                divider = line.find(':')
            else:
                dataline += line

    '''Read final line, unresolved how to include this in above loop'''
    identity = dataline[:divider]
    if identity in [
        'T_R',
        'T_RS',
        'H',
        'C_R',
        'C_plus',
        'C_minus',
        'Nmax',
        'Nmin',
        'W_W',
        'Nmin_W',
        'D_S',
        'Nmin_S',
        'D_R',
        'Nmax_R',
        'H_S1',
        'H_S2',
        'N_N',
        'W_N'
    ]:
        data[identity] = loadValue(dataline, divider, int)
    elif identity in ['H_W', 'WMax_plus', 'WMax_minus']:
        data[identity] = loadValue(dataline, divider, float)
    elif identity in [
        'ShiftTypes',
        'ShiftGroups',
        'ShiftTypesWorking',
        'ShiftTypesOff',
        'PatternsRewarded',
        'PatternsPenalized',
        'PatternsIllegal',
        'Weeks',
        'Days',
        'NormPeriodStartDays',
    ]:
        data[identity] = loadSet(dataline, divider, int)
    elif identity in ['Weekdays']:
        data[identity] = loadSet(dataline, divider, str)
    elif identity in [
        'ShiftTypesGroup',
        'FollowingShiftsIllegal',
        'FollowingShiftsPenalty',
        'StrictDayOff1',
        'StrictDayOff2',
        'DaysInWeek',
        'WeekendDaysInWeek',
        'DaysOnWeekday',
        'DaysOnWeekdayInWeek'
    ]:
        data[identity] = loadIndexedSet(dataline, divider, int)
    elif identity in ['WeekdaysStartPattern']:
        data[identity] = loadIndexedSet(dataline, divider, str)
    elif identity in [
    'C',
    'P',
    'R',
    'T_S',
    'T_E',
    'T'
    ]:
        data[identity] = loadIndexedValue(dataline, divider, float)
    elif identity in [
    'D',
    'NmaxGroup',
    'NminGroup',
    'M'
    ]:
        data[identity] = loadIndexedValue(dataline, divider, int)

    return data

'''Load solution lambdas from file generated in rosterlineMaster.mos'''
def readMoselSolution(filename: str = 'solution.txt'):

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
                if identity == 'xx':
                    solution = loadIndexedValue(dataline, divider)
                elif identity == 'objective':
                    objective = loadValue(dataline, divider)
                dataline = line
                divider = line.find(':')
            else:
                dataline += line
        identity = dataline[:divider]
        if identity == 'xx':
            solution = loadIndexedValue(dataline, divider)
        elif identity == 'objective':
            objective = loadValue(dataline, divider)

    return solution, objective

'''Solution transform from lambda-solution to rosterline'''
def solutionTransform(solution, data):
    solutionTransform = []
    for d in data['Days']:
        solutionDays = [0]*data['ShiftTypes'][-1]
        for s in data['ShiftTypes']:
            if solution[str(d)] == s:
                solutionDays[s-1] = 1
        solutionTransform.append(solutionDays)
    return solutionTransform

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
def solutionWriter(instanceFile, solutionFile, times, solution, objective, data):
    with open(solutionFile, 'w') as file:
        writer = csv.writer(file, delimiter = ',')
        writer.writerow(['Date', str(datetime.datetime.now())])
        writer.writerow(['Instance', instanceFile])
        writer.writerow([])
        writer.writerow(['Objective value', 'Total time'])
        writer.writerow([objective, times['Total']])
        writer.writerow([])
        writer.writerow(['Solution'] + data['ShiftTypes'])
        for d in data['Days']:
            writer.writerow([d] + solution[d-1])
