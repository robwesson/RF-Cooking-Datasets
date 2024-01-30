import plotly.graph_objects as go
from plotly.subplots import make_subplots
import copy 
from operator import add, mul
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from orthogonality import calcOrthogonality

    
def readProcessFile(fileName):
    # read file into list of strings
    file1 = open(fileName,"r")
    stringList = file1.readlines()
    file1.close() 

    # take off headers
    del stringList[0]
    del stringList[0]  

    # declare variable lists
    xDims = []
    yDims = []
    zDims = []
    intensity = []

    for lines in stringList:
        strings = lines.split()
        xDims.append(float(strings[0]))
        yDims.append(float(strings[1]))
        zDims.append(float(strings[2]))
        intensity.append(float(strings[3]))
        
    # create a result structure with all the data in so we can 'clip' it to size to suit the load which we care about
    # ... and to make it more portable - there will be multiples of these coexisitng soon
    resultStructure =  {}
    resultStructure["xDims"] = xDims
    resultStructure["yDims"] = yDims
    resultStructure["zDims"] = zDims
    resultStructure["intensity"] = intensity

    return resultStructure
    
def heuristicSwitch(x, intensity, deleteZeros):
    if x==1:
        return peakToAverage(intensity, deleteZeros)
    else:
        return NMSQE(intensity, deleteZeros)   
    


#fig.add_trace(go.Heatmap(z=[[1,2,3],[3,2,1],[1,2,3]]),row=1,col=1)

def plotHeatMap2(resultStructure, title, zList):
    fig = make_subplots(rows=2, cols=3, 
        column_widths=[0.3,0.3,0.3], row_heights=[1,1],    
        subplot_titles=('Z = ' + str(zList[0]), 'Z = ' + str(zList[1]), 'Z = ' + str(zList[2]), 'Z = ' + str(zList[3]), 'Z = ' + str(zList[4]), 'Z = ' + str(zList[5])))
    # print('----------------')
    xDims = resultStructure['xDims']
    yDims = resultStructure['yDims']
    zDims = resultStructure['zDims']
    intensity = resultStructure['intensity']
    print('x,y and z dims:')
    print(len(xDims))
    print(len(yDims))
    print(len(zDims))
    print(len(intensity))
    
    intensity = resultStructure['intensity']
    resultStructure = reSquareDS(resultStructure)    
    intensity = resultStructure['intensity']
    # print('----------------')
    xDims = resultStructure['xDims']
    yDims = resultStructure['yDims']
    zDims = resultStructure['zDims']
    intensity = resultStructure['intensity']
    print('resquared x,y and z dims:')
    print(len(xDims))
    print(len(yDims))
    print(len(zDims))
    print(len(intensity))
    print('----------------')
    
    rowList = [1,1,1,2,2,2]
    colList = [1,2,3,1,2,3]

    for i in range (0,len(zList)):
        # prep data
        tempRS = copy.deepcopy(resultStructure)
        
        xDims = tempRS['xDims']
        yDims = tempRS['yDims']
        zDims = tempRS['zDims']
        intensity = tempRS['intensity']
        maxIntensity = max(intensity)
        xMax = int(max(xDims))
        xMin = int(min(xDims))
        yMax = int(max(yDims))
        yMin = int(min(yDims))
        step = 5#int(xDims[1] - xDims[0])
        xSteps = list(range(xMin, xMax+step, step))
        ySteps = list(range(yMin, yMax+step, step))

        # run a loop to leave only what is wanted (ie z=z)
        n=len(xDims)
        for j in range (n-1,-1,-1):     # needs to stop at 0 so range is to -1. Test it.
            if not(zDims[j]==zList[i]):
                del xDims[j]
                del yDims[j]
                del zDims[j]
                del intensity[j]

        intensityListOfLists=[]
        
        for j in range (0,len(ySteps)):
            intensityListOfLists.append(intensity[j*len(xSteps):(j+1)*len(xSteps)])
        
        #print('intensityListOfLists = ' + str(intensityListOfLists))
        fig.add_trace(go.Heatmap(x=xSteps,y=ySteps,z=intensityListOfLists, zmin=0,zmax=maxIntensity), row = rowList[i], col = colList[i])
        
    fig.update_layout(title=title, xaxis_title="X", yaxis_title="Y")
    fig.update_layout(height=900, width=1200)
    fig.show()
    return True
    

