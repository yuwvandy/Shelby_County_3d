# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 10:44:11 2019

@author: wany105
"""

def IntenPerform(IntenList, DisrupLat, DisrupLon, Sys_Perform, Sin_Sys_Perform, X):
    AveSysPerform = np.zeros([len(IntenList), len(X)])
    AveSinSysPerform = np.zeros([len(IntenList), len(X)])
    
    ##Average Performance Quantification
    for i in range(len(IntenList)):
        AveSysPerform[i] = np.average(Sys_Perform[DisrupLon][DisrupLat][IntenList[i]])
    
    for i in range(len(IntenList)):
        AveSinSysPerform[i] = np.average(Sin_Sys_Perform[DisrupLon][DisrupLat][IntenList[i]])
    
    ##Performance Plot        
    color = ['red','green','purple', 'blue','black','pink', 'orange']
    Label = [['I-0','I-3', 'I-4.5', 'I-5', 'I-6', 'I-7','I-10'],['I\'-0','I\'-3', 'I\'-4.5', 'I\'-5', 'I\'-6', 'I\'-7','I\'-10']]
        
    fig1 = plt.figure()
    for i in range(len(IntenList)):
        plt.plot(X, AveSysPerform[i], color = color[i], linestyle = '--', label = Label[0][i])
        plt.plot(X, AveSinSysPerform[i], color = color[i], linestyle = '-', label = Label[1][i])
    plt.xticks(np.arange(0, 20, 1))
    plt.xlabel('Time Step', fontweight='bold')
    plt.ylabel('System Performance', fontweight='bold')
    plt.legend(bbox_to_anchor=(1, 1), loc='upper left', ncol=1, frameon = 0)
    plt.grid(True)
    plt.savefig("SystemPerform.png", dpi = 2000, bbox_inches='tight')
    plt.show()
    
    
    ##Interdependency Strength Quantification and Plot
    fig2 = plt.figure()
    plt.xticks(np.arange(0, 20, 1))
    for i in range(len(IntenList)):
        plt.plot(X, AveSinSysPerform[i] - AveSysPerform[i], color = color[i], linestyle = '-', marker = 'o', label = Label[0][i])
    
    plt.xlabel('Time Step', fontweight='bold')
    plt.ylabel('Interdependency Strength', fontweight='bold')
    plt.legend(bbox_to_anchor=(1, 1), loc='upper left', ncol=1, frameon = 0)
    plt.grid(True)
    plt.savefig("InterStrength1.png", dpi = 2000, bbox_inches='tight')
    plt.show()
    
    return AveSysPerform, AveSinSysPerform

IntIter = np.arange(0, 9, 0.1)
def IntenThresh(IntInter, DisrupLat, DisrupLon, Sys_Perform, Sin_Sys_Perform, X):
    AveSysPerform = np.zeros([len(IntInter), len(X)])
    AveSinSysPerform = np.zeros([len(IntInter), len(X)])
    
    ##Average Performance Quantification
    for i in range(len(IntInter)):
        AveSysPerform[i] = np.average(Sys_Perform[DisrupLon][DisrupLat][i])
    
    for i in range(len(IntInter)):
        AveSinSysPerform[i] = np.average(Sin_Sys_Perform[DisrupLon][DisrupLat][i])
    InterStrength = AveSinSysPerform - AveSysPerform
    ##Strength change with intensity

    fig3 = plt.figure()
    for i in range(len(IntInter)):
        plt.plot(IntInter, InterStrength[0:110, -1])
    for i in range(len(InterStrength[:, -1])):
        if(InterStrength[i, -1] == np.max(InterStrength[:, -1])):
            index = i
    print(index, InterStrength[index, -1])
    plt.scatter(IntInter[index], InterStrength[index, -1], marker = 'o', s = 50, color = 'r')
    
    plt.plot([IntInter[index], IntInter[index]], [0, InterStrength[index, -1]], linestyle = '--', color = 'r')
    plt.plot([0, IntInter[index]], [InterStrength[index, -1], InterStrength[index, -1]], linestyle = '--', color = 'r')
    
    plt.xticks(np.arange(0, 11, 1))
    plt.xlabel('The Magnitude of Earthquake(Mw)',  fontweight='bold')
    plt.ylabel('Interdepedency Strength',  fontweight='bold')
    plt.grid(True)
    plt.savefig("InterStrength2.png", dpi = 2000, bbox_inches='tight') 
    plt.show()
    
    
    
    return InterStrength

##Sys_Perform = np.load(r"C:\Users\10624\OneDrive - Vanderbilt\Research\ShelbyCounty_Model\Result_Intensity\Sys_Perform.npy", allow_pickle = True)
##Sin_Sys_Perform = np.load(r"C:\Users\10624\OneDrive - Vanderbilt\Research\ShelbyCounty_Model\Result_Intensity\Sin_Sys_Perform.npy", allow_pickle = True)

IntIter = np.arange(0, 11, 0.1)
IntenList = [0, 30, 45, 50, 60, 70, 100]
DisrupLat = 0
DisrupLon = 0
X = np.arange(0, 20, 1)
A, B = IntenPerform(IntenList, DisrupLat, DisrupLon, Sys_Perform, Sin_Sys_Perform, X)
C = IntenThresh(IntIter, DisrupLat, DisrupLon, Sys_Perform, Sin_Sys_Perform, X)


##Heatmap of Earthquake Location Affection
"""
import seaborn as sns
def EpicenterEffect(LonIter, LatIter, IntIter, Sys_Perform, Sin_Sys_Perform, Diff_Perform):
    ##Variable Initialization
    Label = ['']
    
    AveSysVul = np.array([[[None]*len(IntIter)]*len(LatIter)]*len(LonIter))
    AveSinSysVul = np.array([[[None]*len(IntIter)]*len(LatIter)]*len(LonIter))
    AveInterStrTime = np.array([[[None]*len(IntIter)]*len(LatIter)]*len(LonIter))
    AveInterStr = np.array([[[None]*len(IntIter)]*len(LatIter)]*len(LonIter))
    
    for i in range(len(LonIter)):
        for j in range(len(LatIter)):
            for k in range(len(IntIter)):
                AveSysVul[i][j][k] = 1 - np.average(Sys_Perform[i][j][k])
                AveSinSysVul[i][j][k] = 1 - np.average(Sin_Sys_Perform[i][j][k])
                AveInterStrTime[i][j][k] = AveSysVul[i][j][k] - AveSinSysVul[i][j][k]
                AveInterStr[i][j][k] = AveInterStrTime[i][j][k][-1]

    ##Heatmap          
    for i in range(len(IntIter)):
        ax = sns.heatmap(np.array(list(AveInterStr[:, :, i]), dtype = np.float))
        bottom, top = ax.get_xlim()
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_title('InterDependence Strength with the Earthquake Intensity of {}'.format(IntIter[i]))
    
    plt.savefig("location3.png", dpi = 2000, bbox_inches='tight') 

"""