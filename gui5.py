import tkinter as tk
from tkinter import *
from tkinter import filedialog
import os
import re
import time
import plotly.graph_objects as go
from operator import add, mul
import random
import csv
import copy
from commonFunctions import clipToActiveArea
from commonFunctions import clipToCylindricalLoad
from commonFunctions import peakToAverage
from commonFunctions import heuristicSwitch
from commonFunctions import NMSQE
from commonFunctions import plotPDF
from commonFunctions import plotHeatMap
from commonFunctions import plotHeatMap2
from commonFunctions import plotHeatMap3
from commonFunctions import multModesByWeights
from commonFunctions import plotModeCorrelation
from commonFunctions import calcCoverage
from commonFunctions import readProcessFile
from orthogonality import calcOrthogonality
from randomDescent import manyRandoms
from gradientDescent import gradientDescent
from gradientDescent2 import gradientDescent2
from geneticAlgorithm import geneticAlgorithm
from geneticAlgorithm2 import geneticAlgorithm2
from geneticAlgorithm3 import geneticAlgorithm3
from geneticAlgorithm4 import geneticAlgorithm4
from sequentialDescent import sequentialDescent
from swarmDescent import swarmDescent
from checkOptimum import checkOptimum
from checkTrack import checkTrack

def runMe():
    print('Hiya')
    print(algoRadioButtonVar.get())
    
def sayHi():
    selectedDirectory.delete(1.0, END)
    selectedDirectory.insert(END, "Hi button pressed")
    print(stringVar)

def selectWorkingDirectory(): 
    global fileList
    global path
    path = filedialog.askdirectory()
    print('PATH = ' + str(path))
    selectedDirectory.delete('1.0','2.0')
    selectedDirectory.insert(END, str(path)+'\r\n')
    fileList = os.listdir(path)
        
    filesInDirectory.delete(1.0, END)
    for i in range (0,len(fileList)):
        filesInDirectory.insert(END, str(fileList[i]) + '\r\n')
        
def loadFiles():
    global fileList
    global path
    global deleteZeros
    global binSize
    global allModes
    global tempRS
    global clipToCylinderLoad
    global clipToRectangularLoad
    global allAverageIntensities
    
    if fileList == []:
        print('File List Empty, please select working directory')
    else:
        # set up figure for PDF plots
        fig = go.Figure()   
        fig.update_layout(title="Single Modes, dataset = : " + str(path), xaxis_title="Amplitude (W/m^2)", yaxis_title="PDF (not normalised)")
        numFiles = len(fileList)
        
        allPARs = []
        allNMSQEs=[]
        allAverageIntensities=[]
        allModes=[]
        
        # start reading files in
        numFiles = len(fileList)
        for i in range (0,numFiles):
            fileName = path + '/' + fileList[i]
            resultStructure = readProcessFile(fileName)
            if clipToCylinderLoad:
                #resultStructure[i] = clipToActiveArea(-60,60,90,210,0,100, resultStructureAll[i])
                resultStructure = clipToCylindricalLoad(60, 100, 0, 150, resultStructure)    
            if clipToRectangularLoad:
                resultStructure = clipToActiveArea(-50,50,100,200,0,50, resultStructure) 
            #avIntensity = list(map(add, avIntensity, resultStructure["intensity"]))
            if i==0:
                # save one full structure for later
                tempRS = copy.deepcopy(resultStructure)
                tempRS["intensity"]=[]
            # save all intensity parts
            intensity = resultStructure["intensity"]
        
            currentPAR = peakToAverage(intensity, deleteZeros)
            currentNMSQE = NMSQE(intensity, deleteZeros)
            currentCoverage = calcCoverage(intensity, deleteZeros)
            allPARs.append(currentPAR)
            allNMSQEs.append(currentNMSQE)
        
            plotPDF(fig, intensity, binSize, fileList[i] + ' PAR = ' + str(currentPAR), deleteZeros)
            averageI = sum(intensity)/len(intensity)
            allAverageIntensities.append(averageI)  # store for use in inversely weighted algorithm.
            #plotHeatMap(resultStructure, 50, fileName + ' PAR = ' + str(currentPAR))
            print(str(fileName) + '\tAverage Intensity= \t' + str(averageI) + '\tPAR=\t' + str(currentPAR) + '\tCoverage=\t ' + str(currentCoverage) + '\tNMSQE=\t' +str(currentNMSQE))
            allModes.append(intensity) # save all intensity data for algorithms

        # display the figure with all PDF's
        fig.update_layout(height=600, width=1200)
        fig.show()
        print('Max PAR = ' + str(max(allPARs)) + '\t& Min PAR = ' + str(min(allPARs)) + '\t& Average = ' +str(sum(allPARs)/len(allPARs)))
        print('Max NMSQE = ' + str(max(allNMSQEs)) + '\t& Min NMSQE = ' + str(min(allNMSQEs)) + '\t& Average = ' +str(sum(allNMSQEs)/len(allNMSQEs)))