def plotHeatMap(resultStructure, z, title):
    tempRS = copy.deepcopy(resultStructure)
    xDims = tempRS['xDims']
    yDims = tempRS['yDims']
    zDims = tempRS['zDims']
    intensity = tempRS['intensity']
    xMax = int(max(xDims))
    #print('----------------------')
    #print(xDims)
    #print('----------------------')
    #print(yDims)
    #print('----------------------')
    xMin = int(min(xDims))
    yMax = int(max(yDims))
    yMin = int(min(yDims))
    #print(xMax)
    #print(xMin)
    #print(yMax)
    #print(yMin)
    step = 5#int(xDims[1] - xDims[0])
    xSteps = list(range(xMin, xMax+step, step))
    ySteps = list(range(yMin, yMax+step, step))
    #print('----------------------')
    #print(xSteps)
    #print('----------------------')
    #print(ySteps)
    maxIntensity = max(intensity)   # to scale colourbar on heatmaps
    
    # run a loop to leave only what is wanted (ie z=z)
    n=len(xDims)
    for i in range (n-1,-1,-1):     # needs to stop at 0 so range is to -1. Test it.
        if not(zDims[i]==z):
            del xDims[i]
            del yDims[i]
            del zDims[i]
            del intensity[i]

    xx = xSteps
    yy = ySteps
    zz=intensity
    intensityListOfLists=[]
    
    for i in range (0,len(ySteps)):
        intensityListOfLists.append(intensity[i*len(xSteps):(i+1)*len(xSteps)])
    
    #print('intensityListOfLists = ' + str(intensityListOfLists))
    figHM = go.Figure(data=go.Heatmap(x=xSteps,y=ySteps,z=intensityListOfLists,zmin=0,zmax=maxIntensity))
    figHM.update_layout(title=title, xaxis_title="X", yaxis_title="Y")
    figHM.update_layout(height=600, width=600)
    figHM.show()
    return True

def plotHeatMap3(resultStructure, z, title):
    tempRS = copy.deepcopy(resultStructure)
    xDims = tempRS['xDims']
    yDims = tempRS['yDims']
    zDims = tempRS['zDims']
    intensity = tempRS['intensity']
    xMax = int(max(xDims))
    #print('----------------------')
    #print(xDims)
    #print('----------------------')
    #print(yDims)
    #print('----------------------')
    xMin = int(min(xDims))
    yMax = int(max(yDims))
    yMin = int(min(yDims))
    #print(xMax)
    #print(xMin)
    #print(yMax)
    #print(yMin)
    step = 5#int(xDims[1] - xDims[0])
    xSteps = list(range(xMin, xMax+step, step))
    ySteps = list(range(yMin, yMax+step, step))
    #print('----------------------')
    #print(xSteps)
    #print('----------------------')
    #print(ySteps)
    maxIntensity = max(intensity)   # to scale colourbar on heatmaps
    
    # run a loop to leave only what is wanted (ie z=z)
    n=len(xDims)
    for i in range (n-1,-1,-1):     # needs to stop at 0 so range is to -1. Test it.
        if not(zDims[i]==z):
            del xDims[i]
            del yDims[i]
            del zDims[i]
            del intensity[i]


    intensityListOfLists=[]
    
    for i in range (0,len(ySteps)):
        intensityListOfLists.append(intensity[i*len(xSteps):(i+1)*len(xSteps)])
    print ('there are ' + str(len(xSteps)) + ' x steps and ' + str(len(ySteps)) + ' ysteps')
    
    # matplotlib needs a (reshaped) 2D array from numpy for the z data
    zzz = np.array(zDims)
    print('numpy array has shape:')
    print(str(zzz.shape))
    zzz = np.reshape(zzz, (len(xSteps),len(ySteps)))
    print('numpy array has shape:')
    print(str(zzz.shape))
    fig, ax = plt.subplots()
    im = ax.imshow(np.array(zzz))

    # We want to show all ticks...
    ax.set_xticks(np.arange(len(xSteps)))
    ax.set_yticks(np.arange(len(ySteps)))
    # ... and label them with the respective list entries
    ax.set_xticklabels(xSteps)
    ax.set_yticklabels(ySteps)


    ax.set_title("Harvest of local farmers (in tons/year)")
    fig.tight_layout()
    plt.show(block=False)

    return True   

