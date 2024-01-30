import copy
import random
from commonFunctions import peakToAverage
from commonFunctions import NMSQE
from commonFunctions import multModesByWeights
from commonFunctions import peakToAverage
from commonFunctions import plotPARGraph
from commonFunctions import heuristicSwitch


def gradientDescent(Modes, Weights, numSteps, deleteZeros, heuristic, runSilent):
    # declare initial weights for beginning gradient descent
    
    bestWeights = copy.deepcopy(Weights)    # python requires deep copy to make separate variables from an assignment statement
    intensity = multModesByWeights(Modes, Weights)
    bestPAR = heuristicSwitch(heuristic, intensity, deleteZeros)
    
    #initialise graph list variables to track PAR trajectory
    graphPAR = [0 for i in range(0,numSteps)]
    graphBestPAR = copy.deepcopy(graphPAR)
    try:
        for i in range(0,numSteps):
            # adapt weights by +-0.5 each weight
            adaptVals = [random.random()-0.5 for val in range(len(Modes))]
            for j in range (0,len(Weights)):
                Weights[j] = bestWeights[j] + adaptVals[j]
                if (Weights[j]<0):
                    Weights[j] = 0
            # apply weights
            intensity = multModesByWeights(Modes, Weights)
            PAR = heuristicSwitch(heuristic, intensity, deleteZeros)
            
            # output to screen
            if not runSilent:
                print('PAR ' + str(i)  + '\t=\t' + str(PAR) + ' MinPAR = ' + str(bestPAR))
            
            # is this test better than the best previous? Then update weights
            if (PAR<bestPAR):
                bestPAR = copy.deepcopy(PAR)
                bestWeights = copy.deepcopy(Weights)
            
            #   update graph list variables to track PAR trajectory        
            graphPAR[i] = PAR
            graphBestPAR[i] = bestPAR
        
    except KeyboardInterrupt:
        print('interrupt detected')
        print('exiting gracefully')
    # finished? then create PAR trajectory graphy
    # ... and output best Weights.
    if not runSilent:
        plotPARGraph(graphPAR,graphBestPAR, 'Gradient Descent PAR Trajectory', 'PAR', 'Best PAR')
    
    return bestWeights
