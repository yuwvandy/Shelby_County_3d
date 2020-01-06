# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 16:56:24 2019

@author: wany105
"""
Shelby_County_Flow.PostProcess(Shelby_County)
Shelby_County.SysVisual(Normalize(Shelby_County.FlowAdj[0]))


import numpy as np
from scipy.stats import norm
import copy
import matplotlib.pyplot as plt 
LowBound = 0.3
UpBound = 1.5

def PGAV(M_w, Distance):
    PGA = np.power(10, 3.79 + 0.298*(M_w - 6) - 0.0536*(M_w - 6)**2 - np.log10(Distance) - 0.00135*Distance)
    PGV = np.power(10, 2.04 + 0.422*(M_w - 6) - 0.0373*(M_w - 6)**2 - np.log10(Distance))
    return PGA, PGV

DisrupLon = -90
DisrupLat = 28
DisrupIntensity = 6


class EarthquakeSys:
    def __init__(self, Target, DisrupLon, DisrupLat, DisrupIntensity):##Type 1 - System, Type 2 - Single Network
        self.Target = Target
        self.DisrupX, self.DisrupY = Base(DisrupLon, DisrupLat)
        self.M_w = DisrupIntensity
        self.t = 0
        
        self.Target.TimeAdj = []
        self.Target.TimeAdj.append(copy.deepcopy(Shelby_County.Adj))
        
        ##Keep Track the whole process
        self.NodeFail = []
        self.NodeFailIndex = []
        
        for Network in self.Target.Networks:
            Network.SatisfyDemand = []
            Network.Performance = [1]            
        
        
    def DistanceCalculation(self):
        self.DisrupNodeDistance = np.sqrt((self.Target.CoorlistX - self.DisrupX)**2 + (self.Target.CoorlistY - self.DisrupY)**2)/1000 #Change the unit to km
        self.PGA, self.PGV = PGAV(self.M_w, self.DisrupNodeDistance)
    
    def NodeFailProbCalculation(self):
        self.NodeFailProb = np.zeros(self.Target.NodeNum)
        for Network in self.Target.Networks:
            self.NodeFailProb[Network.WholeNodeSeries[Network.SupplySeries]] = norm.cdf((np.log(self.PGA[Network.WholeNodeSeries[Network.SupplySeries]]) - Network.SLamb)/Network.SZeta)
            self.NodeFailProb[Network.WholeNodeSeries[Network.DemandSeries]] = norm.cdf((np.log(self.PGA[Network.WholeNodeSeries[Network.DemandSeries]]) - Network.DLamb)/Network.DZeta)
    
    def MCFailureSimulation(self):
        self.NodeFailRand = np.random.rand(len(self.NodeFailProb))
        
        #Failure due to Disruption
        self.NodeFail.append(self.NodeFailProb > self.NodeFailRand)
        self.NodeFailIndex.append(list(np.where(self.NodeFail[-1] == True)[0]))  
        self.NodeFailIndex1 = copy.deepcopy(self.NodeFailIndex)
    
    def GeoDepenFailProb(self): ##Only happens rightly after the earthquake
        self.GeoNodeFailProb = []
        for node1 in range(self.Target.NodeNum):
            Temp = 1
            if(node1 not in self.NodeFailIndex[-1]):
                for node2 in self.NodeFailIndex[-1]:
                    Temp *= np.exp(-1/10000*self.Target.Dist[node1, node2])
                self.GeoNodeFailProb.append([node1, 1 - Temp])
        
    def GeoMCSimulation(self):
        self.GeoNodeFail = []
        self.NodeFailRand = np.random.rand(len(self.GeoNodeFailProb))
        for i in range(len(self.GeoNodeFailProb)):
            if(self.GeoNodeFailProb[i][1] > self.NodeFailRand[i]):
                self.NodeFailIndex[-1].append(self.GeoNodeFailProb[i][0])
                
        
    def AdjUpdate(self):
        Adj = copy.deepcopy(self.Target.TimeAdj[-1])
        """
        gama = 0.8
        for i in self.NodeFailIndex[-1]:
            for j in range(self.Target.NodeNum):
                if(Adj[i][j] != gama):
                    Adj[i][j] = gama
                if(Adj[j][i] != gama):
                    Adj[j][i] = gama
        """
        
        Adj[self.NodeFailIndex[-1], :] = 0
        Adj[:, self.NodeFailIndex[-1]] = 0
        
        self.Target.TimeAdj.append(Adj)
        
        
    def FlowUpdate(self):
        Flow = self.Target.TimeAdj[-1]*self.Target.FlowAdj[-1]
        ##Gas Supply - Gas Demand
        Gas.SatisfyDemand.append([])
        for node in Gas.DemandSeries:
            Num = Gas.WholeNodeSeries[node]
            FlowInNode = np.sum(Flow[Gas.WholeNodeSeries[Gas.SupplySeries], Num]) + np.sum(Flow[Gas.WholeNodeSeries[Gas.DemandSeries], Num])
            if(math.floor(FlowInNode) >= math.floor(Gas.DemandValue[node - Gas.DemandSeries[0]])):
                FlowInNode = FlowInNode - Gas.DemandValue[node - Gas.DemandSeries[0]]
                Gas.SatisfyDemand[-1].append(Gas.DemandValue[node - Gas.DemandSeries[0]])
            else:
                Gas.SatisfyDemand[-1].append(0.25*FlowInNode)
                FlowInNode *= 0.75
            
            Ratio = Flow[Num, :]/np.sum(Flow[Num, :])
            Ratio[np.isnan(Ratio)] = 0
            if(np.sum(Flow[Num, :]) != 0):
                Flow[Num, :] = FlowInNode*InterGP.UnitRatio*Ratio 
                
        ##Gas Demand - Power Supply
        for node in Power.SupplySeries:
            Num = Power.WholeNodeSeries[node]
            FlowInNode1 = np.sum(Flow[Gas.WholeNodeSeries[Gas.DemandSeries], Num])
            FlowInNode2 = np.sum(Flow[Water.WholeNodeSeries[Water.DemandSeries], Num])
            FlowInNode = min(FlowInNode1, FlowInNode2*InterWP.UnitRatio)
            
            Ratio = Flow[Num, :]/np.sum(Flow[Num, :])
            Ratio[np.isnan(Ratio)] = 0
            if(np.sum(Flow[Num, :]) != 0):
                Flow[Num, :] = FlowInNode*Ratio
                
        Power.SatisfyDemand.append([])
        ##Power Supply - Power Demand
        for node in Power.DemandSeries:
            Num = Power.WholeNodeSeries[node]
            FlowInNode = np.sum(Flow[Power.WholeNodeSeries[Power.SupplySeries], Num]) + np.sum(Flow[Power.WholeNodeSeries[Power.DemandSeries], Num])
            
            if(math.floor(FlowInNode) >= math.floor(Power.DemandValue[node - Power.DemandSeries[0]])):
                FlowInNode = FlowInNode - Power.DemandValue[node - Power.DemandSeries[0]]
                Power.SatisfyDemand[-1].append(Power.DemandValue[node - Power.DemandSeries[0]])
            else:
                Power.SatisfyDemand[-1].append(0.25*FlowInNode)
                FlowInNode *= 0.75    
                
            Ratio = Flow[Num, :]/np.sum(Flow[Num, :])
            Ratio[np.isnan(Ratio)] = 0
            if(np.sum(Flow[Num, :]) != 0):
                Flow[Num, :] = FlowInNode*InterPW.UnitRatio*Ratio 
            
        ##Power Demand - Water Supply
        for node in Water.SupplySeries:
            Num = Water.WholeNodeSeries[node]
            FlowInNode = np.sum(Flow[Power.WholeNodeSeries[Power.DemandSeries], Num])
            
            Ratio = Flow[Num, :]/np.sum(Flow[Num, :])
            Ratio[np.isnan(Ratio)] = 0
            if(np.sum(Flow[Num, :]) != 0):
                Flow[Num, :] = FlowInNode*Ratio

        Water.SatisfyDemand.append([])
        ##Water Supply - Water Demand
        for node in Water.DemandSeries:
           Num = Water.WholeNodeSeries[node]
           FlowInNode = np.sum(Flow[Water.WholeNodeSeries[Water.SupplySeries], Num]) + np.sum(Flow[Water.WholeNodeSeries[Water.DemandSeries], Num])
           FlowInNode, Water.DemandValue[node - Water.DemandSeries[0]] = math.floor(FlowInNode), math.floor(Water.DemandValue[node - Water.DemandSeries[0]])
           
           if(math.floor(FlowInNode) >= math.floor(Water.DemandValue[node - Water.DemandSeries[0]])):
               FlowInNode = FlowInNode - Water.DemandValue[node - Water.DemandSeries[0]]
               Water.SatisfyDemand[-1].append(Water.DemandValue[node - Water.DemandSeries[0]])
           else:
               Water.SatisfyDemand[-1].append(0.25*FlowInNode)
               FlowInNode *= 0.75    
               
           Ratio = Flow[Num, :]/np.sum(Flow[Num, :])
           Ratio[np.isnan(Ratio)] = 0
           if(np.sum(Flow[Num, :]) != 0):
               Flow[Num, :] = FlowInNode*Ratio
        
        self.Target.FlowAdj.append(Flow)
        
    def CascadFail(self):
        self.NodeFailIndex.append(copy.deepcopy(self.NodeFailIndex[-1]))
        for i in range(Shelby_County.NodeNum):
            FlowInNode = np.sum(self.Target.FlowAdj[-1][:, i])
            FlowInNode0 = np.sum(self.Target.FlowAdj[0][:, i])
            
            if(FlowInNode < LowBound*FlowInNode0 and (i not in self.NodeFailIndex[-1])):
                self.NodeFailIndex[-1].append(i)
            if(FlowInNode > UpBound*FlowInNode0 and (i not in self.NodeFailIndex[-1])):
                self.NodeFailIndex[-1].append(i)

    
    def Performance(self, Type):
        if(Type == "SingleSum"):
            for Network in self.Target.Networks:
                Temp = 0
                Num = 0
                for i in range(len(Network.DemandValue)):
                    if(Network.DemandValue[i] != 0):
                        Temp += Network.SatisfyDemand[-1][i]/Network.DemandValue[i]
                        Num += 1
                Network.Performance.append(min(1, Temp/Num))
                
        if(Type == "WholeSum"):
            for Network in self.Target.Networks:
                Network.Performance.append(min(1, np.sum(np.array(Network.SatisfyDemand[-1]))/np.sum(Network.DemandValue)))
        
        self.Target.Performance  = (np.array(Water.Performance) + np.array(Gas.Performance) + np.array(Power.Performance))/3
        

Earth = EarthquakeSys(Shelby_County, DisrupLon, DisrupLat, DisrupIntensity)
Earth.DistanceCalculation()
Earth.NodeFailProbCalculation()
Earth.MCFailureSimulation()

Earth.GeoDepenFailProb()
Earth.GeoMCSimulation()

while(1):
    Earth.AdjUpdate()
    Earth.FlowUpdate()
    Earth.CascadFail()
    Earth.Performance("SingleSum")
    if(Earth.NodeFailIndex[-1] == Earth.NodeFailIndex[-2]):
        break