def plotModeCorrelation(intensityLOL, title):
    # plots a 2D correlation plot between all modes and all modes
    # returns the average cross correlation value (high is bad!)
    numModes = len(intensityLOL)
    xSteps = [i for i in range (1,numModes+1)]
    ySteps = xSteps # not a deep copy but we don't plan to change it
    
    # set up 2D array (list of lists) for results
    results = [[0 for i in range(0,numModes)] for j in range(0,numModes)]
    for x in range (0, numModes):
        for y in range (0,numModes):
            results[x][y] = calcOrthogonality(intensityLOL[x],intensityLOL[y])
            
    figHM = go.Figure(data=go.Heatmap(x=xSteps,y=ySteps,z=results,zmin=0,zmax=1))
    figHM.update_layout(title=title, xaxis_title="Mode", yaxis_title="Mode")
    figHM.update_layout(height=600, width=600)
    figHM.show()
    
    averageCrossCorrelation = sum(sum(results,[]))/numModes**2
    return averageCrossCorrelation
    
def withinCylindricalLoad(rad, height, xCentre,yCentre, x, y, z):
    # voxel is 'in range' ie within the load if:
    # mag is less than or equal to rad
    # AND z<=h
    # where
    # mag is ((x-xCentre)^2 + (y-yCentre)^2)^0.5
    returnVal = False
    if (z<=height):
        mag = ((x-xCentre)**2 + (y-yCentre)**2)**0.5
        if (mag<=rad):
            returnVal = True
    #print (returnVal)
    return returnVal     
    
    
def clipToCylindricalLoad(rad, height, xCentre, yCentre, resultStructure):
    #unpack the structure

    xDims = resultStructure['xDims']
    yDims = resultStructure['yDims']
    zDims = resultStructure['zDims']
    intensity = resultStructure['intensity']
    n=len(xDims)
    results =[]
    for i in range (n-1,-1,-1):     # needs to stop at 0 so range is to -1. Test it.
        if ((withinCylindricalLoad(rad, height, xCentre,yCentre, xDims[i], yDims[i], zDims[i]) == False)): # or (intensity[i]==0) ):
            del xDims[i]
            del yDims[i]
            del zDims[i]
            del intensity[i]
    resultStructure['xDims'] = xDims
    resultStructure['yDims'] = yDims
    resultStructure['zDims'] = zDims
    resultStructure['intensity'] = intensity
    return resultStructure
            
            
def clipToActiveArea(xMin,xMax,yMin,yMax,zMin,zMax, resultStructure):
    #unpack the structure
    xDims = resultStructure['xDims']
    yDims = resultStructure['yDims']
    zDims = resultStructure['zDims']
    intensity = resultStructure['intensity']
    
    n=len(xDims)
    results =[]
    for i in range (n-1,-1,-1):     # needs to stop at 0 so range is to -1. Test it.
        xInRange = (xMin <= xDims[i] <= xMax)
        yInRange = (yMin <= yDims[i] <= yMax)
        zInRange = (zMin <= zDims[i] <= zMax)
        if not(xInRange and yInRange and zInRange):
            del xDims[i]
            del yDims[i]
            del zDims[i]
            del intensity[i]
    resultStructure['xDims'] = xDims
    resultStructure['yDims'] = yDims
    resultStructure['zDims'] = zDims
    resultStructure['intensity'] = intensity
    return resultStructure

