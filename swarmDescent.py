import copy
import random
import plotly.graph_objects as go
from commonFunctions import peakToAverage
from commonFunctions import NMSQE
from commonFunctions import multModesByWeights
from commonFunctions import peakToAverage
from commonFunctions import plotPARGraph
from commonFunctions import plotPARGraph2D
from commonFunctions import heuristicSwitch
from commonFunctions import deltaT
from commonFunctions import deltaRange
from commonFunctions import directionOfTravel
from commonFunctions import plot3DTracksAllSpecies


def plot3DTracksAllSpecies(trackAllWeights):
    print('entering plot3DTracksAllSpecies')
    numSteps = len(trackAllWeights)
    print('numsteps = ' +str(numSteps))
    numSpecies = len(trackAllWeights[0])
    print('numspecies = ' +str(numSpecies))
    numModes = len(trackAllWeights[0][0])
    print('nummodes = ' +str(numModes))
    xValsAllSpecies = [[0 for i in range(0,numSteps)] for j in range(numSpecies)]
    print('xValsAllSpecies has size ' +str(len(xValsAllSpecies)) + ' by ' +str(len(xValsAllSpecies[0])))
    yValsAllSpecies = [[0 for i in range(0,numSteps)] for j in range(numSpecies)]
    zValsAllSpecies = [[0 for i in range(0,numSteps)] for j in range(numSpecies)]
    for i in range (0,numSteps):
        for j in range (0,numSpecies):
            xValsAllSpecies[j][i] = trackAllWeights[i][j][0]
            yValsAllSpecies[j][i] = trackAllWeights[i][j][1]
            zValsAllSpecies[j][i] = trackAllWeights[i][j][2]
    traces = []
    for i in range (0,numSpecies):
        traces.append(go.Scatter3d(x=xValsAllSpecies[i],y=yValsAllSpecies[i],z=zValsAllSpecies[i], mode='lines'))
    print('------------------')
    print(xValsAllSpecies[0])
    print(yValsAllSpecies[0])
    print(zValsAllSpecies[0])
    print('------------------')
    xVals = [1.1,2,3,4.223,5.9]
    yVals = [1,3,3,1,5]
    zVals = [1,8,7,14,15]
    
    #trace = go.Scatter3d(x=xVals,y=yVals,z=zVals, mode='lines')
    fig = go.Figure(data=traces)
    # fig.update_layout(
    # # scene = dict(
        # xaxis = dict(nticks=4, range=[-100,100],),
                     # yaxis = dict(nticks=4, range=[-50,100],),
                     # zaxis = dict(nticks=4, range=[-100,100],),),width=700,
        # margin=dict(r=20, l=10, b=10, t=10))
    fig.show()



