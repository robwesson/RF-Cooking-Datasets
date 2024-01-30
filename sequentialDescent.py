# Opening and Closing a file "MyFile.txt" 
# for object name file1. 
import random
from commonFunctions import peakToAverage
from commonFunctions import NMSQE
from commonFunctions import multModesByWeights
from commonFunctions import peakToAverage
from commonFunctions import heuristicSwitch

def sequentialDescent(Modes, deleteZeros, heuristic):
    
    numModes = len(Modes)
    # define weights
    Weights = [10 for i in range (0,numModes)]
    bestPAR = 1000000
    step = 1
    
    countFails = 0
    try:
        while step > 0.01:
            
            print('------------------------')
            print(' epoch for step = ' +str(step))
            print('------------------------')
            countFails = 0
            while countFails<1:
            
                #iterate sweeping all weights
                for i in range (0,numModes):
                    currentPAR = heuristicSwitch(heuristic, multModesByWeights(Modes, Weights), False)
                    #tempWeight = Weights [i]
                    testPoints = [j for j in range(-10, 10, 1)]
                    testPoints = list(map(lambda x: step*x+Weights[i], testPoints)) # add the weight to get the actual test values
                    PARCurve = []
                    #for testPoint in testPoints:
                    for j in range (len(testPoints)-1,-1,-1):
                        # step backward through the list removing all sub-zero vals
                        if testPoints[j]<0:
                            del testPoints[j]
                    for testPoint in testPoints:
                        Weights[i] = testPoint
                        PARCurve.append(heuristicSwitch(heuristic, multModesByWeights(Modes, Weights), False))
                    minIndex = PARCurve.index(min(PARCurve)) 
                    #print(testPoints)
                    #print(PARCurve)
                    print('Weight ' + str(i) + ' optimum is ' + str(min(PARCurve)) + ' at index = ' +str(minIndex) + ' and value = ' +str(testPoints[minIndex]))
                    #print(Weights[i])
                    Weights[i] = testPoints[minIndex]
                    #print(Weights[i])
                
                currentPAR = heuristicSwitch(heuristic, multModesByWeights(Modes, Weights), False)
                if currentPAR < bestPAR:
                    bestPAR = currentPAR
                    countFails = 0
                else:
                    countFails +=1
                    
                print('PAR = ' + str(bestPAR) + ' and countFails = ' +str(countFails))
                step = step/2
    except KeyboardInterrupt:
        print('interrupt detected')
        print('exiting gracefully')                            
                        
                    
            
    
    return Weights