import copy
import random
from commonFunctions import peakToAverage
from commonFunctions import NMSQE
from commonFunctions import multModesByWeights
from commonFunctions import plotPARGraph
from commonFunctions import heuristicSwitch

# ideas for improvements: running with a good step, plus self termination


        
def gradientDescent2(Modes, deleteZeros, heuristic):
    # declare initial weights for beginning gradient descent
    
    startBestMode = False
    
    if startBestMode:
        allModePARs = []
        for i in range (0,len(Modes)):
            allModePARs.append(heuristicSwitch(heuristic, Modes[i], deleteZeros))
        bestModeIndex = allModePARs.index(min(allModePARs))
        Weights = [0 for j in range(0,len(Modes))]
        Weights[bestModeIndex] = 10
    else:
        Weights = [10 for i in range (0,len(Modes))]
    
    bestWeights = copy.deepcopy(Weights)    # python requires deep copy to make separate variables from an assignment statement
        
    intensity = multModesByWeights(Modes, Weights)
    bestPAR = heuristicSwitch(heuristic, intensity, deleteZeros)
    lastStepBetter = False # set up variable that controls whether to go for new adaptVals or reuse last (successful) vector
    countFails = 0 # metric to count loops without improvement
    countWins = 0
    noiseMultiplier = 10
    i=0 #counter

    
    #initialise graph list variables to track PAR trajectory
    graphPAR = []
    graphBestPAR = []
    try:
        while countFails<=500:
            # adapt weights by +-0.5 each weight
            if not lastStepBetter:
                adaptVals = [noiseMultiplier*(random.random()-0.5) for val in range(len(Modes))]
            for j in range (0,len(Weights)):
                Weights[j] = bestWeights[j] + adaptVals[j]
                if (Weights[j]<0):
                    Weights[j] = 0
     #           if (Weights[j]>200):
     #               Weights[j]=200
            # apply weights
            intensity = multModesByWeights(Modes, Weights)
            PAR = heuristicSwitch(heuristic, intensity, deleteZeros)
            
            # is this test better than the best previous? Then update weights
            if (PAR<bestPAR):
                bestPAR = copy.deepcopy(PAR)
                bestWeights = copy.deepcopy(Weights)
                lastStepBetter = True
                countFails = 0
                countWins+=1
            else: 
                lastStepBetter = False
                countFails+=1
                countWins=0
            
            # handle the case where we have very small incrementing wins that could go on and on
            if countWins>=100:
                lastStepBetter = False
                countWins=0
                
            if (countFails>250 and noiseMultiplier>0.1):
                noiseMultiplier = noiseMultiplier/2
                countFails=0
                
            # output to screen
            print('PAR ' + str(i)  + '\t=\t' + str(PAR) + '\tMinPAR = ' + str(bestPAR) + '\t Fails/Wins = ' +str(countFails) + '/' + str(countWins) + '\tNoise = ' + str(noiseMultiplier))
            i+=1    # update counter

            graphPAR.append(PAR)
            graphBestPAR.append(bestPAR)
            
            # Normalise back to 10
            averageWeight = sum(Weights)/len(Weights)
            Weights = list(map(lambda x: 10*x/averageWeight, Weights))
            
    except KeyboardInterrupt:
        print('interrupt detected')
        print('exiting gracefully')            
        
    # finished? then create PAR trajectory graphy
    # ... and output best Weights.
    
    plotPARGraph(graphPAR,graphBestPAR, 'Gradient Descent v2 PAR Trajectory', 'PAR', 'Best PAR')
    return bestWeights
