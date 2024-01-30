# Opening and Closing a file "MyFile.txt" 
# for object name file1. 
import random
import copy
from commonFunctions import peakToAverage
from commonFunctions import NMSQE
from commonFunctions import multModesByWeights
from commonFunctions import peakToAverage
from commonFunctions import heuristicSwitch

def manyRandoms(allResultsListOfLists, numRemixes, deleteZeros, heuristic):
    print('entering subroutine')
    # try some different remixes
    lowestPAR = 1000000
    numFiles = len(allResultsListOfLists)
    numPoints = len(allResultsListOfLists[0])
    bestWeights = [random.randint(0,10) for val in range(numFiles)]
    listPAR = []    # for graphing PAR trajectory
    
    for i in range(0,numRemixes):
        # run once per remix
        print('step ' +str(i) + ' of ' +  str(numRemixes), end="\r")
        algoIntensity = [(0) for i in range(numPoints)]
        
        # gen random numbers from 1-10 for each file and calculate PAR using functions from 'misc'
        randValList = [random.randint(0,10) for val in range(numFiles)]  
        algoIntensity = multModesByWeights(allResultsListOfLists, randValList)
        currentPAR = heuristicSwitch(heuristic, algoIntensity, deleteZeros)
        listPAR.append(currentPAR)  # for graphing PAR trajectory
        if (currentPAR < lowestPAR):
            lowestPAR = copy.deepcopy(currentPAR)
            print(lowestPAR)
            bestWeights = copy.deepcopy(randValList)
    
    return bestWeights