def runAlgorithm():
    global runFixed
    global runSingle
    global runEven
    global runEvenIntensity
    global runRandomAlgo
    global runGradientDescentAlgo
    global runGradientDescentAlgo2
    global runGeneticAlgo
    global runGeneticAlgo2
    global runGeneticAlgo3
    global runGeneticAlgo4
    global runSequentialDescent
    global sixZedsForHeatmaps
    global tempRS
    
    global allModes
    global binSize
    global deleteZeros
    
    bestWeights = []
    print('there are ' + str(len(allModes)) + ' with ' + str(len(allModes[0])) + 'entries in the first one')
    
    val = algoRadioButtonVar.get()
    if allModes ==[]:
        print('Please load data before running an algorithm')
    else:

        if val == runFixed:
            fixedWeightsString = fixedWeightsStringVar.get()
            bestWeights = stringToList(fixedWeightsString)
            print(len(bestWeights))
            algoName = 'runFixed'
            
        if val == runSingle:
            singleMode = int(singleModeStringVar.get())
            bestWeights = [0 for i in range (0,len(allModes))]
            print(len(allModes))
            bestWeights[singleMode] = 1
            print(len(bestWeights))
            algoName = 'runSingle'
            
        if val == runEven:
            bestWeights = [1 for i in range (0,len(allModes))]
            algoName = 'runEven'
            
        if val == runEvenIntensity:
            bestWeights = list(map(lambda x: 100/x, allAverageIntensities))
            algoName = 'runEvenIntensity'
            
        if val == runRandomAlgo:
            numRemixes = int(numRandoms.get())
            heuristic = heuristicRadioBtnVar.get()
            bestWeights = manyRandoms(allModes, numRemixes, deleteZeros, heuristic)
            algoName = 'runRandomAlgo'

        if val == runGradientDescentAlgo:
            numRemixes = int(numGradientDescents.get())
            heuristic = heuristicRadioBtnVar.get()
            bestWeights = [1 for i in range (0,len(allModes))]
            bestWeights = gradientDescent(allModes, bestWeights, numRemixes, deleteZeros, heuristic, False)
            algoName = 'runGradientDescentAlgo'
            
        if val == runGradientDescentAlgo2:
            heuristic = heuristicRadioBtnVar.get()
            bestWeights = gradientDescent2(allModes, deleteZeros, heuristic)
            algoName = 'runGradientDescentAlgo2'

        if val == runGeneticAlgo:
            numSpecies = int(numSpeciesGA.get())
            numPasses = int(numPassesGA.get())
            heuristic = heuristicRadioBtnVar.get()
            bestWeights = geneticAlgorithm(allModes, numSpecies, numPasses, deleteZeros, heuristic)
            algoName = 'runGeneticAlgo'        
            
        if val == runGeneticAlgo2:
            numSpecies = int(numSpeciesGA2.get())
            numMutations = int(numMutationsGA2.get())
            heuristic = heuristicRadioBtnVar.get()
            bestWeights = geneticAlgorithm2(allModes, numSpecies, numMutations, deleteZeros, heuristic)
            algoName = 'runGeneticAlgo2'
            
        if val == runGeneticAlgo3:
            numSpecies = int(numSpeciesGA3.get())
            numMutations = int(numMutationsGA3.get())
            heuristic = heuristicRadioBtnVar.get()
            bestWeights = geneticAlgorithm3(allModes, numSpecies, numMutations, deleteZeros, heuristic)
            algoName = 'runGeneticAlgo3'
            
        if val == runGeneticAlgo4:
            numSpecies = int(numSpeciesGA4.get())
            numMutations = int(numMutationsGA4.get())
            heuristic = heuristicRadioBtnVar.get()
            bestWeights = geneticAlgorithm4(allModes, numSpecies, numMutations, deleteZeros, heuristic)
            algoName = 'runGeneticAlgo4'
            
        if val == runSequentialDescent:
            heuristic = heuristicRadioBtnVar.get()
            bestWeights = sequentialDescent(allModes, deleteZeros, heuristic)
            algoName = 'runSequentialDescent'
        
        if val == runSwarmDescent:
            heuristic = heuristicRadioBtnVar.get()
            numSpecies = int(numSpeciesSwarm.get())
            bestWeights = swarmDescent(allModes, numSpecies, deleteZeros, heuristic, False)
            algoName = 'runSwarmDescent'
            
        algoIntensity = multModesByWeights(allModes, bestWeights)  
        print('algo intensity has len = ' +str(len(algoIntensity)))
        averageIntensityResult1 = sum(algoIntensity)/len(algoIntensity)
        bestPAR = peakToAverage(algoIntensity, deleteZeros)
        bestNMSQE = NMSQE(algoIntensity, deleteZeros)
        
        # OUTPUT DATASET AND ALGORTIHM USED TO CMD AND GUI
        text='Dataset = ' +str(path) + ' and algo = ' + str(algoName)
        print(text)
        textBoxKeyResults.delete(1.0,END)
        textBoxKeyResults.insert(END, text + '\r\n')
        
        # OUTPUT WEIGHTS TO CMD AND GUI
        text='Final Weights = ' + str(bestWeights)
        print(text)
        textBoxFinalWeights.delete(1.0,END)
        textBoxFinalWeights.insert(END, text + '\r\n')
        
        # OUTPUT KEY RESULTS TO CMD AND GUI
        text = 'FINAL BEST PAR = ' + str(bestPAR) + ' :Final NMSQE = ' + str(bestNMSQE) + ' : Average Intensity = ' + str(averageIntensityResult1)
        print(text)
        textBoxKeyResults.insert(END, text + '\r\n')


        
        # print ccdf of best solution
        fig = go.Figure()   # set up figure
        fig.update_layout(title='Best Result - PAR = ' +str(bestPAR), xaxis_title="Amplitude (W/m^2)", yaxis_title="PDF (not normalised)")
        plotPDF(fig, algoIntensity, binSize, 'Result', deleteZeros)
        fig.update_layout(height=600, width=1200)
        fig.show()
        
        tempRS["intensity"] = algoIntensity
        # plot heatmaps of best solution
        plotHeatMap2(copy.deepcopy(tempRS), 'heatmaps', sixZedsForHeatmaps)

        # if runCheckOptimum:
            # checkOptimum(allModes, bestWeights, 100)
        
        # if runCheckTrack:
            # Weight1 = [2.935581813,3.676411805,4.276659359,0.085484926,0,1.178258916,0,0.077911611,1.877505842,0.763454556,3.064183604]
            # Weight2 = [15.90292697,82.76297594,0,0,5.48062642,2.916650988,0.011574903,0,8.809910201,11.63412525,17.81278896]
            # checkTrack(allModes, Weight1, Weight2, 20, heuristic)
    
