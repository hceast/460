# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d
from adjacent import get_adjacent
from haversine import haversine

deliv_517 = pd.read_excel("May_17_Delivery_Data.xlsx", sheet_name = "Delivery Data")
deliv_517 = deliv_517[["Longitude", "Latitude", "Delivery Volume"]].copy()

dist_center = pd.read_excel("May_17_Delivery_Data.xlsx", sheet_name = "Centers")
dist_center = dist_center[["Longitude", "Latitude"]].copy()

center_vols = [0, 0, 0]
se1 = pd.Series(center_vols)
dist_center["Delivery Volume"] = se1.values 

deliv_517 = pd.concat([deliv_517, dist_center[["Longitude", "Latitude", "Delivery Volume"]]], ignore_index = True)

#%%
vor = Voronoi(deliv_517[["Longitude", "Latitude"]], qhull_options = "Qbb Qc Qx")
voronoi_plot_2d(vor)
fig = plt.figure()
plt.show()

all_adj = []

i=0
for i in range(len(vor.points)):
    point = (vor.points[i][0], vor.points[i][1])
    adj_pts = get_adjacent(point, vor)
    all_adj.append(adj_pts)
    
se2 = pd.Series(all_adj)
deliv_517["Adj Nodes"] = se2.values

#%%
from Node import node
from Cluster import cluster

#Unused scripts that may be useful
"""
i = 0
for i in range(len(Node)):
    if (Node[i].isOutside == False):
        Outside.remove(Node[i].index)
"""
"""
j = 0
    for j in range(len(Cluster[i].nodes_idx)):
        if (Cluster[i].nodes_idx[j] not in Assigned_Nodes):
            Assigned_Nodes.append(Cluster[i].nodes_idx[j])
"""
"""
Cluster[i].Nodes.append(Cluster[i].centroid.index)

Cluster[i].nodes_idx.append(Cluster[i].centroid.index)
"""

#Create Node set
Node = [node(i, (deliv_517["Longitude"][i], deliv_517["Latitude"][i]), deliv_517["Delivery Volume"][i], deliv_517["Adj Nodes"][i]) for i in range(len(deliv_517))]

#Establish set Outside, which tracks the nodes that are not assigned to a cluster
Outside = []

i = 0
for i in range(len(Node)):
    Outside.append(Node[i].index)

#Create set that tracks the nodes that have been assigned to a cluster
Assigned_Nodes = []

#Cluster Initialization
Cluster = [cluster(Node[i], 999999999999) for i in range(465,468)]

i = 0
for i in range(len(Cluster)):
    Cluster[i].index = i
    
#Adding the centroid to the cluster   
i = 0
for i in range(len(Cluster)):
    
    Cluster[i].Nodes.append(Cluster[i].centroid)
    Cluster[i].nodes_idx.append(Cluster[i].centroid.index)
    Cluster[i].centroid.cluster = Cluster[i].index
    Cluster[i].centroid.isRoot = True
    
    #Update Outside
    Cluster[i].centroid.isOutside = False
    Outside.remove(Cluster[i].centroid.index)
    
    #Update Assigned_Nodes
    Assigned_Nodes.append(Cluster[i].centroid.index)
    
    #Update predecessor path information
    Cluster[i].centroid.Pred = -1
    Cluster[i].centroid.pred_idx = -1
    
    #Calculate distance function value for node
    Cluster[i].centroid.distance = Cluster[i].centroid.calc_distance()
    
i = 0
for i in range(len(Cluster)):
    Cluster[i].reachable = []
    Cluster[i].extensible = []
    
    j = 0
    for j in range(len(Cluster[i].Nodes)):
        Cluster[i].Nodes[j].reachable = []
        
        k = 0
        for k in range(len(Cluster[i].Nodes[j].adj_nodes)):
            if (Node[Cluster[i].Nodes[j].adj_nodes[k]].isOutside == True):
                Node[Cluster[i].Nodes[j].adj_nodes[k]].isReachable == True
                Cluster[i].Nodes[j].reachable.append(Cluster[i].Nodes[j].adj_nodes[k])
                if (Cluster[i].Nodes[j].adj_nodes[k] not in Cluster[i].reachable):
                    Cluster[i].reachable.append(Cluster[i].Nodes[j].adj_nodes[k])
            else:
                Node[Cluster[i].Nodes[j].adj_nodes[k]].isReachable == False
        if (Cluster[i].Nodes[j].reachable != []):
            Cluster[i].Nodes[j].isExtensible = True
            if (Cluster[i].Nodes[j].index not in Cluster[i].extensible):
                Cluster[i].extensible.append(Cluster[i].Nodes[j].index)
        else:
            Cluster[i].Nodes[j].isExtensible = False
    if (Cluster[i].extensible != []):
            Cluster[i].isExtensible = True

#Create set containing all Extensible nodes in all clusters
Extensible = []
#Create set containing all Reachable nodes in all clusters
Reachable = []
               
i = 0
for i in range(len(Cluster)):
    j = 0
    #Step through the cluster's extensible set
    for j in range(len(Cluster[i].extensible)):
        #Update global extensible set
        Extensible.append(Cluster[i].extensible[j])
 