def deleteZeroIntensityPoints(intensity):
    n=len(intensity)
    for i in range (n-1,-1,-1):
        if intensity[i] == 0:
            del intensity[i]
    return intensity

def peakToAverage(intensity, deleteZeros):
    # delete zeros (only get absolute zero values in vacuum in the CST project output)
    # other sources of files can be different
    tempIntensity = copy.deepcopy(intensity)
    if deleteZeros:
        tempIntensity = deleteZeroIntensityPoints(tempIntensity)
    maxI = max(tempIntensity)
    averageI = sum(tempIntensity)/len(tempIntensity)
    return maxI/averageI

def NMSQE(intensity, deleteZeros):
    tempIntensity = copy.deepcopy(intensity)

    if deleteZeros:
        tempIntensity = deleteZeroIntensityPoints(tempIntensity)
    n = len(tempIntensity)
    
    averageIntensity = sum(tempIntensity)/len(tempIntensity)
    meanSquaredErrors = sum(list(map(lambda x: (x-averageIntensity)**2, tempIntensity)))
    meanSquaredValues = sum(list(map(lambda x: x**2, tempIntensity)))
    # meanSquaredErrors=sum(squaredErrors)/n
    # meanSquaredValues=sum(squaredValues)/n
    NMSQE = meanSquaredErrors/meanSquaredValues

    return NMSQE

def calcCoverage(intensity, deleteZeros):
    # this function works out, compared to the peak power point 
    # how 'full' on average all the points in the dataset are with power
    tempIntensity = copy.deepcopy(intensity)
    maxI = max(tempIntensity)
    tempIntensity = list(map(lambda x: x/maxI, tempIntensity))
    sumNormalisedIntensity = sum(tempIntensity)
    return sumNormalisedIntensity/len(tempIntensity)
    
# def calcPAR(Modes, Weights):
    # n = len(Modes)
    # listSum = [0 for i in range (0,n)]
    # for i in range (0,n):
        # nextList = list(map(lambda x: x*Weights[i], Modes[i]))
        # listSum = list(map(add, listSum, nextList))
    # PAR = max(listSum)/(sum(listSum)/len(Modes[0]))
    # return PAR
    
    
def reSquareDS(resultStructure):   
    # step one - is the result set square?
    # ie, all values from xmin-smax, ymin-ymax, zmin-zmax are populated?
    # not true if we've clipped to the load earlier
    # if not true, must re-square.
    
    xDims = resultStructure["xDims"]
    yDims = resultStructure["yDims"]
    zDims = resultStructure["zDims"]
    intensity = resultStructure["intensity"]
    
    sizeOfDS = len(intensity)
    stepSize = xDims[1]-xDims[0]
    #print('stepsize = ' +str(stepSize))
    stepSize = 5 #frigging it
    
    # for readability and later use, get max and min for all three axes in the dataset
    minX = min(xDims)
    maxX = max(xDims)
    minY = min(yDims)
    maxY = max(yDims)
    minZ = min(zDims)
    maxZ = max(zDims)
    
    #print(str(minX) + ',' + str(maxX) + ',' + str(minY) + ',' + str(maxY) + ',' +str(minZ) + ',' + str(maxZ))
    
    # work out how many steps in each axis
    numXSteps = (maxX-minX)/stepSize+1
    numYSteps = (maxY-minY)/stepSize+1
    numZSteps = (maxZ-minZ)/stepSize+1
    squareDSSize = numXSteps * numYSteps * numZSteps
   
    # print(str(numXSteps) + ',' + str(numYSteps) + ',' + str(numZSteps))
    # print('reSquareDS> size of DS = ' +str(sizeOfDS))
    # print('reSquareDS> step size = ' +str(stepSize))
    # print(str(numXSteps) + ',' + str(numYSteps) + ',' + str(numZSteps))
    
    #print('square result set needs: ' + str(squareDSSize) + ' elements')
    if not (sizeOfDS == squareDSSize):
        # build a new structure
        # populate it with the existing dataset
        newXDims = []
        newYDims = []
        newZDims = []
        newIntensity = []
        
        for z in range (int(minZ), int(maxZ+stepSize), int(stepSize)):
            for y in range (int(minY), int(maxY+stepSize), int(stepSize)):
                for x in range (int(minX), int(maxX+stepSize), int(stepSize)):
                    newXDims.append(x)
                    newYDims.append(y)
                    newZDims.append(z)
                    newIntensity.append(0)
                    if not len(xDims)==0:   
                        if xDims[0]==x and yDims[0]==y and zDims[0]==z:
                            newIntensity[len(newIntensity)-1] = intensity[0]
                            del xDims[0]
                            del yDims[0]
                            del zDims[0]
                            del intensity[0]

        resultStructure["xDims"] = newXDims
        resultStructure["yDims"] = newYDims 
        resultStructure["zDims"] = newZDims 
        resultStructure["intensity"] = newIntensity           
            
    return resultStructure
    