def manageCheckBtnDeleteZeros():
    global deleteZeros
    
    val = varCheckBtnDeleteZeros.get()
    if val ==0:
        deleteZeros = False
    else:
        deleteZeros = True
    print('Delete Zeros = ' + str(deleteZeros))
    
def manageCheckBtnClipToCylinder():
    global clipToCylinderLoad
    
    val = varCheckBtnClipToCylinder.get()
    if val ==0:
        clipToCylinderLoad = False
    else:
        clipToCylinderLoad = True
    print('Clip To Cylindrical Load = ' + str(clipToCylinderLoad))

def manageCheckBtnClipToRectangular():
    global clipToRectangularLoad
    
    val = varCheckBtnClipToRectangular.get()
    if val ==0:
        clipToRectangularLoad = False
    else:
        clipToRectangularLoad = True
    print('Clip To Rectangular Load = ' + str(clipToRectangularLoad))
    
def printAlgo():
    selection = var.get()
    print(selection)

def stringToList(inputString):
    if inputString.find(',')>=0:
        return list(map(float, inputString.split(',')))
    else:
        return list(map(float, inputString.split()))
    
# Var initialisation
fileList = []
path = ''
clipToCylinderLoad = False
clipToRectangularLoad = False
allAverageIntensities = []
allModes = []
deleteZeros = False
binSize=50
tempRS = None
allAverageIntensities = []



