#System after Disruption but right before the initialization of the restoration
#T: The Whole Simulation Time; t1: The Beginning of the Restoration Time;
class Res_System:
    def __init__(self, T, System1):
        self.Adj = np.zeros([T, System1.NodeNum, System1.NodeNum])
        self.Flow = np.zeros([T, System1.NodeNum, System1.NodeNum])
        self.LinkCap = System1.LinkCap
        self.NodeCap = System1.NodeCap
        self.NodeNum = System1.NodeNum
        self.InitSystem = System1
        
        self.NodeOp = np.zeros([T, System1.NodeNum])
        self.LinkOp = np.zeros([T, System1.NodeNum, System1.NodeNum])
    
    def InitUpdate(self, t1, Disruption):
        if(t1 < len(self.InitSystem.Performance)):
            self.Adj[0, :, :] = self.InitSystem.TimeAdj[t1]
            self.Flow[0, :, :] = self.InitSystem.FlowAdj[t1]
        else:
            self.Adj[0, :, :] = self.InitSystem.TimeAdj[-1]
            self.Flow[0, :, :] = self.InitSystem.FlowAdj[-1]
    
        self.LinkOp[0, :, :] = self.Flow[0, :, :]/self.LinkCap
        for node in range(self.NodeNum):
            self.NodeOp[0, node] = self.Flow[0][:, node].sum()/self.NodeCap[node]

        
        
Shelby_County_Res = Res_System(10, Shelby_County)
Shelby_County_Res.InitUpdate(3, Earth)

    
    
    
        
    
    
    