def plotPDF(fig, intensity, binSize, plotName, deleteZeros):
    tempIntensity = copy.deepcopy(intensity)
    #tempRS = resultStructure
    #print('plotting CCDF ---------------------')
    #tempRS = clipToCylindricalLoad(60, 100, 0, 150, tempRS)

    if deleteZeros:
        tempIntensity = deleteZeroIntensityPoints(tempIntensity)

    #print('before resquareds ' + str(len(intensity)))
    
    #resultStructure = reSquareDS(resultStructure)
    #intensity = resultStructure["intensity"]
    #print('after resquareds ' + str(len(intensity)))
    maxI = max(tempIntensity)
    #print ('maxI = ' + str(maxI))
    minI = min(tempIntensity)
    #print ('minI = ' + str(minI))
    #print('Max intensity for ' + plotName + ' is ' + str(maxI) + ' and Min is ' + str(minI))
    #print('binsize = ' + str(binSize))
    numBins = round((maxI-minI)/binSize)
    binSize = (maxI-minI)/numBins
    #print('number of bins = ' + str(numBins))
    #print('bin size = ' + str(binSize))
    
    # create X axis
    xBins = []
    binCounts = []
    for i in range (0,numBins):
        xBins.append(minI+(i+0.5)*binSize)
    
    #xBins = list(range(numBins)) # choose integer bin numbers
    for i in range (0,numBins):
        count = 0
        for eachPoint in tempIntensity:
            binL = minI + i*binSize
            binH = binL + binSize
            if (binL <= eachPoint <= binH):
                count+=1
        binCounts.append(count)
    #fig = px.scatter(x=xBins, y=binCounts)
    #fig.show()
    fig.add_trace(go.Scatter(x=xBins, y=binCounts, mode='lines', name=plotName))
    
    #print('------------------------')
    #print(xBins)
    #print('------------------------')
    #print('Total Bins = ' + str(sum(binCounts)))
    #print




    
def plotPARGraph(PARList1,PARList2, plotTitle, plotName1, plotName2):
    fig = go.Figure()
    passNumList = [i for i in range(0,len(PARList1))]
    
    plotTitle = plotTitle + ' : Best PAR = ' + str(min(PARList1))
    #re-create a bestPAR trajectory
        
    fig.add_trace(go.Scatter(x=passNumList, y=PARList1, mode='lines', name=plotName1))
    fig.add_trace(go.Scatter(x=passNumList, y=PARList2, mode='lines', name=plotName2))
    fig.update_layout(title=plotTitle, xaxis_title="Pass #", yaxis_title="PAR")
    fig.update_layout(height=600, width=1200)
    fig.show()
    return True
    
