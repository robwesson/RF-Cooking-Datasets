import copy
import random
import plotly.graph_objects as go
from commonFunctions import peakToAverage
from commonFunctions import NMSQE
from commonFunctions import multModesByWeights
from commonFunctions import peakToAverage
from commonFunctions import plotPARGraph
from commonFunctions import heuristicSwitch

def checkTrack(Modes, Weight1, Weight2, numSteps, heuristic):

    fig = go.Figure()
    steps = [i for i in range (0,numSteps)]
    
    deltaVector = list(map(lambda a,b : (a-b)/(numSteps-1), Weight1,Weight2))
    
    nextWeights = copy.deepcopy(Weight1)
    results = []
    for i in range (0,numSteps):
        nextWeights = list(map(lambda a,b: a+b, nextWeights, deltaVector))
        intensity = multModesByWeights(Modes, nextWeights)
        results.append(heuristicSwitch(heuristic, intensity, False))
        
            
    fig.add_trace(go.Scatter(x=steps, y=results, mode='lines', name='Track'))

    fig.update_layout(title='Checking a track between two Weights', xaxis_title="Step #", yaxis_title="PAR")
    fig.update_layout(height=600, width=1200)
    fig.show()