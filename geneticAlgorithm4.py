import copy
import random
from operator import add, mul
from commonFunctions import NMSQE
from commonFunctions import multModesByWeights
from commonFunctions import peakToAverage
from commonFunctions import plotPARGraph
from commonFunctions import heuristicSwitch
from commonFunctions import deleteDuplicates



# v2 incorporates self termination after n steps of zero improvement.

def geneticAlgorithm4(Modes, numSpecies, numMutations, deleteZeros, heuristic):
    print('numspecies = ' + str(numSpecies) + ' and numMutations = ' + str(numMutations))

    # Control parameters
    shuffle = True # shuffle sequences after each breeding cycle to better mix up the information content
    numWeights = len(Modes)  # in GA there are many sequences with one weight per Mode
    lenToSwap = 3 # define how long the sequence to be swapped is for each interbreeding

    #print('numWeights = ' +str(numWeights))

    # Generate  initial species list
    speciesList =[]
    for i in range (0, numSpecies):
        speciesList.append([random.randint(0,20) for val in range(0,numWeights)])

    # # Generate  PAR values from initial species list
    # PARResults = []
    # for i in range(0,len(speciesList)):
        # intensity = multModesByWeights(Modes, speciesList[i])
        # PARResults.append(heuristicSwitch(heuristic, intensity, deleteZeros))
        
    # # # select the top n, delete the rest
    # # for i in range (0,1*numSpecies):
            # # indexToDelete = PARResults.index(max(PARResults))
            # # del PARResults[indexToDelete]
            # # del speciesList[indexToDelete]
    # # print('BEST PAR (initial generation) = ' + str(min(PARResults)))
    print('BEGINNING BREEDING')

    # now begin to breed species list
    stepCount = 0
    countFails = 0
    bestPAR = 100000
    bestAveragePAR = 100000
    
    graphPAR = []
    graphAveragePAR = []
    
    try:
        while countFails<200:
            childSpeciesList = []
           
            for i in range(0,numSpecies-1):
                randRatio = random.random() #0-1
                #childSpeciesList.append(list(map(add, speciesList[i], speciesList[i+1])))
                childSpeciesList.append(list(map(lambda x,y: randRatio*x + (1-randRatio)*y, speciesList[i], speciesList[i+1])))

            # step through child list mutating 'n' values
            for i in range (0,len(childSpeciesList)):
                for j in range(0,numMutations):
                    index = random.randint(0,len(childSpeciesList[0])-1)
                    childSpeciesList[i][index] = childSpeciesList[i][index] + 2*random.random()-0.5
                    if childSpeciesList[i][index]<0:
                        childSpeciesList[i][index]=0
                    
            # build the full length list for sorting
            speciesList = speciesList + childSpeciesList

            # calculate the PAR's
            PARResults =[]
            for i in range (0,len(speciesList)):
                PARResults.append(heuristicSwitch(heuristic, multModesByWeights(Modes,speciesList[i]), deleteZeros))

            # delete duplicates
            # print(len(speciesList))
            # speciesList = deleteDuplicates(speciesList)
            # print(len(speciesList))
            
            # select the top n, delete the rest
            for i in range (0,len(childSpeciesList)):
                indexToDelete = PARResults.index(max(PARResults))
                del PARResults[indexToDelete]
                del speciesList[indexToDelete]
            
            thisBestPAR = min(PARResults)
            thisAveragePAR = sum(PARResults) / len(PARResults)
            
            graphPAR.append(thisBestPAR)
            graphAveragePAR.append(thisAveragePAR)
            
            # check for improvement        
            if thisBestPAR < bestPAR:
                countFails = 0
                bestPAR = thisBestPAR
            elif thisAveragePAR < bestAveragePAR:
                #countFails = 0
                countFails+=1
                bestAveragePAR = thisAveragePAR
            else:
                countFails+=1
            
            # output to screen some info to track the progress and also possibly to cut and paste into XL for graphing
            print('Pass '  + str(stepCount) + ' \tBEST PAR = \t' + str(thisBestPAR) + '\t countFails = ' + str(countFails))
                
            # shuffle if enabled (to create enhanced mixing)
            if shuffle:
                # shuffle
                for i in range(0,len(speciesList)):
                    a = random.randint(0,len(speciesList)-1)    #-1 to ensure index always less than or equal to len-1
                    b = random.randint(0,len(speciesList)-2)    # -2 because we removed one by the time we insert
                    speciesList.insert(b, speciesList.pop(a))
            
            # increment the index
            stepCount+=1  
            
            # re-normalise to average weight 10
            # prevents escalating weights from reducing the relative effectivness of noise amplitude
            for i in range (0,len(speciesList)):
                averageWeight = sum(speciesList[i])/len(speciesList[i])
                speciesList[i] = list(map(lambda x: x*10/averageWeight, speciesList[i]))
                
                
    except KeyboardInterrupt:
        print('interrupt detected')
        print('exiting gracefully')
    
 
     

     
    # loop finished! 
    # get best PAR and Weights from final species list
    bestWeights = [1 for k in range (0, len(Modes))]
    bestPAR = 100000
    
    #calculate all PAR's
    for k in range (0, len(speciesList)):
        weights = speciesList[k]
        intensity = multModesByWeights(Modes, weights)
        PAR = heuristicSwitch(heuristic, intensity, deleteZeros)
        if PAR<bestPAR:
            bestPAR = copy.deepcopy(PAR)
            bestWeights = copy.deepcopy(weights)
           
    plotPARGraph(graphPAR, graphAveragePAR, 'Genetic Algorithm PAR Trajectory', 'Best PAR', 'Average PAR - Gene Pool')
    
    return bestWeights
