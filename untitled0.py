from docplex.mp.model import Model
from collections import defaultdict
#System after Disruption but right before the initialization of the restoration
class Res_System:
    def __init__(self, T, System1, t1):
        self.Adj = np.zeros([T, System1.NodeNum, System1.NodeNum])
        self.LinkCap = System1.LinkCap
        self.NodeCap = System1.NodeCap
        self.NodeNum = System1.NodeNum
        self.InitSystem = System1
        self.t1 = t1 #the beginning time of the whole restoration
        self.T = T
        
        self.Obj = None
        
        self.Flow = np.zeros([T, System1.NodeNum, System1.NodeNum])
        self.Flow_Object = np.zeros([T, self.NodeNum, self.NodeNum], dtype = object)
        self.trN = np.zeros(self.NodeNum)
        self.trN_Object = np.zeros(self.NodeNum, dtype = object)
        self.tfN = np.zeros(self.NodeNum)
        self.tfN_Object = np.zeros(self.NodeNum, dtype = object)
        self.trL = np.zeros([self.NodeNum, self.NodeNum])
        self.trL_Object = np.zeros([self.NodeNum, self.NodeNum], dtype = object)
        self.tfL = np.zeros([self.NodeNum, self.NodeNum])
        self.tfL_Object = np.zeros([self.NodeNum, self.NodeNum], dtype = object)
        
        self.XN = np.zeros([T, System1.NodeNum])
        self.XN_Object = np.zeros([T, System1.NodeNum], dtype = object)
        self.XL = np.zeros([T, System1.NodeNum, System1.NodeNum])
        self.XL_Object = np.zeros([T, System1.NodeNum, System1.NodeNum], dtype = object)
        
        self.NodeOp = np.zeros([T, System1.NodeNum])
        self.NodeOp_Object = np.zeros([T, System1.NodeNum], dtype = object)
        self.LinkOp = np.zeros([T, System1.NodeNum, System1.NodeNum])
        self.LinkOp_Object = np.zeros([T, System1.NodeNum, System1.NodeNum], dtype = object)
        
        self.Water = self.InitSystem.Networks[2]
        self.Power = self.InitSystem.Networks[1]
        self.Gas = self.InitSystem.Networks[0]
        
        """
        self.WaterReOut = np.zeros([T, Water.DemandNum])
        self.WaterReOut_Object = np.zeros([T, Water.DemandNum], dtype = object)
        self.PowerReOut = np.zeros([T, Power.DemandNum])
        self.PowerReOut_Object = np.zeros([T, Power.DemandNum], dtype = object)
        self.GasReOut = np.zeros([T, Gas.DemandNum])
        self.GasReOut_Object = np.zeros([T, Gas.DemandNum], dtype = object)
        """
        
        self.trN_dic = dict()
        self.tfN_dic = dict()
        self.trL_dic = dict()
        self.tfL_dic = dict()
        self.Flow_dic = dict()
        self.XN_dic = dict()
        self.XL_dic = dict()
        self.NodeOp_dic = dict()
        self.LinkOp_dic = dict()
        
        
        self.InitAdj = np.zeros([self.NodeNum, self.NodeNum])
        self.InitFlow = np.zeros([self.NodeNum, self.NodeNum])
        self.InitLinkOp = np.zeros([self.NodeNum, self.NodeNum])
        self.InitNodeOp = np.zeros(self.NodeNum)
        
        
    def InitUpdate(self, Disruption):#t1- the start time of the restoration
        if(self.t1 < len(self.InitSystem.Performance)):
            self.InitAdj = self.InitSystem.TimeAdj[self.t1]
            self.InitFlow = self.InitSystem.FlowAdj[self.t1]
        else:
            self.InitAdj = self.InitSystem.TimeAdj[-1]
            self.InitFlow = self.InitSystem.FlowAdj[-1]
    
        self.InitLinkOp = self.InitFlow/self.LinkCap
        
        for node in range(self.NodeNum):
            self.InitNodeOp[node] = self.InitFlow[:, node].sum()/self.NodeCap[node]
            
    def RepairRatio(self, beta):##Repair Speed: Capacity/Constant, quantifying how much capacity can we repair 
        self.NReRatio = self.NodeCap/beta
        self.LReRatio = self.LinkCap/beta
        
    def OptModelDefine(self, Name):
        self.mdl = Model(Name)
        
    def OpVarDefine(self):
        #tr, tf: integer Variables defining the beginning and finishing time of restoration for each link and node
        for node1 in range(self.NodeNum):
            exec("self.trN{} = self.mdl.integer_var(lb = self.t1, ub = self.T, name = 'trN{}')".format(node1, node1))
            exec("self.tfN{} = self.mdl.integer_var(lb = self.t1, ub = self.T, name = 'tfN{}')".format(node1, node1))
            
            self.trN_dic['trN{}'.format(node1)] = [eval('self.trN{}'.format(node1)), None]
            self.tfN_dic['tfN{}'.format(node1)] = [eval('self.tfN{}'.format(node1)), None]
            
            self.trN_Object[node1] = eval('self.trN{}'.format(node1))
            self.tfN_Object[node1] = eval('self.tfN{}'.format(node1))
            
            for node2 in range(self.NodeNum):
                exec("self.trL{}_{} = self.mdl.integer_var(lb = self.t1, ub = self.T, name = 'trL{}_{}')".format(node1, node2, node1, node2))
                exec("self.tfL{}_{} = self.mdl.integer_var(lb = self.t1, ub = self.T, name = 'tfL{}_{}')".format(node1, node2, node1, node2))
               
                self.trL_dic['trL{}_{}'.format(node1, node2)] = [eval('self.trL{}_{}'.format(node1, node2)), None]
                self.tfL_dic['tfL{}_{}'.format(node1, node2)] = [eval('self.tfL{}_{}'.format(node1, node2)), None]
    
                self.trL_Object[node1, node2] = eval('self.trL{}_{}'.format(node1, node2))
                self.tfL_Object[node1, node2] = eval('self.tfL{}_{}'.format(node1, node2))
        #XN, XL: Binary Variable determining whether the link and node is in the restoration or not
        #1 when current time step t in [tr, tf], 0 otherwise
        for t in range(T):
            for node1 in range(self.NodeNum):
                exec("self.XN{}_{} = self.mdl.binary_var(name = 'XN{}_{}')".format(t, node1, t, node1))
                
                self.XN_dic['XN{}_{}'.format(t, node1)] = [eval('self.XN{}_{}'.format(t, node1)), None]
                
                self.XN_Object[t, node1] = eval('self.XN{}_{}'.format(t, node1))
                
                exec("self.NodeOp{}_{} = self.mdl.continuous_var(name = 'NodeOp{}_{}')".format(t, node1, t, node1))
                
                self.NodeOp_dic['NodeOp{}_{}'.format(t, node1)] = [eval('self.NodeOp{}_{}'.format(t, node1)), None]
                
                self.NodeOp_Object[t, node1] = eval('self.NodeOp{}_{}'.format(t, node1))
                
                for node2 in range(self.NodeNum):
                    exec("self.XL{}_{}_{} = self.mdl.binary_var(name = 'XL{}_{}_{}')".format(t, node1, node2, t, node1, node2))
                    
                    self.XL_dic['XL{}_{}_{}'.format(t, node1, node2)] = [eval('self.XL{}_{}_{}'.format(t, node1, node2)), None]
                    
                    self.XL_Object[t, node1, node2] = eval('self.XL{}_{}_{}'.format(t, node1, node2))
                    
                    exec("self.LinkOp{}_{}_{} = self.mdl.continuous_var(name = 'LinkOp{}_{}_{}')".format(t, node1, node2, t, node1, node2))
                
                    self.LinkOp_dic['LinkOp{}_{}_{}'.format(t, node1, node2)] = [eval('self.LinkOp{}_{}_{}'.format(t, node1, node2)), None]
                
                    self.LinkOp_Object[t, node1, node2] = eval('self.LinkOp{}_{}_{}'.format(t, node1, node2))
                    
        #f_tij: Continuous Variable determining the value of the flow
        for t in range(T):
            for node1 in range(self.NodeNum):
                for node2 in range(self.NodeNum):   
                    exec("self.f{}_{}_{} = self.mdl.continuous_var(lb = 0, name = 'f{}_{}_{}')".format(t, node1, node2, t, node1, node2))
                    
                    self.Flow_dic['f{}_{}_{}'.format(t, node1, node2)] = [eval('self.f{}_{}_{}'.format(t, node1, node2)), None]
                    
                    self.Flow_Object[t, node1, node2] = eval('self.f{}_{}_{}'.format(t, node1, node2))
        
    def OpCtDefine(self):
        #tf is no less than tr, f doesn't decrease along the time
        for node1 in range(self.NodeNum):
            self.mdl.add_constraint(self.trN_Object[node1] <= self.tfN_Object[node1])
            
            for node2 in range(self.NodeNum):
                self.mdl.add_constraint(self.trL_Object[node1, node2] <= self.tfL_Object[node1, node2])
                
                for t in range(self.T - 1):
                    self.mdl.add_constraint(self.Flow_Object[t, node1, node2] <= self.Flow_Object[t + 1, node1, node2])
        
        #The Restoration Binary Varibale XN, XL
        #1 when current time step t in [tr, tf], 0 otherwise
        for t in range(self.T):
            for node1 in range(self.NodeNum):
                self.mdl.add_constraint((t <= self.trN_Object[node1] - 1) == (self.XN_Object[t, node1] == 0))
                self.mdl.add_constraint((t >= self.tfN_Object[node1]) == (self.XN_Object[t, node1] == 0))
                self.mdl.add_constraint(self.mdl.sum(self.XN_Object[:, node1]) <= (self.tfN_Object[node1] - self.trN_Object[node1] - 1))
                self.mdl.add_constraint(self.mdl.sum(self.XN_Object[:, node1]) >= (self.tfN_Object[node1] - self.trN_Object[node1] - 1))

                for node2 in range(self.NodeNum):
                    self.mdl.add_constraint((t <= self.trL_Object[node1, node2] - 1) == (self.XL_Object[t, node1, node2] == 0))
                    self.mdl.add_constraint((t >= self.tfL_Object[node1, node2]) == (self.XL_Object[t, node1, node2] == 0))
                    self.mdl.add_constraint(self.mdl.sum(self.XL_Object[:, node1, node2]) <= (self.tfL_Object[node1, node2] - self.trL_Object[node1, node2] - 1))
                    self.mdl.add_constraint(self.mdl.sum(self.XL_Object[:, node1, node2]) >= (self.tfL_Object[node1, node2] - self.trL_Object[node1, node2] - 1))
        
        #The Current Operability Variable
        for t in range(self.T - 1):
            for node1 in range(self.NodeNum):
                if(t == 0):
                    self.mdl.add_constraint(self.NodeOp_Object[t, node1] <= self.InitNodeOp[node1])
                    self.mdl.add_constraint(self.NodeOp_Object[t, node1] >= self.InitNodeOp[node1])
                self.mdl.add_constraint(self.NodeOp_Object[t + 1, node1] >= self.NodeOp_Object[t, node1] + self.NReRatio[node1]*self.XN_Object[t, node1])
                self.mdl.add_constraint(self.NodeOp_Object[t + 1, node1] <= self.NodeOp_Object[t, node1] + self.NReRatio[node1]*self.XN_Object[t, node1])
                for node2 in range(self.NodeNum):
                    if(t == 0):
                        self.mdl.add_constraint(self.LinkOp_Object[t, node1, node2] <= self.InitLinkOp[node1, node2])
                        self.mdl.add_constraint(self.LinkOp_Object[t, node1, node2] >= self.InitLinkOp[node1, node2])
                    self.mdl.add_constraint(self.LinkOp_Object[t + 1, node1, node2] >= self.LinkOp_Object[t, node1, node2] + self.LReRatio[node1, node2]*self.XL_Object[t, node1, node2])
                    self.mdl.add_constraint(self.LinkOp_Object[t + 1, node1, node2] <= self.LinkOp_Object[t, node1, node2] + self.LReRatio[node1, node2]*self.XL_Object[t, node1, node2])
                    
        #Flow no decreasing but always smaller than the operability ratio*capacity
        for t in range(self.T):
            for node1 in range(self.NodeNum):
                for node2 in range(self.NodeNum):
                    if(node1 == node2):#Flow from node i to node i is zero
                        self.mdl.add_constraint(self.Flow_Object[t, node1, node2] <= 0)
                        self.mdl.add_constraint(self.Flow_Object[t, node1, node2] >= 0)
                        
                    #self.mdl.add_constraint(self.Flow_Object[t, node1, node2] <= self.LinkOp_Object[t, node1, node2]*self.LinkCap[node1, node2])
                
                #self.mdl.add_constraint(self.mdl.sum(self.Flow_Object[t, :, node1]) <= self.NodeOp_Object[t, node1]*self.NodeCap[node1]) 
        
        
        #Network Extraction
        #Flow Constraint by the real systems
        for t in range(self.T):
            #Gas Network
            for node in self.Gas.SupplySeries:
                WholeNode = self.Gas.WholeNodeSeries[node]
                #10 - conversion unit
                self.mdl.add_constraint(10*self.mdl.sum(self.Flow_Object[t, :, WholeNode]) >= self.mdl.sum(self.Flow_Object[t, WholeNode, :]))
                self.mdl.add_constraint(10*self.mdl.sum(self.Flow_Object[t, :, WholeNode]) <= self.mdl.sum(self.Flow_Object[t, WholeNode, :]))
            for node in self.Gas.DemandSeries:
                WholeNode = self.Gas.WholeNodeSeries[node]
                self.mdl.add_constraint(self.mdl.sum(self.Flow_Object[t, :, WholeNode]) >= self.mdl.sum(self.Flow_Object[t, WholeNode, :] ))
                self.mdl.add_constraint((self.mdl.sum(self.Flow_Object[t, :, WholeNode]) - self.mdl.sum(self.Flow_Object[t, WholeNode, :])) <= self.Gas.DemandValue[node - self.Gas.DemandSeries[0]])
            
            #Power Network
            for node in self.Power.SupplySeries:
                WholeNode = self.Power.WholeNodeSeries[node]
                #Gas-Power
                self.mdl.add_constraint(self.mdl.sum(self.Flow_Object[t, self.Gas.WholeNodeSeries[self.Gas.DemandSeries], WholeNode]) >= self.mdl.sum(self.Flow_Object[t, WholeNode, :]))
                self.mdl.add_constraint(self.mdl.sum(self.Flow_Object[t, self.Gas.WholeNodeSeries[self.Gas.DemandSeries], WholeNode]) <= self.mdl.sum(self.Flow_Object[t, WholeNode, :]))
                #Water-Power
                #10 - conversion unit
                self.mdl.add_constraint(10*self.mdl.sum(self.Flow_Object[t, self.Water.WholeNodeSeries[self.Water.DemandSeries], WholeNode]) >= self.mdl.sum(self.Flow_Object[t, WholeNode, :]))
                self.mdl.add_constraint(10*self.mdl.sum(self.Flow_Object[t, self.Water.WholeNodeSeries[self.Water.DemandSeries], WholeNode]) <= self.mdl.sum(self.Flow_Object[t, WholeNode, :]))
                
            for node in self.Power.DemandSeries:
                WholeNode = self.Power.WholeNodeSeries[node]
                self.mdl.add_constraint(self.mdl.sum(self.Flow_Object[t, :, WholeNode]) >= self.mdl.sum(self.Flow_Object[t, WholeNode, :]))
                self.mdl.add_constraint((self.mdl.sum(self.Flow_Object[t, :, WholeNode]) - self.mdl.sum(self.Flow_Object[t, WholeNode, :])) <= self.Power.DemandValue[node - self.Power.DemandSeries[0]])
            
            #Water Network
            for node in self.Water.SupplySeries:
                WholeNode = self.Water.WholeNodeSeries[node]
                #Power-Water
                self.mdl.add_constraint(self.mdl.sum(self.Flow_Object[t, :, WholeNode]) >= 1*self.mdl.sum(self.Flow_Object[t, WholeNode, :]))
                self.mdl.add_constraint(self.mdl.sum(self.Flow_Object[t, :, WholeNode]) <= 1*self.mdl.sum(self.Flow_Object[t, WholeNode, :]))
            
            for node in self.Water.DemandSeries:
                WholeNode = self.Water.WholeNodeSeries[node]
                self.mdl.add_constraint(self.mdl.sum(self.Flow_Object[t, :, WholeNode]) >= self.mdl.sum(self.Flow_Object[t, WholeNode, :]))
                self.mdl.add_constraint((self.mdl.sum(self.Flow_Object[t, :, WholeNode]) - self.mdl.sum(self.Flow_Object[t, WholeNode, :])) <= self.Water.DemandValue[node - self.Water.DemandSeries[0]])
            
    def Object(self):
        #String combination
        #DemandValue
        self.DemandValueSum = self.T*(np.sum(self.Gas.DemandValue) + np.sum(self.Power.DemandValue) + np.sum(self.Water.DemandValue))
        #Flow into and out DemandNode
        self.Gas_FlowInDeN = np.zeros([self.T, self.Gas.DemandNum, self.Gas.SupplyNum], dtype = object)
        self.Power_FlowInDeN = np.zeros([self.T, self.Power.DemandNum, self.Power.SupplyNum], dtype = object)
        self.Water_FlowInDeN = np.zeros([self.T, self.Water.DemandNum, self.Water.SupplyNum], dtype = object)
        
        self.Gas_FlowOutDeN = np.zeros([self.T, self.Gas.DemandNum, self.Power.SupplyNum], dtype = object)
        self.Power_FlowOutDeN = np.zeros([self.T, self.Power.DemandNum, self.Water.SupplyNum], dtype = object)
        self.Water_FlowOutDeN = np.zeros([self.T, self.Water.DemandNum, self.Power.SupplyNum], dtype = object)
        
        for t in range(self.T):
            for node1 in self.Gas.DemandSeries:
                WholeNode1 = self.Gas.WholeNodeSeries[node1]
                for node2 in self.Gas.SupplySeries:
                    WholeNode2 = self.Gas.WholeNodeSeries[node2]
                    self.Gas_FlowInDeN[t, node1 - self.Gas.DemandSeries[0], node2 - self.Gas.SupplySeries[0]] = self.Flow_Object[t, WholeNode2, WholeNode1]
                
                for node2 in self.Power.SupplySeries:
                    WholeNode2 = self.Power.WholeNodeSeries[node2]
                    self.Gas_FlowOutDeN[t, node1 - self.Gas.DemandSeries[0], node2 - self.Power.SupplySeries[0]] = self.Flow_Object[t, WholeNode1, WholeNode2]
        
        for t in range(self.T):
            for node1 in self.Power.DemandSeries:
                WholeNode1 = self.Power.WholeNodeSeries[node1]
                for node2 in self.Power.SupplySeries:
                    WholeNode2 = self.Power.WholeNodeSeries[node2]
                    self.Power_FlowInDeN[t, node1 - self.Power.DemandSeries[0], node2 - self.Power.SupplySeries[0]] = self.Flow_Object[t, WholeNode2, WholeNode1]
                
                for node2 in self.Water.SupplySeries:
                    WholeNode2 = self.Water.WholeNodeSeries[node2]
                    self.Power_FlowOutDeN[t, node1 - self.Power.DemandSeries[0], node2 - self.Water.SupplySeries[0]] = self.Flow_Object[t, WholeNode1, WholeNode2]
                    
        for t in range(self.T):
            for node1 in self.Water.DemandSeries:
                WholeNode1 = self.Water.WholeNodeSeries[node1]
                for node2 in self.Water.SupplySeries:
                    WholeNode2 = self.Water.WholeNodeSeries[node2]
                    self.Water_FlowInDeN[t, node1 - self.Water.DemandSeries[0], node2 - self.Water.SupplySeries[0]] = self.Flow_Object[t, WholeNode2, WholeNode1]
                
                for node2 in self.Power.SupplySeries:
                    WholeNode2 = self.Power.WholeNodeSeries[node2]
                    self.Water_FlowOutDeN[t, node1 - self.Water.DemandSeries[0], node2 - self.Power.SupplySeries[0]] = self.Flow_Object[t, WholeNode1, WholeNode2]
        
        self.mdl.minimize(self.DemandValueSum - (self.mdl.sum(self.Gas_FlowInDeN) - self.mdl.sum(self.Gas_FlowOutDeN))\
                          - (self.mdl.sum(self.Power_FlowInDeN) - self.mdl.sum(self.Power_FlowOutDeN))\
                          - (self.mdl.sum(self.Water_FlowInDeN) - self.mdl.sum(self.Water_FlowOutDeN)))
        
    def OpSolve(self):
        print("\nSolving model....")
        self.msol = self.mdl.solve()
        """
        self.msol.display()
        """
            
     

#T, The Whole Simulation Time; t1: The Beginning of the Restoration Time
T, t1 = 5, 3
#The speed of repairment, how much capaciity can it be restored per time unit
beta = 10
Shelby_County_Res = Res_System(T, Shelby_County, t1)
Shelby_County_Res.InitUpdate(Earth)
Shelby_County_Res.RepairRatio(beta)
Shelby_County_Res.OptModelDefine('Sc_op')
Shelby_County_Res.OpVarDefine()
Shelby_County_Res.OpCtDefine()
Shelby_County_Res.Object()
Shelby_County_Res.OpSolve()

Shelby_County_Res.mdl.print_information()