#GUI
root=tk.Tk()
root.geometry('1000x1000')
variable=tk.StringVar()
varCheckBtnDeleteZeros = tk.IntVar()
algoRadioButtonVar=tk.IntVar()
varCheckBtnClipToCylinder = tk.IntVar()
varCheckBtnClipToRectangular = tk.IntVar()
fixedWeightsStringVar = tk.StringVar()
singleModeStringVar = tk.StringVar()
numRandoms = tk.StringVar()
numGradientDescents = tk.StringVar()
numSpeciesGA =tk.StringVar()
numPassesGA =tk.StringVar()
numSpeciesGA2 =tk.StringVar()
numMutationsGA2 =tk.StringVar()
numSpeciesGA3 =tk.StringVar()
numMutationsGA3 =tk.StringVar()
numSpeciesGA4 =tk.StringVar()
numMutationsGA4 =tk.StringVar()
numSpeciesSwarm =tk.StringVar()
heuristicRadioBtnVar = tk.IntVar()
sixZedsForHeatmaps = [100,90,75,50,25,10]

(0)
# TITLE LABEL
r=0
c=0
full=5
title = tk.Label(root, font="Times 18 bold", text="Electromagnetic Heating Pattern Optimisation GUI")
title.grid(row=r,column=c,columnspan=full)
r+=1
subtitle = tk.Label(root, font="Times 12", text="Software Engineering MSc Dissertation, Liverpool University (Online Program), Robin Wesson")
subtitle.grid(row=r,column=c,columnspan=full)
        
# Select Directory BUTTON
r+=2
c=0
subSectionHeading1 = tk.Label(root, font="Times 12", text="Main Program Controls")
subSectionHeading1.grid(row=r,column=c,columnspan=full, sticky='W')
r+=1
stringVar = "Select Results Directory"
selDirBtn = tk.Button(root)
selDirBtn["text"] = "Select Directory"
selDirBtn["command"] = command=selectWorkingDirectory
selDirBtn.grid(row=r,column=c)
        
# LOAD FILES BUTTON
c+=1
loadFiles = tk.Button(root, text="Load Files", fg="black", command=loadFiles)
loadFiles.grid(row=r,column=c)

# RUN ALGO BUTTON
c+=1
runAlgoBtn = tk.Button(root, text="Run Algorithm", fg="black", command=runAlgorithm)
runAlgoBtn.grid(row=r,column=c)      

# QUIT BUTTON
c+=1
quitBtn = tk.Button(root, text="QUIT", fg="red", command=root.destroy)
quitBtn.grid(row=r, column=c)

# Misc Boolean Settings (Checkboxes)
r+=2
c=0
subSectionHeading2 = tk.Label(root, font="Times 12", text="Miscellaneous Settings")
subSectionHeading2.grid(row=r,column=c,columnspan=full, sticky='W')
r+=1
c=0
checkBtnDeleteZeros = tk.Checkbutton(root, text="Delete Zeros?", variable=varCheckBtnDeleteZeros, command = manageCheckBtnDeleteZeros)
checkBtnDeleteZeros.grid(row=r, column=c)

