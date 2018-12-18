'''Functions used in spprc.py'''
from classes import *
import resourceExtensionFunctions as ref
import copy
import math

'''Check label resource feasibility'''
def isFeasible(label: Label):
    for r in Resources.resourceVec():
        resourceWindow = label.node.resourceWindows.__dict__[r]
        if type(resourceWindow) == dict: # Indexed resources
            for i in resourceWindow:
                if type(resourceWindow[i]) == dict: #Double-indexed resource
                    for j in resourceWindow[i]:
                        if (label.resources.__dict__[r][i][j] < resourceWindow[i][j][0] or
                            label.resources.__dict__[r][i][j] > resourceWindow[i][j][1]): # If resource outside window
                            return False
                else:
                    if (label.resources.__dict__[r][i] < resourceWindow[i][0] or
                        label.resources.__dict__[r][i] > resourceWindow[i][1]): # If resource outside window
                        return False
        else: # Non-indexed resources
            if (label.resources.__dict__[r] < resourceWindow[0] or
                label.resources.__dict__[r] > resourceWindow[1]): # If resource outside window
                return False
    return True # If no violations, return true

'''Check if label1 dominates label2 (assume dominance initial hypothesis)'''
def dominating(label1: Label, label2: Label, data):
    if label1.node != label2.node: # Same node
        return False
    if label1.node.day >= data['Days'][-1]: #No dominance in last or second last to create more solutions
        return False
    if label1.cost > label2.cost: # Weakly better cost
        return False
    if ('TWMax' in Resources.resourceVec() and
        label1.resources.TWMax > label2.resources.TWMax): # Weakly less work
            return False
    if ('TWMin' in Resources.resourceVec() and
        label1.resources.TWMin < data['Nmin'] and
        label1.resources.TWMin < label2.resources.TWMin): #Weakly more work or above min
        return False
    if 'TWMax_g' in Resources.resourceVec():
        for g in data['ShiftGroups']:
            if label1.resources.TWMax_g[str(g)] > label2.resources.TWMax_g[str(g)]: # Weakly less work (group)
                return False
    if 'TWMin_g' in Resources.resourceVec():
        for g in data['ShiftGroups']:
            if (label1.resources.TWMin_g[str(g)] < data['NminGroup'][str(g)] and
                label1.resources.TWMin_g[str(g)] < label2.resources.TWMin_g[str(g)]): #Weakly more work or above min (group)
                return False
    if 'TH' in Resources.resourceVec():
        for e in range(data['D_R']):
            if label1.resources.TH[str(e)] > label2.resources.TH[str(e)]: # Weakly less reduced rest
                return False
    if 'TV' in Resources.resourceVec():
        for e in range(data['W_W']):
            if label1.resources.TV[str(e)] > label2.resources.TV[str(e)]: # Weakly less weekends working
                return False
    if 'TL' in Resources.resourceVec():
        if label1.resources.TL > label2.resources.TL:
            return False
    if 'TI' in Resources.resourceVec():
        for p in data['PatternsIllegal']:
            for wd in data['WeekdaysStartPattern'][str(p)]:
                for d in data['DaysOnWeekday'][wd]:
                    if d <= data['Days'][-1] - data['D'][str(p)] + 1:
                        if label1.resources.TI[str(p)][str(d)] > label2.resources.TI[str(p)][str(d)]:
                            return False
    return True