def plotPARGraph2D(PARList2DList, plotTitle, plotNameList):
    # structure dim 1 = row1 = species1..n PAR
    # structure dim 2 = row2..n = steps1..m
    fig = go.Figure()
    numSpecies = len(PARList2DList[0])
    numSteps = len(PARList2DList)
    print(numSpecies)
    print(numSteps)
    #Find minimum PAR of 2D list by reformatting into 1D list
    PARList1DList =[]
    for i in range(0,numSteps):
        PARList1DList+=PARList2DList[i]
    minPAR = min(PARList1DList)
    
    speciesPARTrack = [[0 for i in range(0,numSteps)] for j in range (0,numSpecies)] # sublists will contain each species PAR track
    
    for i in range (0,numSteps):
        for j in range(0,numSpecies):
            speciesPARTrack[j][i] = PARList2DList[i][j]
    
    
    plotTitle = (plotTitle + ' : Best PAR = ' + str(minPAR))
    passNumList = [i for i in range(0,numSteps)]
    for i in range (0,numSpecies): 
        
        fig.add_trace(go.Scatter(x=passNumList, y=speciesPARTrack[i], mode='lines', name=plotNameList[i]))

    fig.update_layout(title=plotTitle, xaxis_title="Pass #", yaxis_title="PAR")
    fig.update_layout(height=600, width=1200)
    fig.show()
    return True
    
def multModesByWeights(Modes, Weights):
    numModes = len(Modes)   # how many mode patterns in the list of lists
    modeLength = len(Modes[0])  # how long is each mode patterns
    if not len(Modes) == len(Weights):
        print('ERROR: there are ' +str(len(Modes)) + ' Modes and ' +str(len(Weights)) + ' Weights')
    #print('There are ' + str(numModes) + ' Modes')
    #print('Each of length ' + str(modeLength))
    #print('Weights list has length = ' + str(len(Weights)))
    sumOfWeights = sum(Weights) # needed to equalise intensity results for different cumulative weights
    if numModes != len(Weights):
        print('Num Modes and Len Weights do not match')
    
    result = [0 for i in range(modeLength)]
    for i in range (0,numModes):
        result = list(map(add, result, list(map(lambda x: x*Weights[i]/sumOfWeights, Modes[i]))))
    return result
    
def deltaT(remoteWeight, remotePAR, currentWeight, currentPAR):
    # note, returning a positive value indicates we want to drift TOWARDS remote point
    return currentPAR-remotePAR

def deltaRange(remoteWeight, remotePAR, currentWeight, currentPAR):
    rSquared = 0
    for i in range (0,len(remoteWeight)):   
        rSquared += (remoteWeight[i]-currentWeight[i])**2
    return rSquared**0.5
        
def directionOfTravel(remoteWeight, remotePAR, currentWeight, currentPAR):
    # returns a unit magnitude vector in the direction of the remote weight
    # add (some of) this vector IF WE WANT TO MOVE TOWARDS THAT POINT
    # otherwise, subtract 
    directionVector = list(map(lambda x,y : x-y, remoteWeight,currentWeight))
    # magSquared = 0
    # for i in range (0,len(directionVector)):
        # magSquared += directionVector[i]**2
    # mag = magSquared**0.5
    # if mag>0:
        # normalisedDirectionVector = list(map(lambda x: x/mag, directionVector))
    # else:
        # normalisedDirectionVector = [0 for i in range(0,len(remoteWeight))]
    # return normalisedDirectionVector
    return directionVector
    
def deleteDuplicates(speciesList):
    indexesToDelete = []
    for i in range (0, len(speciesList)):
        for j in range (i+1,len(speciesList)):
            if speciesList[i]==speciesList[j]:
                indexesToDelete.append(j)
    
    print('species to delete = ' + str(indexesToDelete))
                
        # compare each species only with those above it 
        # record a list of items to delete ... always listing the top one.
        
    
    return speciesList
    
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