c+=1
checkBtnClipToCylinder = tk.Checkbutton(root, text="Clip To Cylindrical Load?", variable=varCheckBtnClipToCylinder, command = manageCheckBtnClipToCylinder)
checkBtnClipToCylinder.grid(row=r, column=c)

c+=1
checkBtnClipToRectangular = tk.Checkbutton(root, text="Clip To Rectangular Load?", variable=varCheckBtnClipToRectangular, command = manageCheckBtnClipToRectangular)
checkBtnClipToRectangular.grid(row=r, column=c)


#Heuristic Radio buttons
# ALGORITHM RUN FIXED WEIGTHS
r+=2
c=0
subSectionHeading3 = tk.Label(root, font="Times 12", text="Select Quality Metric")
subSectionHeading3.grid(row=r,column=c,columnspan=full, sticky='W')

r+=1
c=0
heuristicRadioBtn1 = tk.Radiobutton(root, text="NMSQE", variable=heuristicRadioBtnVar, value=0, anchor=tk.W)
heuristicRadioBtn1.grid(row=r, column=c)

c+=1
heuristicRadioBtn2 = tk.Radiobutton(root, text="PAR", variable=heuristicRadioBtnVar, value=1, anchor=tk.W)
heuristicRadioBtn2.grid(row=r, column=c)


# END 
   


# RADIO BUTTON ALGORITHM SELECTION BOXES

# set up variable meanings for algorithm selection
runFixed = 1
runSingle = 2
runEven = 3
runEvenIntensity = 4
runRandomAlgo = 5
runGradientDescentAlgo = 6
runGradientDescentAlgo2 = 7  # self terminating
runGeneticAlgo = 8
runGeneticAlgo2 = 9
runGeneticAlgo3 = 10
runGeneticAlgo4 = 11
runSequentialDescent = 12
runSwarmDescent = 13


# RADIO BUTTONS FOR ALGORTIHM SELECTION
# (PLUS Extra Settings)

r+=2
c=0
subSectionHeading3 = tk.Label(root, font="Times 12", text="Training Algorithm Selection and Settings")
subSectionHeading3.grid(row=r,column=c,columnspan=full, sticky='W')

# ALGORITHM RUN FIXED WEIGHTS
r+=1
c=0
rB1 = tk.Radiobutton(root, text="runFixed", variable=algoRadioButtonVar, value=runFixed)
rB1.grid(row=r, column=c, sticky="W")
c+=1
textBoxFixedWeights = tk.Entry(root, text = '0', textvariable=fixedWeightsStringVar)
textBoxFixedWeights.grid(row=r, column=c, sticky = 'W')
c+=1
labelFixedWeights = tk.Label(root, text="(Comma or whitespace separated list of weights)")
labelFixedWeights.grid(row=r, column=c, sticky = 'W')
# END 
   
# ALGORITHM RUN SINGLE MODE   
r+=1
c=0
rB2 = tk.Radiobutton(root, text="runSingle", variable=algoRadioButtonVar, value=runSingle)
rB2.grid(row=r, column=c, sticky="W")
c+=1
textBoxSingleMode = tk.Entry(root, text = '0', textvariable=singleModeStringVar)
textBoxSingleMode.grid(row=r, column=c, sticky = 'W')
c+=1
labelSingleMode = tk.Label(root, text="(Index of Mode)")
labelSingleMode.grid(row=r, column=c, sticky = 'W')
# END 
   
# ALGORITHM RUN EVENLY WEIGHTED
r+=1
c=0
rB3 = tk.Radiobutton(root, text="runEven", variable=algoRadioButtonVar, value=runEven)
rB3.grid(row=r, column=c, sticky="W")
# END 
   
# ALGORITHM RUN WEIGHTED FOR EVEN INTENSITY 
r+=1
rB3 = tk.Radiobutton(root, text="runEvenIntensity", variable=algoRadioButtonVar, value=runEvenIntensity)
rB3.grid(row=r, column=c, sticky="W")
# END 
   