i = 0
for i in range(len(Cluster)): 
    #Establish global reachable set
    j = 0
    for j in range(len(Cluster[i].reachable)):          
    #Add node to global reachable set if it is not already in the set
        if (Cluster[i].reachable[j] not in Reachable):
            Reachable.append(Cluster[i].reachable[j])         
                
#%%
i =0
for i in range(0, 456):
    Best_Reachable_Dist = []
    C_star = ""
    q_star = ""
    p_star = ""
    
    i = 0
    for i in range(len(Cluster)):
        best_dist = "None"
        
        j = 0
        for j in range(len(Cluster[i].extensible)):
            
            k = 0
            for k in range(len(Node[Cluster[i].extensible[j]].reachable)):
                Node[Node[Cluster[i].extensible[j]].reachable[k]].min_reachable_dist = Node[Cluster[i].extensible[j]].distance + haversine(Node[Cluster[i].extensible[j]].coords, Node[Node[Cluster[i].extensible[j]].reachable[k]].coords)
                if(best_dist == "None"):
                    best_dist = Node[Node[Cluster[i].extensible[j]].reachable[k]].min_reachable_dist
                    Cluster[i].best_extensible = Cluster[i].extensible[j]
                    Cluster[i].best_reachable = Node[Cluster[i].extensible[j]].reachable[k]
                if (Node[Node[Cluster[i].extensible[j]].reachable[k]].min_reachable_dist < best_dist):
                    best_dist = Node[Node[Cluster[i].extensible[j]].reachable[k]].min_reachable_dist
                    Cluster[i].best_extensible = Cluster[i].extensible[j]
                    Cluster[i].best_reachable = Node[Cluster[i].extensible[j]].reachable[k]
                    
        Best_Reachable_Dist.append(Node[Cluster[i].best_reachable].min_reachable_dist)
    
    C_star = Best_Reachable_Dist.index(min(Best_Reachable_Dist))
    q_star = Cluster[C_star].best_reachable
    p_star = Cluster[C_star].best_extensible
                    
    #Add q_star to Cluster
    Cluster[C_star].Nodes.append(Node[q_star])
    Cluster[C_star].nodes_idx.append(q_star)
    Node[q_star].cluster = Cluster[C_star].index
    
    Cluster[C_star].weight += Node[q_star].weight
    Cluster[C_star].capac -= Cluster[C_star].weight
    
    #Update Outside
    Node[q_star].isOutside = False
    if (Node[q_star].index in Outside):
        Outside.remove(Node[q_star].index)
    Node[q_star].isReachable = False
    
    #Update Assigned_Nodes
    Assigned_Nodes.append(Node[q_star].index)
    
    #Update predecessor path information about q_star
    Node[q_star].Pred.append(Node[p_star])
    Node[q_star].pred_idx.append(Node[p_star].index)
    Node[p_star].child = q_star
    
    #Calculate distance function value for node
    Node[q_star].distance = 0
    Node[q_star].distance = Node[q_star].calc_distance()
    
    #Updating extensible and reachable information
    Extensible = []
    Reachable = []
    
    i = 0
    for i in range(len(Cluster)):
        Cluster[i].reachable = []
        Cluster[i].extensible = []
        
        j = 0
        for j in range(len(Cluster[i].Nodes)):
            Cluster[i].Nodes[j].reachable = []
            
            k = 0
            for k in range(len(Cluster[i].Nodes[j].adj_nodes)):
                if (Node[Cluster[i].Nodes[j].adj_nodes[k]].isOutside == True):
                    Node[Cluster[i].Nodes[j].adj_nodes[k]].isReachable == True
                    Cluster[i].Nodes[j].reachable.append(Cluster[i].Nodes[j].adj_nodes[k])
                    if (Cluster[i].Nodes[j].adj_nodes[k] not in Cluster[i].reachable):
                        Cluster[i].reachable.append(Cluster[i].Nodes[j].adj_nodes[k])
                else:
                    Node[Cluster[i].Nodes[j].adj_nodes[k]].isReachable == False
            if (Cluster[i].Nodes[j].reachable != []):
                Cluster[i].Nodes[j].isExtensible = True
                if (Cluster[i].Nodes[j].index not in Cluster[i].extensible):
                    Cluster[i].extensible.append(Cluster[i].Nodes[j].index)
            else:
                Cluster[i].Nodes[j].isExtensible = False
        if (Cluster[i].extensible != []):
                Cluster[i].isExtensible = True
"""
i = 0
for i in range(len(Cluster)):
    j = 0
    #Step through the cluster's extensible set
    for j in range(len(Cluster[i].extensible)):
        #Update global extensible set
        Extensible.append(Cluster[i].extensible[j])
 
i = 0
for i in range(len(Cluster)): 
    #Establish global reachable set
    j = 0
    for j in range(len(Cluster[i].reachable)):          
    #Add node to global reachable set if it is not already in the set
        if (Cluster[i].reachable[j] not in Reachable):
            Reachable.append(Cluster[i].reachable[j])  
"""