'''Initialize initial label (start node) - Set to lower resource window bound'''
def initializeLabel(nodes, data):
    TWMax_g, TWMin_g, TH, TV, TI = {}, {}, {}, {}, {} # Prepare indexed resourceWindows (can maybe be abbreviated?)
    for g in data['ShiftGroups']:
        TWMax_g[str(g)] = 0
        TWMin_g[str(g)] = data['NminGroup'][str(g)]
    for e in range(data['D_R']):
        TH[str(e)] = 0
    for e in range(data['W_W']):
        TV[str(e)] = 0
    for p in data['PatternsIllegal']:
        TIp = {}
        for wd in data['WeekdaysStartPattern'][str(p)]:
            for d in data['DaysOnWeekday'][wd]:
                TIp[str(d)] = 0
                TI[str(p)] = TIp
    label = Label(name = 1, node = nodes[0], path = [nodes[0]], cost = 0)
    for r in Resources.resourceVec():
        if r == 'TWMax':
            label.resources.__dict__[r] = 0
        if r == 'TWMin':
            label.resources.__dict__[r] = data['Nmin']
        if r == 'TW':
            print('PLACEHOLDER TW Resource Window')
        if r == 'TWMax_g':
            label.resources.__dict__[r] = TWMax_g
        if r == 'TWMin_g':
            label.resources.__dict__[r] = TWMin_g
        if r == 'TW_g':
            print('PLACEHOLDER TW_g Resource Window')
        if r == 'TH':
            label.resources.__dict__[r] = TH
        if r == 'TV':
            label.resources.__dict__[r] = TV
        if r == 'TL':
            label.resources.__dict__[r] = 0
        if r == 'TI':
            label.resources.__dict__[r] = TI
    return label

'''Extend label using REFs and check feasibility'''
def extend(label: Label, arcs: [Arc], labelName, data):
    extendedArcs = [arc for arc in arcs if arc.start == label.node] # Likely slow implementation
    extendedLabels = []
    for extendedArc in extendedArcs:
        overtimeCost = 0 #To increase cost if workload is introduced
        resources = Resources() #To store resources
        for r in Resources.resourceVec():
            if r == "TWMax":
                resources.TWMax = ref.TWMax(label.resources.TWMax, extendedArc, data)
            if r == "TWMin":
                resources.TWMin = ref.TWMin(label.resources.TWMin, extendedArc, data)
            if r == "TW":
                print('PLACEHOLDER TW Resource Window')
            if r == "TWMax_g":
                resources.TWMax_g = ref.TWMax_g(label.resources.TWMax_g, extendedArc, data)
            if r == "TWMin_g":
                resources.TWMin_g = ref.TWMin_g(label.resources.TWMin_g, extendedArc, data)
            if r == 'TW_g':
                print('PLACEHOLDER TW_g Resource Window')
            if r == "TH":
                resources.TH = ref.TH(label.resources.TH, extendedArc, data)
            if r == "TV":
                resources.TV = ref.TV(label.resources.TV, extendedArc, data)
            if r == 'TL':
                resources.TL = ref.TL(label.resources.TL, extendedArc, data)
                overtimeCost = max(0, data['C_plus']*min(copy.copy(resources.TL) - data['W_N']*data['H_W'], extendedArc.workload)) #Extra cost for overtime
            if r == 'TI':
                resources.TI = ref.TI(label.resources.TI, extendedArc, data)
        newLabel = Label(
        name = labelName,
        node = extendedArc.end,
        path = label.path + [extendedArc.end],
        cost = label.cost + extendedArc.cost + overtimeCost,
        resources = resources
        )
        labelName += 1
        if isFeasible(newLabel):
            extendedLabels.append(newLabel)

    return extendedLabels, labelName

'''Load data from file generated in rosterlineDataMaker.mos'''
def dataLoader(filename: str):

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

