# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 11:22:00 2019

@author: wany105
"""

import math

N = 3 #Number of vertices that the vertex in another network depends on
def NMinIndex(Array, N):
    temp = 0
    Index = []
    while(temp < N):
        Min = math.inf
        for i in range(len(Array)):
            if(Array[i] < Min and i not in Index):
                Min = Array[i]
                Temp = i
        Index.append(Temp)
        temp += 1
    return np.array(Index)

class Interdependency:
    def __init__(self, Name, Network1, Network2, System, Type, UnitRatio): #Network2 depend on Network1
        self.Name = Name
        self.System = System
        
        self.Name1 = Network1.Name
        self.Name2 = Network2.Name
        
        self.Network1 = Network1
        self.Network2 = Network2
        
        self.NodeSeries1 = self.Network1.DemandSeries
        self.NodeSeries2 = self.Network2.SupplySeries
        
        self.Type = Type
        self.UnitRatio = UnitRatio
    
    def InterDepAdj(self):
        self.Adj = np.zeros([self.Network1.DemandNum, self.Network2.SupplyNum])
        self.Capacity = np.zeros([self.Network1.DemandNum, self.Network2.SupplyNum])
        
        for i in self.Network2.WholeSupplySeries:
            Index = NMinIndex(self.System.Dist[self.Network1.WholeDemandSeries, i], N)
            self.Adj[Index, i - self.Network2.WholeSupplySeries[0]] = 1
            self.Capacity[Index, i - self.Network2.WholeSupplySeries[0]] = self.Network1.Limit
            self.System.Adj[Index + self.Network1.WholeDemandSeries[0], i] = 1
            self.System.Capacity[Index + self.Network1.WholeDemandSeries[0], i] = self.Network1.Limit
            

InterGP = Interdependency("InterGasPower", Gas, Power, Shelby_County, "Resource", 1)
InterPG = Interdependency("InterPowerGas", Power, Gas, Shelby_County, "Power", 10)
InterPW = Interdependency("InterPowerWater", Power, Water, Shelby_County, "Power", 1)
InterWP = Interdependency("InterWaterPower", Water, Power, Shelby_County, "Cooling", 10)

InterGP.InterDepAdj()
InterPG.InterDepAdj()
InterPW.InterDepAdj()
InterWP.InterDepAdj()

Shelby_County.Interdependency = [InterGP, InterPG, InterPW, InterWP]

for InterNetwork in Shelby_County.Interdependency:
    InterNetwork.TimeAdj = []
    InterNetwork.TimeAdj.append(InterNetwork.Adj)
    