# ALGORITHM RUN  MANY RANDOMS
r+=1
rB3 = tk.Radiobutton(root, text="runRandomAlgo", variable=algoRadioButtonVar, value=runRandomAlgo)
rB3.grid(row=r, column=c, sticky="W")
c+=1
textBoxNumRandoms = tk.Entry(root, text = '0', textvariable=numRandoms)
textBoxNumRandoms.grid(row=r, column=c, sticky="W")
c+=1
labelNumRandoms = tk.Label(root, text="(Number of Passes)")
labelNumRandoms.grid(row=r, column=c, sticky = 'W')
# END 
   
# ALGORITHM RUN GRADIENT DESCENT 
r+=1
c=0
rB3 = tk.Radiobutton(root, text="runGradientDescentAlgo", variable=algoRadioButtonVar, value=runGradientDescentAlgo)
rB3.grid(row=r, column=c, sticky="W")
c+=1
textBoxNumGradientDescent = tk.Entry(root, text = '0', textvariable=numGradientDescents)
textBoxNumGradientDescent.grid(row=r, column=c, sticky="W")
c+=1
labelNumGDPasses = tk.Label(root, text="(Number of Passes)")
labelNumGDPasses.grid(row=r, column=c, sticky = 'W')
# END 
   
# ALGORITHM RUN GRADIENT DESCENT 2 
r+=1
c=0
rB3 = tk.Radiobutton(root, text="runGradientDescentAlgo2", variable=algoRadioButtonVar, value=runGradientDescentAlgo2)
rB3.grid(row=r, column=c, sticky="W")

# END 
   
# ALGORITHM RUN GENETIC ALGORITHM
r+=1
c=0
rB3 = tk.Radiobutton(root, text="runGeneticAlgo", variable=algoRadioButtonVar, value=runGeneticAlgo)
rB3.grid(row=r, column=c, sticky="W")
c+=1
textBoxNumSpeciesGA = tk.Entry(root, text = '0', textvariable=numSpeciesGA)
textBoxNumSpeciesGA.grid(row=r, column=c, sticky="W")
c+=1
labelNumSpeciesGA = tk.Label(root, text="(Number of Species)")
labelNumSpeciesGA.grid(row=r, column=c, sticky = 'W')
c+=1
textBoxNumPassesGA = tk.Entry(root, text = '0', textvariable=numPassesGA)
textBoxNumPassesGA.grid(row=r, column=c, sticky="W")
c+=1
labelNumPassesGA = tk.Label(root, text="(Number of Passes)")
labelNumPassesGA.grid(row=r, column=c, sticky = 'W')
# END 
   
# ALGORITHM RUN GENETIC ALGORITHM V2
r+=1
c=0
rB3 = tk.Radiobutton(root, text="runGeneticAlgo2", variable=algoRadioButtonVar, value=runGeneticAlgo2)
rB3.grid(row=r, column=c, sticky="W")
c+=1
textBoxNumSpeciesGA2 = tk.Entry(root, text = '0', textvariable=numSpeciesGA2)
textBoxNumSpeciesGA2.grid(row=r, column=c, sticky="W")
c+=1
labelNumSpeciesGA2 = tk.Label(root, text="(Number of Species)")
labelNumSpeciesGA2.grid(row=r, column=c, sticky = 'W')
c+=1
textBoxNumMutationsGA2 = tk.Entry(root, text = '0', textvariable=numMutationsGA2)
textBoxNumMutationsGA2.grid(row=r, column=c, sticky="W")
c+=1
labelNumMutationsGA2 = tk.Label(root, text="(Number of Mutations)")
labelNumMutationsGA2.grid(row=r, column=c, sticky = 'W')
# END 
   
# ALGORITHM RUN GENETIC ALGORITHM V3
r+=1
c=0
rB3 = tk.Radiobutton(root, text="runGeneticAlgo3", variable=algoRadioButtonVar, value=runGeneticAlgo3)
rB3.grid(row=r, column=c, sticky="W")
c+=1
textBoxNumSpeciesGA3 = tk.Entry(root, text = '0', textvariable=numSpeciesGA3)
textBoxNumSpeciesGA3.grid(row=r, column=c, sticky="W")
c+=1
labelNumSpeciesGA3 = tk.Label(root, text="(Number of Species)")
labelNumSpeciesGA3.grid(row=r, column=c, sticky = 'W')
c+=1
textBoxNumMutationsGA3 = tk.Entry(root, text = '0', textvariable=numMutationsGA3)
textBoxNumMutationsGA3.grid(row=r, column=c, sticky="W")
c+=1
labelNumMutationsGA3 = tk.Label(root, text="(Number of Mutations)")
labelNumMutationsGA3.grid(row=r, column=c, sticky = 'W')
# END 
   