'''Create graph from data'''
def graphMaker(data):
    inf = float('inf') # Declare infinite
    nodes, arcs = [], []
    name = 1

    # Create start node
    TWMax_g, TWMin_g, TH, TV, TI = {}, {}, {}, {}, {} # Prepare indexed resourceWindows (can maybe be abbreviated?)
    for g in data['ShiftGroups']:
        TWMax_g[str(g)] = [0, data['NmaxGroup'][str(g)]]
        TWMin_g[str(g)] = [0, inf]
    for e in range(data['D_R']):
        TH[str(e)] = [0, data['Nmax_R']]
    for e in range(data['W_W']):
        TV[str(e)] = [0, data['W_W'] - data['Nmin_W']]
    for p in data['PatternsIllegal']:
        TIp = {}
        for wd in data['WeekdaysStartPattern'][str(p)]:
            for d in data['DaysOnWeekday'][wd]:
                TIp[str(d)] = [0, data['D'][str(p)] - 1]
                TI[str(p)] = TIp
    resourceWindows = ResourceWindows()
    for r in Resources.resourceVec():
        if r == 'TWMax':
            resourceWindows.__dict__[r] = [0, data['Nmax']]
        if r == 'TWMin':
            resourceWindows.__dict__[r] = [0, inf]
        if r == 'TW':
            print('PLACEHOLDER TW Resource Window')
        if r == 'TWMax_g':
            resourceWindows.__dict__[r] = TWMax_g
        if r == 'TWMin_g':
            resourceWindows.__dict__[r] = TWMin_g
        if r == 'TW_g':
            print('PLACEHOLDER TW_g Resource Window')
        if r == 'TH':
            resourceWindows.__dict__[r] = TH
        if r == 'TV':
            resourceWindows.__dict__[r] = TV
        if r == 'TL':
            resourceWindows.__dict__[r] = [0, data['W_N']*data['H_W'] + data['WMax_plus']]
        if r == 'TI':
            resourceWindows.__dict__[r] = TI
    node = Node(name = name, day = 0, shiftType = 0, resourceWindows = resourceWindows)

    nodes.append(node)
    prevNodes, curNodes = [], [] # Lists for storing nodes of previos day and nodes of current day
    curNodes.append(node)
    prevNodes.append(node)

    # Create nodes other than start and end nodes, add arcs
    for day in data['Days']:
        curNodes = []
        for shiftType in data['ShiftTypes']: # Artificial shift excluded (can be added byshiftType in [0]+data['ShiftTypes'])
            name += 1
            resourceWindows = ResourceWindows()
            # node = Node(name = name, day = day, shiftType = shiftType)
            TWMax_g, TWMin_g, TH, TV, TI = {}, {}, {}, {}, {} # Prepare indexed resourceWindows (can maybe be abbreviated?)
            for g in data['ShiftGroups']:
                TWMax_g[str(g)] = [0, data['NmaxGroup'][str(g)]]
                if shiftType in data['ShiftTypesGroup'][str(g)]:
                    TWMin_g[str(g)] = [0, inf]
                else:
                    TWMin_g[str(g)] = [data['NminGroup'][str(g)], inf]
            for e in range(data['D_R']):
                TH[str(e)] = [0, data['Nmax_R']]
            for e in range(data['W_W']):
                TV[str(e)] = [0, data['W_W'] - data['Nmin_W']]
            for p in data['PatternsIllegal']:
                TIp = {}
                for wd in data['WeekdaysStartPattern'][str(p)]:
                    for d in data['DaysOnWeekday'][wd]:
                        TIp[str(d)] = [0, data['D'][str(p)] - 1]
                        TI[str(p)] = TIp
            for r in Resources.resourceVec():
                if r == 'TWMax':
                    resourceWindows.__dict__[r] = [0, data['Nmax']]
                if r == 'TWMin':
                    if shiftType in data['ShiftTypesOff']:
                        resourceWindows.__dict__[r] = [data['Nmin'], inf]
                    else:
                        resourceWindows.__dict__[r] = [0, inf]
                if r == 'TW':
                    print('PLACEHOLDER TW Resource Window')
                if r == 'TWMax_g':
                    resourceWindows.__dict__[r] = TWMax_g
                if r == 'TWMin_g':
                    resourceWindows.__dict__[r] = TWMin_g
                if r == 'TW_g':
                    print('PLACEHOLDER TW_g Resource Window')
                if r == 'TH':
                    resourceWindows.__dict__[r] = TH
                if r == 'TV':
                    resourceWindows.__dict__[r] = TV
                if r == 'TL':
                    resourceWindows.__dict__[r] = [0, data['W_N']*data['H_W'] + data['WMax_plus']]
                if r == 'TI':
                    resourceWindows.__dict__[r] = TI
            node = Node(name = name, day = day, shiftType = shiftType, resourceWindows = resourceWindows)
            nodes.append(node)
            curNodes.append(node)
            for prevNode in prevNodes: # Add arcs from previous day nodes if conditions satisfied
                if (str(prevNode.shiftType) in data['FollowingShiftsIllegal'] and # Required rest satisfied
                node.shiftType in data['FollowingShiftsIllegal'][str(prevNode.shiftType)]):
                    continue
                if (node.day in data['DaysOnWeekday']['SUN']): #Both or none weekend days working
                    if (prevNode.shiftType in data['ShiftTypesWorking'] and node.shiftType in data['ShiftTypesOff']):
                        continue
                    if (prevNode.shiftType in data['ShiftTypesOff'] and node.shiftType in data['ShiftTypesWorking']):
                        continue
                cost = data['C'][str(node.day)+' '+str(node.shiftType)] # Cost of working shift
                if (str(prevNode.shiftType) in data['FollowingShiftsPenalty'] and # Reduced rest
                        node.shiftType in data['FollowingShiftsPenalty'][str(prevNode.shiftType)]):
                    cost += data['C_R'] # Cost of reduced rest
                workload = 0
                if node.shiftType in data['ShiftTypesWorking']: # Workload
                    workload += data['T'][str(node.shiftType)]
                arcs.append(Arc(
                start = prevNode,
                end = node,
                cost = cost,
                workload = workload
                ))
        prevNodes = curNodes.copy()

    # Create end node, add arcs
    resourceWindows = ResourceWindows()
    TWMax_g, TWMin_g, TH, TV, TI = {}, {}, {}, {}, {} # Prepare indexed resourceWindows (can maybe be abbreviated?)
    for g in data['ShiftGroups']:
        TWMax_g[str(g)] = [0, data['NmaxGroup'][str(g)]]
        TWMin_g[str(g)] = [0, inf]
    for e in range(data['D_R']):
        TH[str(e)] = [0, data['Nmax_R']]
    for e in range(data['W_W']):
        TV[str(e)] = [0, data['W_W'] - data['Nmin_W']]
    for p in data['PatternsIllegal']:
        TIp = {}
        for wd in data['WeekdaysStartPattern'][str(p)]:
            for d in data['DaysOnWeekday'][wd]:
                TIp[str(d)] = [0, data['D'][str(p)] - 1]
                TI[str(p)] = TIp
    for r in Resources.resourceVec():
        if r == 'TWMax':
            resourceWindows.__dict__[r] = [0, data['Nmax']]
        if r == 'TWMin':
            resourceWindows.__dict__[r] = [0, inf]
        if r == 'TW':
            print('PLACEHOLDER TW Resource Window')
        if r == 'TWMax_g':
            resourceWindows.__dict__[r] = TWMax_g
        if r == 'TWMin_g':
            resourceWindows.__dict__[r] = TWMin_g
        if r == 'TW_g':
            print('PLACEHOLDER TW_g Resource Window')
        if r == 'TH':
            resourceWindows.__dict__[r] = TH
        if r == 'TV':
            resourceWindows.__dict__[r] = TV
        if r == 'TL':
            resourceWindows.__dict__[r] = [0, data['W_N']*data['H_W'] + data['WMax_plus']]
        if r == 'TI':
            resourceWindows.__dict__[r] = TI
    node = Node(name = name + 1, day = len(data['Days']) + 1, shiftType = 0, resourceWindows = resourceWindows)
    nodes.append(node)
    for prevNode in prevNodes: # Add arcs from previous day nodes to end node
        arcs.append(Arc(
        start = prevNode,
        end = node,
        cost = 0,
        workload = 0
        ))

    return nodes, arcs