def swarmDescent(Modes, numSpecies, deleteZeros, heuristic, runSilent):
    # declare initial weights for beginning gradient descent
    numModes = len(Modes)
    
    # allWeights = []
    # allPARs = []
    # currentWeight = copy.deepcopy(Weights)
    # remoteWeight = copy.deepcopy(Weights)
    # bestWeights = copy.deepcopy(Weights)    # python requires deep copy to make separate variables from an assignment statement
    # intensity = multModesByWeights(Modes, Weights)
    
    
    #initialise graph list variables to track PAR trajectory
    #graphPAR2D = [[0 for i in range(0,numSteps)] for j in range (0,numSpecies)]
    graphPAR2D = []
    # create initial weights for all species
    weights2D = []    
    
    # need to record all weights for all species to plot... how? 
    # only for 3 mode datasets! not normal operation
    # need array of:
    # num Weights
    # x
    # num Steps
    # x 
    # numSpecies
    # if numModes == 3:
        # trackAllWeights = [[[0 for i in range(0,numModes)] for j in range (0,numSteps)] for k in range (0,numSpecies)]
    
    trackAllWeights = []
    currentPARs = []
    # Set up initial Weights
    for i in range (0,numSpecies):
        weights2D.append([10*random.random() for i in range (0,numModes)])
    
    bestWeights2D = copy.deepcopy(weights2D)    
    bestPARs = [100000 for i in range(0,numSpecies)]
    
    stepNum=0
    overallBestPAR=10000
    noiseFactor = 10
    attractionFactor = 0.1
    try:
        while noiseFactor>0.05:
            
            
            # adapt weights randomly for all species, all weights (RANDOM WALK PART)
            adaptVals=[]
            for j in range (0,numSpecies):
                adaptVals.append([noiseFactor*(random.random()-0.5) for val in range(0,numModes)])
            
            #print('printing all of allWeights')
            #print('--------------------')
            #for j in range (0,len(allWeights)):
            #    print(allWeights[j])
            #    print(allPARs[j])
            #print('--------------------')   
            
            # 'feel the force' of all previous results
            # for all of allWeights
            if stepNum>0:
                for j in range (0,numSpecies):
                    
                    currentWeight = weights2D[j]
                    bestWeight = bestWeights2D[j]
                    currentPAR = currentPARs[j]
                    bestPAR = bestPARs[j]

                    
                    dT = deltaT(bestWeight, bestPAR, currentWeight, currentPAR)
                    dR = deltaRange(bestWeight, bestPAR, currentWeight, currentPAR)
                    DOT = directionOfTravel(bestWeight, bestPAR, currentWeight, currentPAR)
                    adaptVals[j] = list(map(lambda x,y:x+attractionFactor*y, adaptVals[j],DOT))
            
                    dT = deltaT(overallBestWeights, overallBestPAR, currentWeight, currentPAR)
                    dR = deltaRange(overallBestWeights, overallBestPAR, currentWeight, currentPAR)
                    DOT = directionOfTravel(overallBestWeights, overallBestPAR, currentWeight, currentPAR)
                    adaptVals[j] = list(map(lambda x,y:x+attractionFactor*y, adaptVals[j],DOT))
                    
            for j in range (0,numSpecies):
                for k in range (0,numModes):
                    weights2D[j][k] = weights2D[j][k] + adaptVals[j][k]
                    if (weights2D[j][k]<0):
                        weights2D[j][k] = 0
            if numModes == 3:
                temp = copy.deepcopy(weights2D)
                trackAllWeights.append(temp)
            
            currentPARs = []            
            # apply weights and calculate PARs
            for j in range (0,numSpecies):
                intensity = multModesByWeights(Modes, weights2D[j])
                PAR = heuristicSwitch(heuristic, intensity, deleteZeros)
                temp = copy.deepcopy(weights2D)
                # add to lists of weights and PARs
                #allWeights.append(temp)
                currentPARs.append(PAR)
            
            
            # is this test better than the best previous? Then update weights
            for j in range (0,numSpecies):
                if (currentPARs[j]<bestPARs[j]):
                    bestPARs[j] = copy.deepcopy(currentPARs[j])
                    bestWeights2D[j] = copy.deepcopy(weights2D[j])
            
            bestPARIndex = bestPARs.index(min(bestPARs))
            overallBestWeights = bestWeights2D[bestPARIndex]
            thisPassBestPAR = bestPARs[bestPARIndex]
            #thisPassAveragePAR = sum(currentPARs)/len(currentPARs)
            
            # Is PAR better? Update bestPAR and manage runtime loops
            if thisPassBestPAR < overallBestPAR:
                overallBestPAR = thisPassBestPAR
                countFails = 0
            else:
                countFails+=1
                
            # If countFails is too high, divide noiseFactor and reset
            # program terminates if noiseFactor too lower
            if countFails > 100:
                noiseFactor = noiseFactor/2
                countFails = 0
            
            #   update graph list variables to track PAR trajectory  
            #for j in range(0,numSpecies):
            graphPAR2D.append(currentPARs)
            
            # iterate stepNum at ends
            print('PAR ' + str(stepNum)  + '=\t' + str(thisPassBestPAR) + '\tMinPAR = ' + str(overallBestPAR) + '\t Fails = ' + str(countFails) + '\tNoise = ' + str(noiseFactor))
            
            stepNum+=1
            
    except KeyboardInterrupt:
        print('interrupt detected')
        print('exiting gracefully')
    # finished? then create PAR trajectory graphy
    # ... and output best Weights.
    
    plotNames =[]
    for j in range (0,numSpecies):
        plotNames.append('Plot for Species #' +str(j))
    
    if not runSilent:
        plotPARGraph2D(graphPAR2D, 'Gradient Descent PAR Trajectory', plotNames)
    
    # special case of 3-mode test cases where we can graph the trajectories in 2D
    if numModes == 3:
        plot3DTracksAllSpecies(trackAllWeights)
        
    return overallBestWeights
