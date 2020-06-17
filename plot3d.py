# -*- coding: utf-8 -*-
"""
Created on Sun Dec 22 12:46:08 2019

@author: 10624
"""

from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt
def Plot3d(System):
    fig = plt.figure(figsize = (20, 15))
    ax = fig.add_subplot(111, projection = '3d')
    ZZ = [0, 50, 100]
    temp = 0
    for Network in System.Networks:
        ##Plane Coordinates
        x = np.arange(0, 70, 1)
        y = np.arange(0, 70, 1)
        x, y = np.meshgrid(x, y)
        z = np.array([[ZZ[temp]]*len(x)]*len(y), dtype = float)
        temp += 1
        
        ##Network Coordinates
        X = Network.X/1000
        Y = Network.Y/1000
        if(Network.Name == 'Gas'):
            Z = np.array([0]*Network.NodeNum, dtype = float)
        if(Network.Name == 'Power'):
            Z = np.array([50]*Network.NodeNum, dtype = float)
        if(Network.Name == 'Water'):
            Z = np.array([100]*Network.NodeNum, dtype = float)
        Network.Z = Z
        
        ##Network Nodes Plots
        ax.scatter3D(X[Network.SupplySeries], Y[Network.SupplySeries], Z[Network.SupplySeries], depthshade = False, zdir = 'z', marker = 's', color = Network.Color, label = Network.SupplyName, s = 40)
        ax.scatter3D(X[Network.DemandSeries], Y[Network.DemandSeries], Z[Network.DemandSeries], depthshade = False, zdir = 'z', marker = 'o', label = Network.DemandName, s = 40, facecolors = 'none', edgecolors = Network.Color)
        ax.plot_surface(x, y, z, linewidth=0, antialiased=False, alpha=0.05, color = Network.Color)

    ##link Plots
    System.CoorlistZ = np.concatenate([System.Networks[0].Z, System.Networks[1].Z, System.Networks[2].Z])    
    Normalize_Flow = Normalize(System.FlowAdj[0])
    for i in range(System.NodeNum):
            for j in range(System.NodeNum):
                if(System.Adj[i][j] == 1):
                    if((i in Water.WholeNodeSeries and j in Water.WholeNodeSeries) or (i in Power.WholeNodeSeries and j in Power.WholeNodeSeries) or (i in Gas.WholeNodeSeries and j in Gas.WholeNodeSeries)):
                        ax.plot([System.CoorlistX[i]/1000, System.CoorlistX[j]/1000], [System.CoorlistY[i]/1000, System.CoorlistY[j]/1000], [System.CoorlistZ[i], System.CoorlistZ[j]], 'purple', lw = 7.5*Normalize_Flow[i][j])        
                    else:
                        ax.plot([System.CoorlistX[i]/1000, System.CoorlistX[j]/1000], [System.CoorlistY[i]/1000, System.CoorlistY[j]/1000], [System.CoorlistZ[i], System.CoorlistZ[j]], 'black', lw = 7.5*Normalize_Flow[i][j])        
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.legend(frameon = 0)
#    plt.savefig("graph_conv1.png", dpi = 3000) 
    
Plot3d(Shelby_County)
    
    