'''Update costs on arcs from dual solution'''
def costUpdate(arcs, data, dualVariables):
    for arc in arcs:
        day = arc.end.day
        shiftType = arc.end.shiftType
        cost = 0
        if day in data['Days']:
            cost += data['C'][str(day)+' '+str(shiftType)] # Cost of working shift type at the end of the arc
        if (str(arc.start.shiftType) in data['FollowingShiftsPenalty'] and
                shiftType in data['FollowingShiftsPenalty'][str(arc.start.shiftType)]):
            cost += data['C_R'] # Cost of reduced rest
        if arc.start.day == 0:
            cost -= dualVariables['Convexity']
        for v in dualVariables:
            if v == 'MaxConsecDaysWorking':
                for d in data['Days']:
                    if d <= data['Days'][-1]-data['Nmax']:
                        if (day in range(d, d + data['Nmax'] + 1)
                            and shiftType in data['ShiftTypesWorking']):
                            cost -= dualVariables[v][str(d)]
            if v == 'MinConsecDaysWorking':
                for d in data['Days'] + [0]:
                    if d <= data['Days'][-1]-data['Nmin']:
                        if (day in range(d + 1, d + data['Nmin'] + 1)
                            and shiftType in data['ShiftTypesWorking']):
                            cost -= dualVariables[v][str(d)]
                        if day == d and shiftType in data['ShiftTypesOff']:
                            cost += data['Nmin'] * dualVariables[v][str(d)]
                        if day == d + 1 and shiftType in data['ShiftTypesOff']:
                            cost -= data['Nmin'] * dualVariables[v][str(d)]
            if v == 'MaxConsecDaysWorkingGroup':
                for g in data['ShiftGroups']:
                    for d in data['Days']:
                        if d <= data['Days'][-1]-data['NmaxGroup'][str(g)]:
                            if (day in range(d, d + data['NmaxGroup'][str(g)] + 1)
                                and shiftType in data['ShiftTypesGroup'][str(g)]):
                                cost -= dualVariables[v][str(g)+' '+str(d)]
            if v == 'MinConsecDaysWorkingGroup':
                for g in data['ShiftGroups']:
                    for d in data['Days'] + [0]:
                        if d <= data['Days'][-1]-data['NminGroup'][str(g)]:
                            if (day in range(d + 1, d + data['NminGroup'][str(g)] + 1)
                                and shiftType in data['ShiftTypesGroup'][str(g)]):
                                cost -= dualVariables[v][str(g)+' '+str(d)]
                            if day == d + 1 and shiftType in data['ShiftTypesGroup'][str(g)]:
                                cost += data['NminGroup'][str(g)]*dualVariables[v][str(g)+' '+str(d)]
                            if day == d and shiftType in data['ShiftTypesGroup'][str(g)]:
                                cost -= data['NminGroup'][str(g)]*dualVariables[v][str(g)+' '+str(d)]
            if v == 'MaxReducedRest':
                for d in data['Days']:
                    if d <= data['Days'][-1]-data['D_R']+1:
                        if (day in range(d, d + data['D_R']) and
                            str(arc.start.shiftType) in data['FollowingShiftsPenalty'] and
                            shiftType in data['FollowingShiftsPenalty'][str(arc.start.shiftType)]):
                            cost -= dualVariables[v][str(d)]
            if v == 'MinWeekendsOff':
                for w in data['Weeks']:
                    if w <= data['Weeks'][-1] - data['W_W'] + 1:
                        if (shiftType in data['ShiftTypesOff'] and
                            day in data['DaysOnWeekday']['SAT']): #Worth checking further
                            week = 0 #Start finding week of end node on arc
                            for ww in data['Weeks']:
                                if day in data['DaysInWeek'][str(ww)]:
                                    week = ww #Find week of end node of arc
                            if week in range(w, w + data['W_W']): #Saurday and off shift already checked
                                cost -= dualVariables[v][str(w)]
            if v == 'StrictDaysOff': #Off shift if strict day off
                for d in data['Days']:
                    if day == d and shiftType in data['ShiftTypesOff']:
                        cost += dualVariables[v][str(d)]
            if v == 'StrictDaysOff1': #Requirement for one strict day off
                for d in data['Days']:
                    if d in range(2, data['Days'][-1]):
                        if (day == d-1 and
                            str(shiftType) in data['StrictDayOff1']):
                            for s2 in data['StrictDayOff1'][str(shiftType)]:
                                cost -= dualVariables[v][str(d)+' '+str(shiftType)+' '+str(s2)]
                        if day == d+1:
                            for s1 in data['StrictDayOff1']:
                                if shiftType in data['StrictDayOff1'][str(s1)]:
                                    cost -= dualVariables[v][str(d)+' '+str(s1)+' '+str(shiftType)]
            if v == 'StrictDaysOff2': #Requirement for two strict days off
                for d in data['Days']:
                    if d in range(2, data['Days'][-1] - 1):
                        if (day == d-1 and
                            str(shiftType) in data['StrictDayOff2']):
                            for s2 in data['StrictDayOff2'][str(shiftType)]:
                                cost -= dualVariables[v][str(d)+' '+str(shiftType)+' '+str(s2)]
                        if day == d+2:
                            for s1 in data['StrictDayOff2']:
                                if shiftType in data['StrictDayOff2'][str(s1)]:
                                    cost -= dualVariables[v][str(d)+' '+str(s1)+' '+str(shiftType)]
            if v == 'WorkLoad_plus':
                for d in data['NormPeriodStartDays']:
                    if (day in range(d, d + data['N_N']) and
                        shiftType in data['ShiftTypesWorking']):
                        cost -= data['T'][str(shiftType)] * dualVariables[v][str(d)]
            if v == 'WorkLoad_minus':
                for d in data['NormPeriodStartDays']:
                    if (day in range(d, d + data['N_N']) and
                        shiftType in data['ShiftTypesWorking']):
                        cost -= data['T'][str(shiftType)] * dualVariables[v][str(d)]
            if v == 'RewardedPatterns':
                for p in data['PatternsRewarded']:
                    for dd in data['WeekdaysStartPattern'][str(p)]:
                        for d in data['DaysOnWeekday'][dd]:
                            if d <= data['Days'][-1] - data['D'][str(p)] + 1:
                                if day - d + 1 in range(1, data['D'][str(p)] + 1):
                                    for g in data['ShiftGroups']:
                                        if data['M'][str(day - d + 1)+' '+str(g)+' '+str(p)] == 1:
                                            if shiftType in data['ShiftTypesGroup'][str(g)]:
                                                cost -= dualVariables[v][str(p)+' '+str(d)]
            if v == 'PenalizedPatterns':
                for p in data['PatternsPenalized']:
                    for dd in data['WeekdaysStartPattern'][str(p)]:
                        for d in data['DaysOnWeekday'][dd]:
                            if d <= data['Days'][-1] - data['D'][str(p)] + 1:
                                if day - d + 1 in range(1, data['D'][str(p)] + 1):
                                    for g in data['ShiftGroups']:
                                        if data['M'][str(day - d + 1)+' '+str(g)+' '+str(p)] == 1:
                                            if shiftType in data['ShiftTypesGroup'][str(g)]:
                                                cost -= dualVariables[v][str(p)+' '+str(d)]
            if v == 'IllegalPatterns':
                for p in data['PatternsIllegal']:
                    for dd in data['WeekdaysStartPattern'][str(p)]:
                        for d in data['DaysOnWeekday'][dd]:
                            if d <= data['Days'][-1] - data['D'][str(p)] + 1:
                                if day - d + 1 in range(1, data['D'][str(p)] + 1):
                                    for g in data['ShiftGroups']:
                                        if data['M'][str(day - d + 1)+' '+str(g)+' '+str(p)] == 1:
                                            if shiftType in data['ShiftTypesGroup'][str(g)]:
                                                cost -= dualVariables[v][str(p)+' '+str(d)]
        arc.cost = cost

    return arcs
