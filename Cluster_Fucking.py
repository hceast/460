# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import random
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d
from adjacent import get_adjacent
from haversine import haversine

deliv_517 = pd.read_excel("May_17_Delivery_Data.xlsx", sheet_name = "Delivery Data")
deliv_517 = deliv_517[["Longitude", "Latitude", "Delivery Volume"]].copy()

dist_center = pd.read_excel("May_17_Delivery_Data.xlsx", sheet_name = "Centers")
dist_center = dist_center[["Longitude", "Latitude"]].copy()

target_weight = (deliv_517["Delivery Volume"].sum()/3)
avg_weight = deliv_517["Delivery Volume"].mean()

se1 = [999999999, 999999999, 999999999]
dist_center["Delivery Volume"] = se1

deliv_517 = pd.concat([deliv_517, dist_center[["Longitude", "Latitude", "Delivery Volume"]]], ignore_index = True)

#%%
vor = Voronoi(deliv_517[["Longitude", "Latitude"]], qhull_options = "Qbb Qc Qx")
#voronoi_plot_2d(vor)
#fig = plt.figure()
#plt.show()

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
Cluster = [cluster(Node[i], target_weight, deliv_517["Delivery Volume"][i]) for i in range(465,468)]

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
l = 0
for l in range(0, 466):
    
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
     
    C_star = ""
    q_star = ""
    p_star = ""    


#The best reachable node from each cluster is determined. The cluster to extend is selected to maximize the improvement in reaching the target weight
#The option to weight the improvement agaisnt min reachable distance is included. Ties are broken with min reachable distance   
    """
    Weight_Improvement = []
    
    i = 0
    for i in range(len(Cluster)):
    
        current_deviation = ""
        new_deviation = ""
        
        current_deviation = abs(Cluster[i].weight - Cluster[i].balance_target)
        new_deviation = abs((Cluster[i].weight + Node[Cluster[i].best_reachable].weight) - Cluster[i].balance_target)
        
        Weight_Improvement.append(current_deviation - new_deviation)
        #Weight_Improvement.append((current_deviation - new_deviation)*(1/Node[Cluster[i].best_reachable].min_reachable_dist))
    
    C_star = Weight_Improvement.index(max(Weight_Improvement))
    
    best_improvement = max(Weight_Improvement)
    candidates = []
    
    i = 0
    for i in range(len(Weight_Improvement)):
        if (Weight_Improvement[i] == best_improvement):
            candidates.append(i)
            
    if (len(candidates) == 1):
        C_star = Weight_Improvement.index(max(Weight_Improvement))
    else:
        choice = random.randint(min(range(len(candidates))), max(range(len(candidates))))
        C_star = candidates[choice]
    
        Min_Reach_Dist = []
        
        i = 0
        for i in range(len(candidates)):
            Min_Reach_Dist.append(Node[Cluster[candidates[i]].best_reachable].min_reachable_dist)
            #Weight_Improvement[candidates[i]] = (Weight_Improvement[candidates[i]]/Node[Cluster[candidates[i]].best_reachable].min_reachable_dist)
            
        C_star = Min_Reach_Dist.index(min(Min_Reach_Dist))
        #C_star = Weight_Improvement.index(max(Weight_Improvement))
    """
    
#Decision of what node to add to what cluster is made purely to minimize distance.
#The option to use a weighting factor that applied to the distance measure is included.
    
    Best_Reach_Dist = []
    
    i = 0
    for i in range(len(Cluster)):
       
        #weight_factor = (Cluster[i].weight + Node[Cluster[i].best_reachable].weight) / Cluster[i].balance_target
        #Best_Reach_Dist.append(Node[Cluster[i].best_reachable].min_reachable_dist * weight_factor)
        
        Best_Reach_Dist.append(Node[Cluster[i].best_reachable].min_reachable_dist)
    
    C_star = Best_Reach_Dist.index(min(Best_Reach_Dist))

#Selects cluster with fewest elements.   
    """
    Card = [len(Cluster[i].Nodes) for i in range(len(Cluster))]
    min_card = min(Card)
    candidates = []
    
    i = 0
    for i in range(len(Card)):
        if (Card[i] == min_card):
            candidates.append(i)
            
    if (len(candidates) == 1):
        C_star = Card.index(min_card)
    else:
        
        Min_Reach_Dist = []
        
        i = 0
        for i in range(len(candidates)):
            Min_Reach_Dist.append(Node[Cluster[candidates[i]].best_reachable].min_reachable_dist)
        
        C_star = Min_Reach_Dist.index(min(Min_Reach_Dist))
        
        choice = random.randint(min(range(len(candidates))), max(range(len(candidates))))
        C_star = candidates[choice]
    """
    q_star = Cluster[C_star].best_reachable
    p_star = Cluster[C_star].best_extensible
                    
    #Add q_star to Cluster
    Cluster[C_star].Nodes.append(Node[q_star])
    Cluster[C_star].nodes_idx.append(q_star)
    Node[q_star].cluster = Cluster[C_star].index
    
    Cluster[C_star].weight += Node[q_star].weight
    Cluster[C_star].capac -= Node[q_star].weight
    
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
#%%
#Plotting

print(len(Cluster[0].Nodes))
print(len(Cluster[0].Nodes))
print(len(Cluster[2].Nodes))

cluster_0_x = []
cluster_0_y = []
cluster_1_x = []
cluster_1_y = []
cluster_2_x = []
cluster_2_y = []

for i in range(len(Cluster[0].Nodes)):
    cluster_0_x += [Cluster[0].Nodes[i].coords[0]]
    cluster_0_y += [Cluster[0].Nodes[i].coords[1]]

for i in range(len(Cluster[1].Nodes)):
    cluster_1_x += [Cluster[1].Nodes[i].coords[0]]
    cluster_1_y += [Cluster[1].Nodes[i].coords[1]]
    
for i in range(len(Cluster[2].Nodes)):
    cluster_2_x += [Cluster[2].Nodes[i].coords[0]]
    cluster_2_y += [Cluster[2].Nodes[i].coords[1]]

c0 = pd.DataFrame({"X": cluster_0_x, "Y": cluster_0_y})
c1 = pd.DataFrame({"X": cluster_1_x, "Y": cluster_1_y})
c2 = pd.DataFrame({"X": cluster_2_x, "Y": cluster_2_y})

ax = c0.plot(x = "X", y = "Y", kind = "scatter", c = "Red")
c1.plot(x = "X", y = "Y", kind = "scatter", c = "Blue", ax = ax)
c2.plot(x = "X", y = "Y", kind = "scatter", c = "Green", ax = ax)
