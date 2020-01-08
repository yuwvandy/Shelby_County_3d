# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 15:03:15 2019

@author: wany105
"""
import os

#os.environ['PROJ_LIB'] = r"E:\Anaconda\pkgs\proj4-5.2.0-ha925a31_1\Library\share"
os.environ['PROJ_LIB'] = r"C:\Users\wany105\AppData\Local\Continuum\anaconda3\pkgs\proj4-5.2.0-ha925a31_1\Library\share"

"""
The environment is different among different computers. Please check where the epsg file is in your own computer and change the path in os.environ accordingly
EXAMPLE: In my laptop ---- os.environ['PROJ_LIB'] = E:\Anaconda\pkgs\proj4-5.2.0-ha925a31_1\Library\share
"""
Type = "local"

import copy
from mpl_toolkits.basemap import Basemap ##Basemap package is used for creating geography map
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as colors
import math
import csv
import pandas as pd

Disrupllon, Disruprlon = -90.2, -89.6
Disrupllat, Disruprlat = 34.98, 35.4


def Normalize(Data):
    return (Data - np.min(Data))/(np.max(Data) - np.min(Data))

def BaseMapSet(Type):
    if(Type == 'local'):
        Base = Basemap(projection = 'merc', resolution = 'l', area_thresh = 1000.0, lat_0=0, lon_0=0, llcrnrlon = Disrupllon, llcrnrlat=Disrupllat, urcrnrlon=Disruprlon, urcrnrlat=Disruprlat)
    elif(Type == 'whole'):
        Base = Basemap(resolution = 'l', area_thresh = 1000.0, lat_0=0, lon_0=0, llcrnrlon=Disrupllon, llcrnrlat = Disrupllat, urcrnrlon=Disruprlon, urcrnrlat=Disruprlat)
    Base.drawcoastlines()
    Base.drawcountries()
    Base.drawmapboundary()
    Base.drawparallels(np.arange(34, 36, 0.07), labels=[1,0,0,1], fontsize=10)
    Base.drawmeridians(np.arange(-91, -89, 0.1), labels=[1,1,0,1], fontsize=10)
    return Base

#Laptop
#WN = pd.read_excel (r'C:\Users\10624\OneDrive - Vanderbilt\Research\ShelbyCounty_DataRead\WaterNodes.xlsx') #for an earlier version of Excel, you may need to use the file extension of 'xls'
#WE = pd.read_excel (r'C:\Users\10624\OneDrive - Vanderbilt\Research\ShelbyCounty_DataRead\WaterEdges.xlsx') #for an earlier version of Excel, you may need to use the file extension of 'xls'
#PN = pd.read_excel (r'C:\Users\10624\OneDrive - Vanderbilt\Research\ShelbyCounty_DataRead\PowerNodes.xlsx') #for an earlier version of Excel, you may need to use the file extension of 'xls'
#PE = pd.read_excel (r'C:\Users\10624\OneDrive - Vanderbilt\Research\ShelbyCounty_DataRead\PowerEdges.xlsx') #for an earlier version of Excel, you may need to use the file extension of 'xls'
#GN = pd.read_excel (r'C:\Users\10624\OneDrive - Vanderbilt\Research\ShelbyCounty_DataRead\GasNodes.xlsx') #for an earlier version of Excel, you may need to use the file extension of 'xls'
#GE = pd.read_excel (r'C:\Users\10624\OneDrive - Vanderbilt\Research\ShelbyCounty_DataRead\GasEdges.xlsx') #for an earlier version of Excel, you may need to use the file extension of 'xls'

#Desktop
WN = pd.read_excel (r'C:\Users\wany105\OneDrive - Vanderbilt\Research\ShelbyCounty_DataRead\WaterNodes.xlsx') #for an earlier version of Excel, you may need to use the file extension of 'xls'
WE = pd.read_excel (r'C:\Users\wany105\OneDrive - Vanderbilt\Research\ShelbyCounty_DataRead\WaterEdges.xlsx') #for an earlier version of Excel, you may need to use the file extension of 'xls'
PN = pd.read_excel (r'C:\Users\wany105\OneDrive - Vanderbilt\Research\ShelbyCounty_DataRead\PowerNodes.xlsx') #for an earlier version of Excel, you may need to use the file extension of 'xls'
PE = pd.read_excel (r'C:\Users\wany105\OneDrive - Vanderbilt\Research\ShelbyCounty_DataRead\PowerEdges.xlsx') #for an earlier version of Excel, you may need to use the file extension of 'xls'
GN = pd.read_excel (r'C:\Users\wany105\OneDrive - Vanderbilt\Research\ShelbyCounty_DataRead\GasNodes.xlsx') #for an earlier version of Excel, you may need to use the file extension of 'xls'
GE = pd.read_excel (r'C:\Users\wany105\OneDrive - Vanderbilt\Research\ShelbyCounty_DataRead\GasEdges.xlsx') #for an earlier version of Excel, you may need to use the file extension of 'xls'


Infras_Dict = [[WN, WE], [PN, PE], [GN, GE]]

class Network:
    def __init__(self, Name, NodeNum, Lon, Lat, SupplyNum, DemandNum, Color, SupplyName, DemandName, \
                 Limit, TranFee, SLamb, DLamb, SZeta, DZeta, Demand_Person):
        self.Name = Name
        self.NodeNum = NodeNum
        self.Color = Color
        self.DemandName = DemandName
        self.SupplyName = SupplyName
        self.Limit  = Limit
        self.Demand_Person = Demand_Person
        
        self.Lon = Lon
        self.Lat = Lat
        
        self.Adjlist = None
        self.NodeDist = np.zeros([NodeNum, NodeNum])
        
        self.SupplyNum = SupplyNum
        self.DemandNum = DemandNum
        
        self.SupplySeries = np.arange(0, SupplyNum, 1)
        self.DemandSeries = np.arange(SupplyNum, SupplyNum + DemandNum, 1)
        self.NodeSeries = np.arange(0, SupplyNum + DemandNum, 1)
        
        self.TranFee = TranFee
        self.SLamb, self.SZeta = SLamb, SZeta
        self.DLamb, self.DZeta = DLamb, DZeta
        
        
    
    def Geo2XY(self, EarthMap):
        self.X, self.Y = EarthMap(self.Lon, self.Lat)
    
    def AdjList2Matrix(self):
        self.EdgeNum = len(self.Adjlist[0])
        self.Adj = np.zeros([self.NodeNum, self.NodeNum])
        self.Capacity = np.zeros([self.NodeNum, self.NodeNum])
        for i in range(self.EdgeNum):
            if(self.Adjlist[0][i] in self.SupplySeries and self.Adjlist[1][i] in self.DemandSeries):
                self.Adj[self.Adjlist[0][i]][self.Adjlist[1][i]] = 1
                self.Capacity[self.Adjlist[0][i]][self.Adjlist[1][i]] = self.Limit
                
            elif(self.Adjlist[0][i] in self.DemandSeries and self.Adjlist[1][i] in self.SupplySeries):
                self.Adj[self.Adjlist[1][i]][self.Adjlist[0][i]] = 1
                
                self.Capacity[self.Adjlist[1][i]][self.Adjlist[0][i]] = self.Limit
            else:
                self.Adj[self.Adjlist[0][i]][self.Adjlist[1][i]] = 1
                self.Adj[self.Adjlist[1][i]][self.Adjlist[0][i]] = 1
                
                self.Capacity[self.Adjlist[0][i]][self.Adjlist[1][i]] = self.Limit
                self.Capacity[self.Adjlist[1][i]][self.Adjlist[0][i]] = self.Limit
    
    def NetworkVisual(self):
        plt.figure(figsize = (20, 12))
        Base = BaseMapSet(Type)
        ##Vertice
        plt.scatter(self.X[self.SupplySeries], self.Y[self.SupplySeries], 200, marker = 's', color = self.Color, label = self.SupplyName)
        plt.scatter(self.X[self.DemandSeries], self.Y[self.DemandSeries], 200, marker = 'o', color = self.Color, facecolors = 'none', label = self.DemandName)
                
        ##Edge                
        for i in range(self.EdgeNum):
            plt.plot([self.X[self.Adjlist[0][i]], self.X[self.Adjlist[1][i]]], [self.Y[self.Adjlist[0][i]], self.Y[self.Adjlist[1][i]]], 'black', lw = 2)
            
        plt.legend(bbox_to_anchor=(1, 1), loc='upper left', ncol=1)
    
    def Dist(self):
        self.Dist = np.zeros([self.NodeNum, self.NodeNum])
        for i in range(self.NodeNum):
            for j in range(self.NodeNum):
                self.Dist[i][j] = np.sqrt((self.X[i] - self.X[j])**2 + (self.Y[i] - self.Y[j])**2)/1000 #Unit Change km
        
            
            
class System:
    def __init__(self, Name):
        self.Name = Name
        self.Networks = None
        self.NodeNum = 0
        self.Interdependency = None
        self.WholeFlow = []
        
        
        
    def DataCombine(self):
        self.Networks[0].WholeNodeSeries = np.arange(0, self.Networks[0].NodeNum, 1)
        self.Networks[1].WholeNodeSeries = np.arange(self.Networks[0].NodeNum, self.Networks[0].NodeNum + self.Networks[1].NodeNum, 1)
        self.Networks[2].WholeNodeSeries = np.arange(self.Networks[0].NodeNum + self.Networks[1].NodeNum, \
                                     self.Networks[0].NodeNum + self.Networks[1].NodeNum + self.Networks[2].NodeNum, 1)
            
        self.NodeNum = self.Networks[0].NodeNum + self.Networks[1].NodeNum + self.Networks[2].NodeNum
        
        self.Networks[0].IniNum = 0
        self.Networks[1].IniNum = self.Networks[0].NodeNum
        self.Networks[2].IniNum = self.Networks[0].NodeNum + self.Networks[1].NodeNum
        self.Networks[0].EndNum = self.Networks[1].IniNum
        self.Networks[1].EndNum = self.Networks[2].IniNum
        self.Networks[2].EndNum = self.NodeNum
        
        for Network in self.Networks:
            Network.WholeSupplySeries = np.arange(Network.IniNum, Network.IniNum + Network.SupplyNum, 1)
            Network.WholeDemandSeries = np.arange(Network.IniNum + Network.SupplyNum, Network.EndNum, 1)
            
        
        self.CoorlistX = np.concatenate((self.Networks[0].X, self.Networks[1].X, self.Networks[2].X))
        self.CoorlistY = np.concatenate((self.Networks[0].Y, self.Networks[1].Y, self.Networks[2].Y))
        
        self.Whole2NetworkSeries = np.concatenate((self.Networks[0].NodeSeries, (self.Networks[1].NodeSeries), (self.Networks[2].NodeSeries)))
        
    def Dist(self):
        self.Dist = np.zeros([self.NodeNum, self.NodeNum])
        for i in range(self.NodeNum):
            for j in range(self.NodeNum):
                self.Dist[i][j] = np.sqrt((self.CoorlistX[i] - self.CoorlistX[j])**2 + (self.CoorlistY[i] - self.CoorlistY[j])**2)/1000
    
    def AdjMatrix(self):
        self.Adj = np.zeros([self.NodeNum, self.NodeNum])
        self.Capacity = np.zeros([self.NodeNum, self.NodeNum])
        for Network in self.Networks:
            self.Adj[Network.IniNum:Network.EndNum, Network.IniNum:Network.EndNum] = Network.Adj
            self.Capacity[Network.IniNum:Network.EndNum, Network.IniNum:Network.EndNum] = Network.Capacity
    
    def LinkNodeCoor(self):
        self.LinkListCoor = []
        for i in range(self.NodeNum):
            for j in range(self.NodeNum):
                if(self.Adj[i, j] == 1):
                    self.LinkListCoor.append([i, j, self.CoorlistX[i], self.CoorlistX[j], self.CoorlistY[i], self.CoorlistY[j], self.Dist[i, j]])
        self.LinkListCoor = np.array(self.LinkListCoor)
                    

    def SysVisual(self, Normalize_Flow):
        plt.figure(figsize = (20, 12))
        Base = BaseMapSet(Type)
        
        #Vertice
        for Network in self.Networks:
            plt.scatter(Network.X[Network.SupplySeries], Network.Y[Network.SupplySeries], 150, marker = 's', color = Network.Color, label = Network.SupplyName)
            plt.scatter(Network.X[Network.DemandSeries], Network.Y[Network.DemandSeries], 150, marker = 'o', color = Network.Color, facecolors = 'none', label = Network.DemandName)
        
        plt.legend(bbox_to_anchor=(1, 1), loc='upper left', ncol=1)        
        #Edge
        for i in range(self.NodeNum):
            for j in range(self.NodeNum):
                if(self.Adj[i][j] == 1):
                    plt.plot([self.CoorlistX[i], self.CoorlistX[j]], [self.CoorlistY[i], self.CoorlistY[j]], 'black', lw = 7.5*Normalize_Flow[i][j])        
                
Limit = 200
    
##Define Network: Water, Electricity, Gas
Water = Network('Water', len(WN), np.array(WN['Long']), np.array(WN['Lat']), 9, 40, 'blue', 'Pump Station', 'Water Substation', 1000, 0.1, np.log(1.5), np.log(1.2), 0.8, 0.6, 0.01)
Power = Network('Power', len(PN), np.array(PN['Long']), np.array(PN['Lat']), 9, 51, 'r', 'Power Plant', 'Power Substaion', 1000, 0.1, np.log(1.4), np.log(1.2), 0.4, 0.4, 0.01)
Gas = Network('Gas', len(GN), np.array(GN['Long']), np.array(GN['Lat']), 3, 13, 'green', 'Gas Plant', 'Gas Substation', 1000, 0.1, np.log(1.5), np.log(1.2), 0.8, 0.6, 0.01)

Water.Adjlist = np.stack((np.array(WE['START WATER NODE ID']) - 1, np.array(WE['END WATER NODE ID']) - 1))
Power.Adjlist = np.stack((np.array(PE['START POWER NODE ID']) - 1, np.array(PE['END POWER NODE ID']) - 1))
Gas.Adjlist = np.stack((np.array(GE['START GAS NODE ID']) - 1, np.array(GE['END GAS NODE ID']) - 1))

Water.AdjList2Matrix()
Power.AdjList2Matrix()
Gas.AdjList2Matrix()

Base = BaseMapSet(Type)
Water.Geo2XY(Base)
Power.Geo2XY(Base)
Gas.Geo2XY(Base)

Water.Dist()
Power.Dist()
Gas.Dist()

##Define System: Shelby_County
Shelby_County = System("Shelby_County")
Shelby_County.Networks = [Gas, Power, Water]

Water.NetworkVisual()
Power.NetworkVisual()
Gas.NetworkVisual()

Shelby_County.DataCombine()
Shelby_County.Dist()
Shelby_County.AdjMatrix()
Shelby_County.LinkNodeCoor()

Shelby_County.DemandNum = 0
Shelby_County.SupplyNum = 0



for Network in Shelby_County.Networks:
    Shelby_County.DemandNum += Network.DemandNum
    Shelby_County.SupplyNum += Network.SupplyNum
    
    
##----------------------------------------------------Network Demand Need
Lon = np.arange(Disrupllon, Disruprlon, (Disruprlon - Disrupllon)/10)
Lat = np.arange(Disrupllat, Disruprlat, (Disruprlat - Disrupllat)/10)
X = np.zeros(len(Lon) - 1)
Y = np.zeros(len(Lat) - 1)
Grid_Area = np.zeros([len(Lon) - 1, len(Lat) - 1])
MiddleX = np.zeros([len(Lon) - 1, len(Lat) - 1])
MiddleY = np.zeros([len(Lon) - 1, len(Lat) - 1])
Density = np.zeros([len(Lon) - 1, len(Lat) - 1])
X, Y = Base(Lon, Lat)
for i in range(len(X) - 1):
    for j in range(len(Y) - 1):
        Grid_Area[i][j] = (X[i+1] - X[i])*(Y[j+1] - Y[j])
        Density[i][j] = 166/(1600)**2 ##Data: http://worldpopulationreview.com/states/state-densities/: 166Popu/1mi^2
        MiddleX[i][j] = (X[i] + X[i+1])/2
        MiddleY[i][j] = (Y[j] + Y[j+1])/2

def NeedAssignment(Network, Density, X, Y, Area):
    for j in range(len(X)):
        for k in range(len(Y)):
            Min = math.inf
            for i in Network.DemandSeries:
                Temp = np.sqrt((Network.X[i] - X[j][k])**2 + (Network.Y[i] - Y[j][k])**2)
                if(Temp < Min):
                    Index = i
                    Min = Temp
            Network.DemandValue[Index - Network.DemandSeries[0]] += Density[j][k]*Area[j][k]*Network.Demand_Person

for Network in Shelby_County.Networks:
    Network.DemandValue = np.zeros(Network.DemandNum)
    NeedAssignment(Network, Density, MiddleX, MiddleY, Grid_Area)    