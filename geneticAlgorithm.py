import copy
import random
from commonFunctions import peakToAverage
from commonFunctions import NMSQE
from commonFunctions import multModesByWeights
from commonFunctions import peakToAverage
from commonFunctions import plotPARGraph
from commonFunctions import heuristicSwitch

def geneticAlgorithm(Modes, numSpecies, numSteps, deleteZeros, heuristic):
    print('numspecies = ' + str(numSpecies) + ' and numSteps = ' + str(numSteps))

    # Control parameters
    shuffle = True # shuffle sequences after each breeding cycle to better mix up the information content
    numWeights = len(Modes)  # in GA there are many sequences with one weight per Mode
    lenToSwap = 3 # define how long the sequence to be swapped is for each interbreeding

    #print('numWeights = ' +str(numWeights))

    # Generate  initial species list
    speciesList =[]
    for i in range (0, 1*numSpecies):
        speciesList.append([random.randint(0,10) for val in range(0,numWeights)])

    # Generate  PAR values from initial species list
    PARResults = []
    for i in range(0,len(speciesList)):
        intensity = multModesByWeights(Modes, speciesList[i])
        PARResults.append(heuristicSwitch(heuristic, intensity, deleteZeros))
        

    # select the top n, delete the rest
    for i in range (0,1*numSpecies):
            indexToDelete = PARResults.index(max(PARResults))
            del PARResults[indexToDelete]
            del speciesList[indexToDelete]
    print('BEST PAR (initial generation) = ' + str(min(PARResults)))
    print('BEGINNING BREEDING')

    graphPAR = []
    graphAveragePAR = []
    
    # now begin to breed species list for numSteps generations
    try:
        for steps in range(0,numSteps):
            childSpeciesList = copy.deepcopy(speciesList)
            swapIndex = random.randint(0,len(Modes)-lenToSwap)
            #print('swapping 3 elements from ' + str(swapIndex))
            # swap in pairs
            # step through species list in pairs swapping sequences of lenToSwap values at random offsets
            for i in range(0,numSpecies, 2):
                for j in range(swapIndex,swapIndex+lenToSwap):
                    #print ('i = ' + str(i) + ' and j = ' +str(j))
                    childSpeciesList[i][j] = speciesList[i+1][j]
                    childSpeciesList[i+1][j] = speciesList[i][j]
                   
                    
            # step through child list mutating single values
            for i in range (0,len(childSpeciesList)):
                index = random.randint(0,len(childSpeciesList[0])-1)
                childSpeciesList[i][index] = childSpeciesList[i][index] + random.random()-0.5
                if childSpeciesList[i][index]<0:
                    childSpeciesList[i][index]=0
                    
            # build the full, double length list for sorting
            speciesList = speciesList + childSpeciesList

            # calculate the PAR's
            PARResults =[]
            for i in range (0,len(speciesList)):
                PARResults.append(heuristicSwitch(heuristic, multModesByWeights(Modes,speciesList[i]), deleteZeros))

            # select the top n, delete the rest
            for i in range (0,numSpecies):
                indexToDelete = PARResults.index(max(PARResults))
                del PARResults[indexToDelete]
                del speciesList[indexToDelete]
                
            graphPAR.append(min(PARResults))
            graphAveragePAR.append(sum(PARResults)/len(PARResults))             
                  
            
            # output to screen some info to track the progress and also possibly to cut and paste into XL for graphing
            print('Pass '  + str(steps) + ' \tBEST PAR = \t' + str(min(PARResults)))

            # shuffle if enabled (to create enhanced mixing)
            if shuffle:
                # shuffle
                for i in range(0,len(speciesList)):
                    a = random.randint(0,len(speciesList)-1)    #-1 to ensure index always less than or equal to len-1
                    b = random.randint(0,len(speciesList)-2)    # -2 because we removed one by the time we insert
                    speciesList.insert(b, speciesList.pop(a))
    except KeyboardInterrupt:
        print('interrupt detected')
        print('exiting gracefully')
        
    # get best PAR and Weights from final species list
    bestWeights = [1 for k in range (0, len(Modes))]
    bestPAR = 100000
    
    for k in range (0, len(speciesList)):
        weights = speciesList[k]
        intensity = multModesByWeights(Modes, weights)
        PAR = heuristicSwitch(heuristic, intensity, deleteZeros)
        if PAR<bestPAR:
            bestPAR = copy.deepcopy(PAR)
            bestWeights = copy.deepcopy(weights)
            

    plotPARGraph(graphPAR, graphAveragePAR, 'Genetic Algorithm PAR Trajectory', 'Best PAR', 'Average PAR - Gene Pool')
    
    return bestWeights
