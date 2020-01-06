# -*- coding: utf-8 -*-
"""
Created on Sun Jan  5 21:22:36 2020

@author: 10624
"""

import seaborn as sns

##Earthquake Failure Simulation
#Input: System subjected Earthquake, Flow of the System, Earthquake epicenter(Lon, Lat), Earthquake Intensity
#Output: The node failure sequnce when the whole system reaches a stable state
def FailureSimu(System, Flow, DisrupLon, DisrupLat, Intensity, Dist_Coffi):
    Flow.PostProcess(System)
    Earthquake = EarthquakeSys(System, DisrupLon, DisrupLat, Intensity)
    
    Earthquake.DistanceCalculation()
    Earthquake.NodeFailProbCalculation()
    Earthquake.MCFailureSimulation()
    Earthquake.GeoDepenFailProb(Dist_Coffi)
    Earthquake.GeoMCSimulation()
    
    while(1):
        Earthquake.AdjUpdate()
        Earthquake.FlowUpdate()
        Earthquake.CascadFail()
        Earthquake.Performance(AnalType)
        if((Earthquake.NodeFailIndex[-1] == Earthquake.NodeFailIndex[-2]) or (len(Water.Performance) == 20)):
            break    
    
    return Earthquake.NodeFailIndex[-1]

def FailCount(System, NodeFailList, NFailCount, NNFailCount):
    for node in NodeFailList:
        NFailCount[node] += 1
    
    for i in range(System.NodeNum):
        for j in range(i, System.NodeNum):
            if(i in NodeFailList and j in NodeFailList):
                if(i == j):
                    NNFailCount[i, j] += 1
                else:
                    NNFailCount[i, j] += 1
                    NNFailCount[j, i] += 1
    
    return NFailCount, NNFailCount
    

def FailCondProb(System, NFailCount, NNFailCount, ConFailProb):
    for i in range(System.NodeNum):
        for j in range(System.NodeNum):
            ConFailProb[i, j] = NNFailCount[i, j]/NFailCount[i]
    
    return ConFailProb

def DistConProb(ConFailProb, Dist):
    List_ConProb = np.reshape(len(ConFailProb)**2)
    List_Dist = np.reshape(len(Dist)**2)
    
    return 

#Parameter Specification
T = 100 #Simulation times

#Information of the Earthquake Disruption
DisrupLon = -90
DisrupLat = 30
DisrupInt = 5

#The way to calculate the performance
AnalType = 'SingleSum'
Simu_Time = 0
Dist_Coffi = 10000

NFailCount = np.zeros(Shelby_County.NodeNum)
NNFailCount = np.zeros([Shelby_County.NodeNum, Shelby_County.NodeNum])
ConFailProb = np.zeros([Shelby_County.NodeNum, Shelby_County.NodeNum])

for t in range(T):
    NodeFailList = FailureSimu(Shelby_County, Shelby_County_Flow, DisrupLon, DisrupLat, DisrupInt, Dist_Coffi)
    
    NFailCount, NNFailCount = FailCount(Shelby_County, NodeFailList, NFailCount, NNFailCount)
    
    print("Iteration {}".format(t))
    
ConFailProb = FailCondProb(Shelby_County, NFailCount, NNFailCount, ConFailProb)

##Heatmap          
ConProb_Heatmap = sns.heatmap(ConFailProb)
#Dist_Heatmap = sns.heatmap(Shelby_County.Dist)

##Relationship between distance and Conditional Probability
List_ConProb = np.reshape(len(ConFailProb)**2)
List_Dist = np.reshape(len(Shelby_County.Dist)**2)




    
    