import copy
import random
import plotly.graph_objects as go
from commonFunctions import peakToAverage
from commonFunctions import NMSQE
from commonFunctions import multModesByWeights
from commonFunctions import peakToAverage
from commonFunctions import plotPARGraph
from commonFunctions import heuristicSwitch

def checkOptimum(Modes, Weights, numSweeps, heuristic):

    numSteps = 100
    fig = go.Figure()
    steps = [i for i in range(0,numSteps+1)]
    
    intensity = multModesByWeights(Modes, Weights)  
    startPAR = heuristicSwitch(heuristic, intensity, False)
    
    # loop defining how many PAR degradation vectors to map
    for i in range(0,numSweeps):
        
        #create a random vector
        vector = [1*random.random() for j in range(0,len(Weights))]
        
        # apply it a bunch of times to see what happens to PAR
        
        PARTrack = [startPAR] # put the optimum PAR point in to the start of each track

        tempWeights = copy.deepcopy(Weights)
        
        # for j steps...
        for j in range (0,numSteps):
            
            # for each weight
            for k in range(0,len(tempWeights)):
                tempWeights[k]+= vector[k]
                
                # and check if a weight went below 0
                if tempWeights[k]<0:
                    tempWeights[k]=0
                    
            # append the new PAR value
            intensity = multModesByWeights(Modes, tempWeights)  
            PARTrack.append(heuristicSwitch(heuristic, intensity, False))
            
        fig.add_trace(go.Scatter(x=steps, y=PARTrack, mode='lines', name='Vec' + str(i)))


    fig.update_layout(title='Checking the Minima', xaxis_title="Step #", yaxis_title="PAR")
    fig.update_layout(height=600, width=1200)
    fig.show()