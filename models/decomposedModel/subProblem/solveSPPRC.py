'''SPPRC solver'''
import resourceExtensionFunctions as ref
import functionsSPPRC as fn
from classes import *
import copy
import time

def solveSPPRC(dualVariables, data, nodes, arcs, k: int = 0, nSol: int = 1):
	arcs = fn.costUpdate(arcs, data, dualVariables) # Update costs on all arcs
	processedLabels, unprocessedLabels = [], [] # Initialize unprocessedLabels and processedLabels, set counter
	initialLabel = fn.initializeLabel(nodes, data) # Initialize start label
	labelName = initialLabel.name + 1 # Increment label names
	unprocessedLabels.append(initialLabel) # Add initialLabel to unprocessedLabels

	'''Labelling algorithm'''
	while len(unprocessedLabels) != 0: # While there are unprocessed labels
		unprocessedLabel = unprocessedLabels.pop(0) # Get an unprocessed label
		extendedLabels, labelName = fn.extend(unprocessedLabel, arcs, labelName, data) # Extend the label
		for label1 in extendedLabels: # Check dominance among all extended labels and unprocessedLabels and processedLabels
			label1Dominated = False
			for label2 in processedLabels:
				if fn.dominating(label2, label1, data):
					label1Dominated = True
				elif fn.dominating(label1, label2, data):
					processedLabels.remove(label2)
			for label2 in unprocessedLabels:
				if fn.dominating(label2, label1, data):
					label1Dominated = True
				elif fn.dominating(label1, label2, data):
					unprocessedLabels.remove(label2)
			if not label1Dominated:
				unprocessedLabels.append(label1) # Add the extended label to unprocessedLabels if not dominated
		processedLabels.append(unprocessedLabel) # Add the unprocessed label

	'''Retrieve up to nSol most optimal, feasible and non-positive reduced cost labels'''
	solutionLabels = []
	found = False
	while not found:
		candidateLabel = processedLabels.pop() # Get one of processedLabels
		if candidateLabel.node.day == data['Days'][-1] + 1:
			solutionLabels.append(candidateLabel) # If candidate is feasible, assume most optimal
			found = True

	n, m = len(solutionLabels), len(processedLabels)
	while m > 0: # While there are still processedLabels
		m -= 1
		candidateLabel = processedLabels.pop() # Get one of processedLabels
		if (candidateLabel.node.day == data['Days'][-1] + 1
			and (candidateLabel.cost < 0
			or candidateLabel.cost < solutionLabels[0].cost)): # Check feasibility and non-neg
			for i in range(1, n + 1): # Find where to insert candidateLabel in list of best labels
				if candidateLabel.cost > solutionLabels[-i].cost:
					solutionLabels.insert(len(solutionLabels) - i + 1, candidateLabel)
					n += 1
					if n > nSol: # Trim solutionLabels if more than nSol
						solutionLabels.pop()
						n -= 1
					break

	# Format up to nSol most optimal, feasible solutions
	solutions, reducedCosts = {}, {}
	for label in solutionLabels:
		k += 1
		solutions[str(k)] = [0] * data['Days'][-1] # Non-numpy way
		# solution[str(i)] = np.zeros(data['Days'][-1]) # Numpy way
		for node in label.path[1:-1]: # Ignore artificial days (start and end)
			solutions[str(k)][node.day - 1] = node.shiftType
		reducedCosts[str(k)] = label.cost

	return solutions, reducedCosts, k
