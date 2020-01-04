# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 16:28:44 2019

@author: wany105
"""

from pulp import *
from collections import defaultdict
import copy



#Class Flow
class Flow:
    def __init__(self, System):
        self.System = System
        self.temp, self.WholeFlow, self.Obj = 1, dict(), ""
        
        
    def FlowProb(self, System):
        ##Problem Setup and Variable Initialization----------------------------
        self.prob = LpProblem('Flow', LpMinimize)
        
        for Network in System.Networks:
            Network.Flow = dict()
            Network.NodeFlowConverge = [""]*Network.NodeNum
            if(Network.Name == 'Power'):
                Network.NodeFlowConverge2 = [""]*Network.NodeNum
                
        for InterNetwork in self.System.Interdependency:
            InterNetwork.Flow = dict()
            
        #Flow within Network Initialization------------------------------------
        for Network in System.Networks:
            for i in Network.NodeSeries:
                for j in Network.NodeSeries:
                    if(Network.Adj[i][j] == 1):
                        exec('f{}{}{} = LpVariable("f{}{}{}", 10, {})'.format(Network.Name, i, j, Network.Name, i, j, Network.Capacity[i][j]))
                        
                        Network.Flow['f{}{}{}'.format(Network.Name, i, j)] = [i, j, None]
                        self.WholeFlow['f{}{}{}'.format(Network.Name, i, j)] = None
                        
                        """
                        if(i in Network.SupplySeries):
                            if(Network.Name == "Power"):
                                Network.FlowSupPro_Cooling[i - Network.SupplySeries[0]] += "f{}{}{}".format(Network.Name, i, j)
                            Network.FlowSupProvide[i - Network.SupplySeries[0]] += '-f{}{}{}'.format(Network.Name, i, j)
                        """
                        
                        if(Network.NodeFlowConverge[j] == ""):
                            Network.NodeFlowConverge[j] += "f{}{}{}".format(Network.Name, i, j)
                        else:  
                            Network.NodeFlowConverge[j] += "+f{}{}{}".format(Network.Name, i, j)
                        
                        Network.NodeFlowConverge[i] += "-f{}{}{}".format(Network.Name, i, j)
                        
                        if(self.Obj == ""):
                            self.Obj += 'f{}{}{}*{}*{}'.format(Network.Name, i, j, Network.TranFee, Network.Dist[i][j])
                        else:
                            self.Obj += '+ f{}{}{}*{}*{}'.format(Network.Name, i, j, Network.TranFee, Network.Dist[i][j])
        
        Power.NodeFlowConverge2 = copy.copy(Power.NodeFlowConverge)
        
        ##Rule out circulation between vertice within the same network---------
        """
        for Network in self.System.Networks:
            for i in Network.NodeSeries:
                exec('self.prob += ' + Network.NodeFlowConverge[i] + ' == 0, "c{}"'.format(self.temp))
                self.temp += 1        
        """
        #Flow between Network Initialization-----------------------------------
        for InterNetwork in System.Interdependency:
            for i in InterNetwork.NodeSeries1:
                for j in InterNetwork.NodeSeries2:
                    if(InterNetwork.Adj[i - InterNetwork.NodeSeries1[0]][j - InterNetwork.NodeSeries2[0]] == 1):
                        exec('f{}{}{}{} = LpVariable("f{}{}{}{}", 10, {})'.format(InterNetwork.Name1, i, InterNetwork.Name2, j, InterNetwork.Name1, i, InterNetwork.Name2, j, InterNetwork.Capacity[i - InterNetwork.NodeSeries1[0]][j - InterNetwork.NodeSeries2[0]]))
                        
                        InterNetwork.Flow['f{}{}{}{}'.format(InterNetwork.Name1, i, InterNetwork.Name2, j)] = [i, j, None]
                        self.WholeFlow['f{}{}{}{}'.format(InterNetwork.Name1, i, InterNetwork.Name2, j)] = None
                    
                        InterNetwork.Network1.NodeFlowConverge[i] += "-f{}{}{}{}".format(InterNetwork.Name1, i, InterNetwork.Name2, j)
                        
                        if(InterNetwork.Name != "InterWaterPower"):
                            InterNetwork.Network2.NodeFlowConverge[j] += "+{}*f{}{}{}{}".format(InterNetwork.UnitRatio, InterNetwork.Name1, i, InterNetwork.Name2, j)
                        if(InterNetwork.Name == "InterWaterPower"):
                            InterNetwork.Network2.NodeFlowConverge2[j] += "+{}*f{}{}{}{}".format(InterNetwork.UnitRatio, InterNetwork.Name1, i, InterNetwork.Name2, j)
                            
                        if(self.Obj == ""):
                            self.Obj += 'f{}{}{}{}*{}*{}'.format(InterNetwork.Name1, i, InterNetwork.Name2, j, InterNetwork.Network1.TranFee, System.Dist[InterNetwork.Network1.WholeNodeSeries[i]][InterNetwork.Network2.WholeNodeSeries[j]])
                        else:
                            self.Obj += '+ f{}{}{}{}*{}*{}'.format(InterNetwork.Name1, i, InterNetwork.Name2, j, InterNetwork.Network1.TranFee, System.Dist[InterNetwork.Network1.WholeNodeSeries[i]][InterNetwork.Network2.WholeNodeSeries[j]])
        #Flow Constraints------------------------------------------------------
        for Network in System.Networks:
            for i in Network.NodeSeries:
                if(i in Network.DemandSeries):
                    exec('self.prob += ' + Network.NodeFlowConverge[i] + ' == {}, "c{}"'.format(Network.DemandValue[i - Network.SupplyNum], self.temp))
                    self.temp += 1
                else:
                    if(Network.Name == 'Power'):
                        exec('self.prob += ' + Network.NodeFlowConverge2[i] + ' == 0, "c{}"'.format(self.temp))  
                        self.temp += 1
                    
                    exec('self.prob += ' + Network.NodeFlowConverge[i] + ' == 0, "c{}"'.format(self.temp))
                    self.temp += 1
    
        #Flow Solve------------------------------------------------------------
        exec('self.prob += ' + self.Obj + ',"Obj"')
        self.prob.solve()
        print("Status", LpStatus[self.prob.status])
    
    def PostProcess(self, System):
        System.FlowAdj = []
        System.FlowAdj.append(np.zeros([System.NodeNum, System.NodeNum]))            
        
        for v in self.prob.variables():
            """
            print(v.name, "=", v.varValue)
            """
            self.WholeFlow[v.name] = v.varValue
            for Network in System.Networks:
                try:
                    Network.Flow[v.name][2] = v.varValue
                    System.FlowAdj[-1][Network.WholeNodeSeries[Network.Flow[v.name][0]]]\
                        [Network.WholeNodeSeries[Network.Flow[v.name][1]]] = v.varValue
                except:
                    continue
            
            for InterNetwork in System.Interdependency:
                try:
                    InterNetwork.Flow[v.name][2] = v.varValue
                    System.FlowAdj[-1][InterNetwork.Network1.WholeNodeSeries[InterNetwork.Flow[v.name][0]]]\
                        [InterNetwork.Network2.WholeNodeSeries[InterNetwork.Flow[v.name][1]]] = v.varValue
                except:
                    continue

        System.WholeFlow.append(self.WholeFlow)

        
Shelby_County_Flow = Flow(Shelby_County)
Shelby_County_Flow.FlowProb(Shelby_County)


    
                        
                        
                    
                    
                    
                    