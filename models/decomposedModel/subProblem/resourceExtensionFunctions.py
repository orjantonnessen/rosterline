'''REF functions in the problem'''
import copy

'''TWMax'''
def TWMax(TWMax, arc, data): #Max consecutive days. TWMax is scalar input
    j=arc.end.shiftType
    if j in data['ShiftTypesWorking']:
        return TWMax + 1
    else:
        return 0

'''TWMax_g'''
def TWMax_g(TWMax_g,arc,data): #TWMax_g is a dictionary of the resource for each g in working ShiftTypes, e.g. TWMax_g={'1': 3, '2': 2, '3': 1}
    j=arc.end.shiftType
    newTWMax_g = copy.copy(TWMax_g)
    for g in data['ShiftGroups']: #One function for each shift group
        if j in data['ShiftTypesGroup'][str(g)]:
            newTWMax_g[str(g)] += 1
        else:
            newTWMax_g[str(g)] = 0
    return newTWMax_g

'''TWMin'''
def TWMin(TWMin,arc,data): #Min consecutive days
    i=arc.start.shiftType
    j=arc.end.shiftType
    ShiftTypesWorking=data['ShiftTypesWorking']
    if (i in ShiftTypesWorking and j in ShiftTypesWorking):
        return TWMin+1
    elif (not(i in ShiftTypesWorking) and j in ShiftTypesWorking): #Not in working needed to also handle
        return 1
    else:
        return TWMin

'''TWMin_g'''
def TWMin_g(TWMin_g,arc,data): #TWMin_g is a dictionary of the resource for each g in working ShiftTypes, e.g. TWMin_g={'1': 3, '2': 2, '3': 1}
    i=arc.start.shiftType
    j=arc.end.shiftType
    ShiftTypesGroup=data['ShiftTypesGroup']
    newTWMin_g = copy.copy(TWMin_g)
    for g in ShiftTypesGroup: #One function for each shift group
        if (i in ShiftTypesGroup[str(g)] and j in ShiftTypesGroup[str(g)]):
            newTWMin_g[str(g)] += 1
        elif (not(i in ShiftTypesGroup[str(g)]) and j in ShiftTypesGroup[str(g)]):
            newTWMin_g[str(g)] = 1
    return newTWMin_g

'''TH (Required rest)'''
def TH(TH,arc,data): #TH is a dictionary of the resource for each e in 0,..,D_R-1. E.g. TH={'0': 1, '1': 0, .... , 'D_R-1': 1}
    i=arc.start.shiftType
    j=arc.end.shiftType
    d=arc.end.day
    D_R=data['D_R']
    FollowingShiftsPenalty=data['FollowingShiftsPenalty']
    newTH = copy.copy(TH)
    for e in range(D_R): #One function for each rolling time horizon start (e in 0,...,D_R-1)
        #Calculate ksi parameter:
        if (d % D_R) == (1+e):
            ksi = 0
        else:
            ksi = 1
        #Calculate resource extension:
        if (str(i) in FollowingShiftsPenalty and j in FollowingShiftsPenalty[str(i)]): #FollowingShiftsPenalty['i'] is not empty to avoid error
            newTH[str(e)] = ksi * newTH[str(e)] + 1
        else:
            newTH[str(e)] = ksi * newTH[str(e)]

    return newTH

'''TV (Weekends)'''
def TV(TV,arc,data): #TV is a dictionary of the resource for each e in 0,..,W_W-1. E.g. TV={'0': 1, '1': 0, .... , 'W_W-1': 1}
    i=arc.start.shiftType
    j=arc.end.shiftType
    d=arc.end.day
    W_W=data['W_W']
    newTV = copy.copy(TV)
    for e in range(W_W):
        if (d in data['DaysOnWeekday']['SAT'] and j in data['ShiftTypesWorking']):
            newTV[str(e)]=newTV[str(e)]+1
        for w in data['Weeks']:
            if ((w % W_W) == (1+e) and d in data['DaysOnWeekdayInWeek']['MON '+str(w)]):
                newTV[str(e)] = 0
                break
    return newTV

'''TI (Illegal patterns)'''
def TI(TI,arc,data): #TI is a dictionary of the resource for each p in P_I and for each p a dictionary of days. E.g. with two patterns TI={'1': {'1': 0, '2': 1,...}, '2': {'1': 0, '2': 1,...}}
    i=arc.start.shiftType
    j=arc.end.shiftType
    d=arc.end.day
    newTI = copy.deepcopy(TI)
    g=0 #To store shift group of shift j
    for gg in data['ShiftGroups']:
        if j in data['ShiftTypesGroup'][str(gg)]:
            g = gg

    for p in data['PatternsIllegal']:
        for wd in data['WeekdaysStartPattern'][str(p)]:
            for dd in data['DaysOnWeekday'][wd]:
                if dd <= data['Days'][-1] - data['D'][str(p)] + 1:
                    if g != 0 and d >= dd and d <= dd + data['D'][str(p)] - 1 and data['M'][str(d-dd+1)+' '+str(g)+' '+str(p)] == 1:
                        newTI[str(p)][str(dd)] += 1
                    else:
                        newTI[str(p)][str(dd)] = 0
    return newTI