# ALGORITHM RUN GENETIC ALGORITHM V4
r+=1
c=0
rB3 = tk.Radiobutton(root, text="runGeneticAlgo4", variable=algoRadioButtonVar, value=runGeneticAlgo4)
rB3.grid(row=r, column=c, sticky="W")
c+=1
textBoxNumSpeciesGA4 = tk.Entry(root, text = '0', textvariable=numSpeciesGA4)
textBoxNumSpeciesGA4.grid(row=r, column=c, sticky="W")
c+=1
labelNumSpeciesGA4 = tk.Label(root, text="(Number of Species)")
labelNumSpeciesGA4.grid(row=r, column=c, sticky = 'W')
c+=1
textBoxNumMutationsGA4 = tk.Entry(root, text = '0', textvariable=numMutationsGA4)
textBoxNumMutationsGA4.grid(row=r, column=c, sticky="W")
c+=1
labelNumMutationsGA4 = tk.Label(root, text="(Number of Mutations)")
labelNumMutationsGA4.grid(row=r, column=c, sticky = 'W')
# END 
   
# ALGORITHM RUN SEQUENTIAL DESCENT  
r+=1
c=0
rB3 = tk.Radiobutton(root, text="runSequentialDescent", variable=algoRadioButtonVar, value=runSequentialDescent)
rB3.grid(row=r, column=c, sticky="W")


# ALGORITHM RUN SWARM DESCENT  
r+=1
c=0
rB3 = tk.Radiobutton(root, text="runSwarmDescent", variable=algoRadioButtonVar, value=runSwarmDescent)
rB3.grid(row=r, column=c, sticky="W")
c+=1
textBoxNumSpeciesSwarm = tk.Entry(root, text = '0', textvariable=numSpeciesSwarm)
textBoxNumSpeciesSwarm.grid(row=r, column=c, sticky="W")
c+=1
labelNumSpeciesSwarm = tk.Label(root, text="(Number of Species)")
labelNumSpeciesSwarm.grid(row=r, column=c, sticky = 'W')
# END    






# TEXT OUTPUT BOXES
c=0
r+=2
labelSelectedDirectory = tk.Label(root, text="Selected Directory")
labelSelectedDirectory.grid(row=r, column=c, sticky="W")
r+=1
selectedDirectory = tk.Text(root, height=3,width=70)
selectedDirectory.grid(row=r, column=c, columnspan=full, )

r+=1
labelFilesInDirectory = tk.Label(root, text="Files In Directory")
labelFilesInDirectory.grid(row=r, column=c, sticky="W")
r+=1
# scroll = Scrollbar(root)
# scroll.grid(row = r, column=c)
# c+=1
filesInDirectory = tk.Text(root, height=10,width=70)
filesInDirectory.grid(row=r, column=c, columnspan=full)

r+=1
labelKeyResults = tk.Label(root, text="Key Results")
labelKeyResults.grid(row=r, column=c, sticky="W")
r+=1
# scroll = Scrollbar(root)
# scroll.grid(row = r, column=c)
# c+=1
textBoxKeyResults = tk.Text(root, height=4,width=70)
textBoxKeyResults.grid(row=r, column=c, columnspan=full)

r+=1
labelFinalWeights = tk.Label(root, text="Final Weights")
labelFinalWeights.grid(row=r, column=c, sticky="W")
r+=1
# scroll = Scrollbar(root)
# scroll.grid(row = r, column=c)
# c+=1
textBoxFinalWeights = tk.Text(root, height=2,width=70)
textBoxFinalWeights.grid(row=r, column=c, columnspan=full)

root.mainloop()

