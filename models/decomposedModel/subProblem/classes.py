'''File to create classes Node, Arc, Label'''
import inspect #To retrieve arguments in __self__ function

class Resources:
    def __init__(self,
        DummyResource: float = None, #Dummy resource in case no resources
        TWMax: float = None, # Max consecutive days working
        TWMin: float = None, # Min consecutive days working
        TWMax_g: dict = {None}, # Max consecutive days working shift group
        TWMin_g: dict = {None}, # Min consecutive days working shift group
        TH: dict = {None}, #Max number of days with reduced rest
        TV: dict = {None}, #Minimum number of weekends off
        TL: float = None, #Workload
        TI: dict = {'1': {'1': None}} #Illegal patterns
        ):
            self.DummyResource = DummyResource
            self.TWMax = TWMax
            self.TWMin = TWMin
            self.TWMax_g = TWMax_g
            self.TWMin_g = TWMin_g
            self.TH = TH
            self.TV = TV
            self.TL = TL
            self.TI = TI

    def resourceVec(): #Returns vector of resources used
        resourceVec = inspect.getfullargspec(Resources.__init__).args
        resourceVec.pop(0) #Remove 'self'
        resourceVec.pop(0) #Remove DummyResource
        return resourceVec

class ResourceWindows:
    '''All descriptions found in Resources class'''
    def __init__(self,
        DummyResource: float = [None],
        TWMax: [float] = [None],
        TWMin: [float] = [None],
        TWMax_g: dict = {None},
        TWMin_g: dict = {None},
        TH: dict = {None},
        TV: dict = {None},
        TL: [float] = [None],
        TI: dict = {'1': {'1': None}}
        ):
            self.DummyResource = DummyResource
            self.TWMax = TWMax
            self.TWMin = TWMin
            self.TWMax_g = TWMax_g
            self.TWMin_g = TWMin_g
            self.TH = TH
            self.TV = TV
            self.TL = TL
            self.TI = TI

class Node:
    def __init__(self,
    name: int = None,
    day: int = None,
    shiftType: int  = None,
    resourceWindows: ResourceWindows = ResourceWindows()):
        self.name = name
        self.day = day
        self.shiftType = shiftType
        self.resourceWindows = resourceWindows
    def __repr__(self):
        return "Node " + str(self.name)

class Arc:
    def __init__(self,
    start: Node,
    end: Node,
    cost: float,
    workload: float):
        self.start = start
        self.end = end
        self.name = "{},{},{}".format(self.end.day, self.start.shiftType, self.end.shiftType)
        self.cost = cost
        self.workload = workload
    def __repr__(self):
        return "Arc(" + self.name + ")"

class Label:
    def __init__(self,
    name: int = None,
    node: Node = Node(),
    path: [Node] = [None],
    cost: float = None,
    resources: Resources = Resources()):
        self.name = name
        self.node = node
        self.path = path
        self.cost = cost
        self.resources = resources

    def __repr__(self):
        rep = "Label " + str(self.name) + ";\n\tNode: " + str(self.node.name) + ",\n\tCost: " + str(self.cost)
        for r in Resources.resourceVec():
            rep = rep + ",\n\t" + r + ": " + str(self.resources.__dict__[r])
        return rep
