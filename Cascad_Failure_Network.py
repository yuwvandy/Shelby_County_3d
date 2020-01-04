# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 16:56:24 2019

@author: wany105
"""
for Network in Shelby_County.Networks:
    Network.FlowAdj = []
    Network.FlowAdj.append(np.zeros([Network.NodeNum, Network.NodeNum]))
    i = Network.WholeNodeSeries[Network.SupplySeries[0]]
    j = Network.WholeNodeSeries[Network.DemandSeries[-1]]
    Network.FlowAdj[0] = Shelby_County.FlowAdj[0][i:(j + 1), i:(j + 1)]

class EarthquakeNet:
    def __init__(self, Target, FailureSystem):##Type 1 - System, Type 2 - Single Network
        self.Target = Target
        self.FailSys = FailureSystem
    
    def VariableIni(self):
        self.Target.SingleTimeAdj = []
        self.Target.SingleTimeAdj.append(copy.copy(Network.Adj))
        self.Target.NodeFailIndex = []
        self.Target.SingleSatisDe = []
        self.Target.SinglePerform = [1]
        self.Target.TimeAdj = []
        self.Target.TimeAdj.append(self.Target.Adj)

    def IniFailCopy(self):
        self.Target.NodeFailIndex.append([])
        for node in self.Target.NodeSeries:
            if(self.Target.WholeNodeSeries[node] in self.FailSys.NodeFailIndex1[0]):
                self.Target.NodeFailIndex[-1].append(node)
        
    def AdjUpdate(self):
        Adj = copy.copy(self.Target.TimeAdj[-1])
        """
        gama = 0.5
        for i in self.Target.NodeFailIndex[-1]:
            for j in range(self.Target.NodeNum):
                if(Adj[i][j] != gama):
                    Adj[i][j] = gama
                if(Adj[j][i] != gama):
                    Adj[j][i] = gama
        """
        
        Adj[self.Target.NodeFailIndex[-1], :] = 0
        Adj[:, self.Target.NodeFailIndex[-1]] = 0
        
        self.Target.TimeAdj.append(Adj)
        
    def FlowUpdate(self):
        Flow = self.Target.TimeAdj[-1]*self.Target.FlowAdj[-1]

        ##Demand -> Supply
        for node in self.Target.SupplySeries:
            FlowInNode = np.sum(Flow[node, self.Target.DemandSeries])
            Ratio = Flow[node, :]/np.sum(Flow[node, :])
            Ratio[np.isnan(Ratio)] = 0
            if(np.sum(Flow[node, :]) != 0):
                Flow[node, :] = FlowInNode*Ratio

        ##Supply -> Demand
        self.Target.SingleSatisDe.append([])
        for node in self.Target.DemandSeries:
            FlowInNode = np.sum(Flow[self.Target.SupplySeries, node]) + np.sum(Flow[self.Target.DemandSeries, node])
            if(math.floor(FlowInNode) >= math.floor(self.Target.DemandValue[node - self.Target.DemandSeries[0]])):
                FlowInNode = FlowInNode - self.Target.DemandValue[node - self.Target.DemandSeries[0]]
                self.Target.SingleSatisDe[-1].append(self.Target.DemandValue[node - self.Target.DemandSeries[0]])
            else:
                self.Target.SingleSatisDe[-1].append(0.25*FlowInNode)
                FlowInNode *= 0.75
            """
            Ratio = Flow[node, :]/np.sum(Flow[node, :])
            Ratio[np.isnan(Ratio)] = 0
            if(np.sum(Flow[node, :]) != 0):
                Flow[node, :] = FlowInNode*Ratio        
            """
        self.Target.FlowAdj.append(Flow)
        
    def CascadFail(self):
        self.Target.NodeFailIndex.append(copy.copy(self.Target.NodeFailIndex[-1]))
        for i in range(Network.NodeNum):
            FlowInNode = np.sum(self.Target.FlowAdj[-1][:, i])
            FlowInNode0 = np.sum(self.Target.FlowAdj[0][:, i])
            if(FlowInNode < LowBound*FlowInNode0 and (i not in self.Target.NodeFailIndex[-1])):
                self.Target.NodeFailIndex[-1].append(i)
            if(FlowInNode > UpBound*FlowInNode0 and (i not in self.Target.NodeFailIndex[-1])):
                self.Target.NodeFailIndex[-1].append(i)


    def Performance(self, Type):
        if(Type == "SingleSum"):
            Temp = 0
            Num = 0
            for i in range(len(self.Target.DemandValue)):
                if(self.Target.DemandValue[i] != 0):
                    Temp += self.Target.SingleSatisDe[-1][i]/self.Target.DemandValue[i]
                    Num += 1
            self.Target.SinglePerform.append(min(1, Temp/Num))
        
        if(Type == "WholeSum"):
            self.Target.SinglePerform.append(min(1, np.sum(np.array(self.Target.SingleSatisDe[-1]))/np.sum(self.Target.DemandValue)))
            
AnalType = 'SingleSum'
for Network in Shelby_County.Networks:
    exec('Earth{} = EarthquakeNet(Network, Earth)'.format(Network.Name))
    exec('Earth{}.VariableIni()'.format(Network.Name))
    exec('Earth{}.IniFailCopy()'.format(Network.Name))
    while(1):
        exec('Earth{}.AdjUpdate()'.format(Network.Name))
        exec('Earth{}.FlowUpdate()'.format(Network.Name))
        exec('Earth{}.CascadFail()'.format(Network.Name))
        exec('Earth{}.Performance("{}")'.format(Network.Name, AnalType))
        exec('Temp1 = Earth{}.Target.NodeFailIndex[-1]'.format(Network.Name))
        exec('Temp2 = Earth{}.Target.NodeFailIndex[-2]'.format(Network.Name))
        if(Temp1 == Temp2):
            break