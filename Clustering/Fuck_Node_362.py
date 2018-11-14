# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
# Importing packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d
from adjacent import get_adjacent
from haversine import haversine

#Reads in the excel file that contains all of the May 17th deliveries, and constructs a data frame
delivs = pd.read_excel("May_17_Delivery_Data.xlsx", sheet_name = "Delivery Data")
#Exclude addresses from the data frame, we only need Lat/Longs
delivs = delivs[["Longitude", "Latitude", "Delivery Volume"]].copy()

#Establish targets for balancing
target_card = len(delivs)/3
target_weight = [(delivs["Delivery Volume"].sum()/3), (delivs["Delivery Volume"].sum()/3), (delivs["Delivery Volume"].sum()/3)]
#target_weight = [(delivs["Delivery Volume"].sum()*(3/8)), (delivs["Delivery Volume"].sum()*(1/4)), (delivs["Delivery Volume"].sum()*(3/8))]

#Create data frame containing distribution center information
dist_center = pd.read_excel("May_17_Delivery_Data.xlsx", sheet_name = "Centers")
dist_center = dist_center[["Longitude", "Latitude"]].copy()

#Append weight-balance-target volumes to the dataframe. Name the column "Delivery Volume" for sake of simplicity with the
#concatenation below
dist_center["Delivery Volume"] = target_weight

#Make everything one data frame. Facility locations are at the bottom of the data frame.
delivs = pd.concat([delivs, dist_center[["Longitude", "Latitude", "Delivery Volume"]]], ignore_index = True)

#Distance Matrix that gives the great-circle distance between each pair of nodes
D_Mat = np.zeros((len(delivs), len(delivs))) 

i = 0
for i in range(len(delivs)):
    coords1 = (delivs["Longitude"][i], delivs["Latitude"][i])
    
    j = 0
    for j in range(len(delivs)):
        coords2 = (delivs["Longitude"][j], delivs["Latitude"][j])
        D_Mat[i][j] = haversine(coords1, coords2)

#%%
#Create Voronoi diagram that will be the basis for clustering
vor = Voronoi(delivs[["Longitude", "Latitude"]], qhull_options = "Qbb Qc Qx")
#voronoi_plot_2d(vor)
#fig = plt.figure()
#plt.show()

#Determine node adjacencies
all_adj = []

i = 0
for i in range(len(vor.points)):
    point = (vor.points[i][0], vor.points[i][1])
    adj_pts = get_adjacent(point, vor)
    all_adj.append(adj_pts)

#Append list of node adjacencies to deliv-517 dataframe   
se2 = pd.Series(all_adj)
delivs["Adj Nodes"] = se2.values

#%%
"""
#Reachability factor

i = 0
for i in range(len(Outside)):
    n_outside = 0
    
    j = 0
    for j in range(len(Node[Outside[i]].adj_nodes)):
        if (Node[Node[Outside[i]].adj_nodes[j]].isOutside == True):
            n_outside += 1
    Node[Outside[i]].reachability = n_outside/len(Outside)
"""   
"""              
i = 0
for i in range(len(Cluster)):
    
    j = 0
    for j in range(len(Cluster[i].Nodes)):
        
        k = 0
        for k in range(len(Cluster[i].Nodes[j].adj_nodes)):
            if (Node[Cluster[i].Nodes[j].adj_nodes[k]].cluster != i):
                Cluster[i].Nodes[j].isBoundary = True
                Cluster[i].boundary.append(Cluster[i].Nodes[j].index)
                break
"""
"""
i = 0
for i in range(len(Node)):
    
    if (Node[i].isBoundary == True):
    
        j = 0
        for j in range(len(Node[i].adj_nodes)):
            
            if ((Node[Node[i].adj_nodes[j]].isBoundary == True) and (Node[i].cluster != Node[Node[i].adj_nodes[j]].cluster)):
                Node[i].moves.append(Node[Node[i].adj_nodes[j]].cluster)
"""
"""
num_eq = 0
i = 0
for i in range(len(Node)):
    if (Node[i].index == Outside[i].index):
        num_eq += 1
"""
#%%
#Import node and cluster class objects
from Node import node
from Cluster import cluster

#Create Node set
Node = [node(i, (delivs["Longitude"][i], delivs["Latitude"][i]), delivs["Delivery Volume"][i], delivs["Adj Nodes"][i]) for i in range(len(delivs))]

#Establish set Outside, which tracks the nodes that are not assigned to a cluster
Outside = [Node[i] for i in range(len(Node))]

#Create set that tracks the nodes that have been assigned to a cluster
Assigned_Nodes = []

#Cluster Initialization:

#Clusters take a Node object that will be the centroid, a balance target for the cluster, and a capacity.
#This line creates 3 clusters with the facilities as the central locations.
Cluster = [cluster(Node[i], target_card, delivs["Delivery Volume"][i], 999999999) for i in range(455,458)]

#This section of code assigns what are considered to be "better" initial centroids.
"""
Cluster = []
Cluster.append(cluster(Node[376], target_weight[i], 999999999))
Cluster.append(cluster(Node[49], target_weight[i], 999999999))
Cluster.append(cluster(Node[68], target_weight[i], 999999999))
"""
#Give clusters indicies for easy indentification
i = 0
for i in range(len(Cluster)):
    Cluster[i].index = i
    
#Update cluster information
i = 0
for i in range(len(Cluster)):
    
    Cluster[i].Nodes.append(Cluster[i].centroid)

    Cluster[i].nodes_idx.append(Cluster[i].centroid.index)
    
    #Makes sure the centroid node object has the index of the cluster to which it is assigned
    Cluster[i].centroid.cluster = Cluster[i].index
    #Centroid is centroid
    Cluster[i].centroid.isRoot = True
    
    #Update Outside, as the centroids are now part of the clusters
    Cluster[i].centroid.isOutside = False
    Outside.remove(Cluster[i].centroid)
    
    #Update Assigned_Nodes
    Assigned_Nodes.append(Cluster[i].centroid)
    
    #Calculate distance function value for node, which for the centroid will be zero
    Cluster[i].centroid.distance = Cluster[i].centroid.calc_distance()

#Determine the extensible and reachable nodes
i = 0
for i in range(len(Assigned_Nodes)):
    Assigned_Nodes[i].isReachable = False
    Assigned_Nodes[i].isExtensible = False
    Assigned_Nodes[i].reachable = []
    
    j = 0
    for j in range(len(Assigned_Nodes[i].adj_nodes)):
        if ((Node[Assigned_Nodes[i].adj_nodes[j]] in Outside) == True):
            
            Node[Assigned_Nodes[i].adj_nodes[j]].isReachable = True
            Assigned_Nodes[i].reachable.append(Assigned_Nodes[i].adj_nodes[j])
            
    if ((len(Assigned_Nodes[i].reachable)) != 0):
        Assigned_Nodes[i].isExtensible = True
    else:
        Assigned_Nodes[i].isExtensible = True
            
i = 0
for i in range(len(Cluster)):
    Cluster[i].extensible = []
    
    j = 0
    for j in range(len(Cluster[i].Nodes)):
        if ((Cluster[i].Nodes[j].isExtensible) == True):
            if ((Cluster[i].Nodes[j].index not in Cluster[i].extensible) == True):
                Cluster[i].extensible.append(Cluster[i].Nodes[j].index)
            
        k = 0
        for k in range(len(Cluster[i].Nodes[j].adj_nodes)):
            if ((Node[Cluster[i].Nodes[j].adj_nodes[k]].isReachable) == True):
                if ((Cluster[i].Nodes[j].adj_nodes[k] not in Cluster[i].reachable) == True):
                    Cluster[i].reachable.append(Cluster[i].Nodes[j].adj_nodes[k])
                    
    if ((len(Cluster[i].extensible)) != 0):
        Cluster[i].isExtensible = True
    else:
        Cluster[i].isExtensible = False

Reachable_idx = []
Extensible_idx = []
        
i = 0
for i in range(len(Cluster)):
    
    j = 0
    for j in range(len(Cluster[i].reachable)):
        if ((Cluster[i].reachable[j] not in Reachable_idx) == True):
            Reachable_idx.append(Cluster[i].reachable[j])
            
    j = 0
    for j in range(len(Cluster[i].extensible)):
        if ((Cluster[i].extensible[j] not in Extensible_idx) == True):
            Extensible_idx.append(Cluster[i].extensible[j])
        
#Create set containing all Extensible nodes in all clusters
Extensible = []
               
i = 0
for i in range(len(Node)):
    if (Node[i].isExtensible == True):
        Extensible.append(Node[i])

i = 0        
for i in range(len(Extensible)):
    if ((Extensible[i].index not in Extensible_idx) == True):
        print("Node " + str(Extensible[i].index) + " is in Extensible but is not in Extensible_idx.")

#Create set containing all Reachable nodes in all clusters
Reachable = []

i = 0
for i in range(len(Node)):
    if (Node[i].isReachable == True):
        Reachable.append(Node[i])
        
i = 0        
for i in range(len(Reachable)):
    if ((Reachable[i].index not in Reachable_idx) == True):
        print("Node " + str(Reachable[i].index) + " is in Reachable but is not in Reachable_idx.")
        
#%%
while (len(Outside) > 1):
#l = 0
#for l in range(0, 455):
    
    n_Outside = len(Outside)
    n_Assigned = len(Assigned_Nodes)
    
    in_clusters1 = 0
    
    i = 0
    for i in range(len(Cluster)):
        in_clusters1 += len(Cluster[i].Nodes)
    
    #Identify the best reachable node for every extensible node, and the best extensible
    #node for every reachable node.
    i = 0
    for i in range(len(Extensible)):
        Reach_Dist = []
        Dist = []
        
        j = 0
        for j in range(len(Extensible[i].adj_nodes)):
            if (Node[Extensible[i].adj_nodes[j]].isReachable == True):
                Reach_Dist.append([Extensible[i].adj_nodes[j], Extensible[i].distance + haversine(Extensible[i].coords, Node[Extensible[i].adj_nodes[j]].coords)])
                
        Dist = [Reach_Dist[j][1] for j in range(len(Reach_Dist))]
        
        Extensible[i].best_reach = Node[Reach_Dist[Dist.index(min(Dist))][0]]
        
    i = 0
    for i in range(len(Reachable)):
        Ext_Dist = []
        Dist = []
        
        j = 0
        for j in range(len(Reachable[i].adj_nodes)):
            if (Node[Reachable[i].adj_nodes[j]].isExtensible == True):
                Ext_Dist.append([Reachable[i].adj_nodes[j], Node[Reachable[i].adj_nodes[j]].distance + haversine(Node[Reachable[i].adj_nodes[j]].coords, Reachable[i].coords)])
        
        Dist = [Ext_Dist[j][1] for j in range(len(Ext_Dist))]
        
        Reachable[i].best_ext = Node[Ext_Dist[Dist.index(min(Dist))][0]]
        
        Reachable[i].preferred_cluster = Node[Ext_Dist[Dist.index(min(Dist))][0]].cluster
        
        Reachable[i].min_reachable_dist = Ext_Dist[Dist.index(min(Dist))][1]
   
    #Identify the best reachable and extensible nodes for each cluster.
    i = 0
    for i in range(len(Cluster)):
        
        if (Cluster[i].isExtensible == True):
            Ext_Reach_Dist = []
            Dist = []
            
            j = 0
            for j in range(len(Cluster[i].Nodes)):
                
                if((Cluster[i].Nodes[j].index in Cluster[i].extensible) == True):
                    Ext_Reach_Dist.append([Cluster[i].Nodes[j].index, Cluster[i].Nodes[j].best_reach.index, Cluster[i].Nodes[j].best_reach.min_reachable_dist])
            
            Dist = [Ext_Reach_Dist[j][2] for j in range(len(Ext_Reach_Dist))]
            
            Cluster[i].best_extensible = Node[Ext_Reach_Dist[Dist.index(min(Dist))][0]]
            
            Cluster[i].best_reachable = Node[Ext_Reach_Dist[Dist.index(min(Dist))][1]]
            
    
    #Selected cluster, selected reachable (q_star) and selected extensible (p-star)
    C_star = ""
    q_star = ""
    p_star = "" 
    
    #Determine C_star
    Decision_Mat = []
    
    i = 0
    for i in range(len(Cluster)):
        if(Cluster[i].isExtensible == True):
            Decision_Mat.append([i, len(Cluster[i].Nodes), ((abs(Cluster[i].weight - Cluster[i].target_weight)) - (abs((Cluster[i].weight + Cluster[i].best_reachable.weight) - Cluster[i].target_weight))), Cluster[i].best_reachable.min_reachable_dist])

    Card = [Decision_Mat[i][1] for i in range(len(Decision_Mat))]
    min_card = min(Card)
    candidates = []
    
    #Find the ones that tie
    i = 0
    for i in range(len(Decision_Mat)):
        if (Decision_Mat[i][1] == min_card):
            candidates.append(Decision_Mat[i])
    
    if (len(candidates) > 1):
        
        #Find the one that also minimizes distance.
        Min_Reach_Dist = [candidates[i][3] for i in range(len(candidates))]
        
        C_star = Cluster[candidates[Min_Reach_Dist.index(min(Min_Reach_Dist))][0]]
        """
        Weight_Improvement = [candidates[i][2] for i in range(len(candidates))]
        
        C_star = Cluster[candidates[Weight_Improvement.index(max(Weight_Improvement))][0]]
        """
    if (len(candidates) == 1):
        C_star = Cluster[candidates[0][0]]
    
    #Once you know your C_star, you know your q_star which is associated with a p_star
    q_star = C_star.best_reachable
    p_star = C_star.best_extensible
    
    #Update Outside
    q_star.isOutside = False
    Outside.remove(q_star)
    q_star.isReachable = False

    delta_Outside = n_Outside - len(Outside)

    #Update Assigned_Nodes
    Assigned_Nodes.append(q_star)
    delta_Assigned = len(Assigned_Nodes) - n_Assigned
    
    #Assign q_star to C_star, update C_star, update Node set.
    #Add q_star to Cluster
    C_star.Nodes.append(q_star)
    C_star.nodes_idx.append(q_star.index)
    q_star.cluster = C_star.index
    
    in_clusters2 = 0
    
    i = 0
    for i in range(len(Cluster)):
        in_clusters2 += len(Cluster[i].Nodes)
        
    delta_clustered = in_clusters2 - in_clusters1
    
    #Update cluster weight and capacity
    C_star.weight += q_star.weight
    C_star.capac -= q_star.weight
    
    #Update predecessor path information about q_star
    q_star.Pred.extend(p_star.Pred)
    q_star.Pred.append(p_star)
    
    q_star.pred_idx.extend(p_star.pred_idx)
    q_star.pred_idx.append(p_star.index)
    
    #Set q_star as the immediate successor of p_star
    p_star.child = q_star
    
    #Calculate distance function value for node
    q_star.distance = q_star.calc_distance()
    
    #Update extensible and reachable information.
    Extensible = []
    Reachable = []
    Extensible_idx = []
    Reachable_idx = []
    
    i = 0
    for i in range(len(Assigned_Nodes)):
        Assigned_Nodes[i].isReachable = False
        Assigned_Nodes[i].isExtensible = False
        Assigned_Nodes[i].reachable = []
        
        j = 0
        for j in range(len(Assigned_Nodes[i].adj_nodes)):
            if ((Node[Assigned_Nodes[i].adj_nodes[j]] in Outside) == True):
                
                Node[Assigned_Nodes[i].adj_nodes[j]].isReachable = True
                Assigned_Nodes[i].reachable.append(Assigned_Nodes[i].adj_nodes[j])
                
        if ((len(Assigned_Nodes[i].reachable)) != 0):
            Assigned_Nodes[i].isExtensible = True
        else:
            Assigned_Nodes[i].isExtensible = False
                
    i = 0
    for i in range(len(Cluster)):
        Cluster[i].extensible = []
        
        j = 0
        for j in range(len(Cluster[i].Nodes)):
            if ((Cluster[i].Nodes[j].isExtensible) == True):
                if ((Cluster[i].Nodes[j].index not in Cluster[i].extensible) == True):
                    Cluster[i].extensible.append(Cluster[i].Nodes[j].index)
                
            k = 0
            for k in range(len(Cluster[i].Nodes[j].adj_nodes)):
                if ((Node[Cluster[i].Nodes[j].adj_nodes[k]].isReachable) == True):
                    if ((Cluster[i].Nodes[j].adj_nodes[k] not in Cluster[i].reachable) == True):
                        Cluster[i].reachable.append(Cluster[i].Nodes[j].adj_nodes[k])
                        
        if ((len(Cluster[i].extensible)) != 0):
            Cluster[i].isExtensible = True
        else:
            Cluster[i].isExtensible = False
            
    i = 0
    for i in range(len(Cluster)):
        
        j = 0
        for j in range(len(Cluster[i].reachable)):
            if ((Cluster[i].reachable[j] not in Reachable_idx) == True):
                Reachable_idx.append(Cluster[i].reachable[j])
                
        j = 0
        for j in range(len(Cluster[i].extensible)):
            if ((Cluster[i].extensible[j] not in Extensible_idx) == True):
                Extensible_idx.append(Cluster[i].extensible[j])
            
    #Create set containing all Extensible nodes in all clusters            
    i = 0
    for i in range(len(Node)):
        if (Node[i].isExtensible == True):
            Extensible.append(Node[i])
    
    i = 0        
    for i in range(len(Extensible)):
        if ((Extensible[i].index not in Extensible_idx) == True):
            print("Node " + str(Extensible[i].index) + " is in Extensible but is not in Extensible_idx.")
    
    #Create set containing all Reachable nodes in all clusters    
    i = 0
    for i in range(len(Node)):
        if (Node[i].isReachable == True):
            Reachable.append(Node[i])
            
    i = 0        
    for i in range(len(Reachable)):
        if ((Reachable[i].index not in Reachable_idx) == True):
            print("Node " + str(Reachable[i].index) + " is in Reachable but is not in Reachable_idx.")
            
    print("The number of outside nodes decreased by: " + str(delta_Outside))
    print("The number of assigned nodes increased by: " + str(delta_Assigned))
    print("The number of clustered nodes decreased by: " + str(delta_clustered)) 
    
#%%
i = 0
for i in range(len(Node)):
    Node[i].times_assigned = 0
    
    for j in range(len(Assigned_Nodes)):
        if (Assigned_Nodes[j].index == Node[i].index):
            Node[i].times_assigned += 1

Cluster0_Nodes = Cluster[0].nodes_idx
Cluster1_Nodes = Cluster[1].nodes_idx
Cluster2_Nodes = Cluster[2].nodes_idx

for i in range(len(Cluster0_Nodes)):
    Node[Cluster0_Nodes[i]].num_clust += 1
    
    if (Cluster0_Nodes[i] in Cluster1_Nodes):
        Node[Cluster0_Nodes[i]].num_clust += 1
    if (Cluster0_Nodes[i] in Cluster2_Nodes):
        Node[Cluster0_Nodes[i]].num_clust += 1
"""        
i = 0
for i in range(len(Cluster[0].Nodes)):
    print(Cluster[0].Nodes[i].num_clust)
""" 
for i in range(len(Cluster1_Nodes)):
    Node[Cluster1_Nodes[i]].num_clust += 1
    
    if (Cluster1_Nodes[i] in Cluster0_Nodes):
        Node[Cluster1_Nodes[i]].num_clust += 1
    if (Cluster1_Nodes[i] in Cluster2_Nodes):
        Node[Cluster1_Nodes[i]].num_clust += 1
"""        
i = 0
for i in range(len(Cluster[1].Nodes)):
    print(Cluster[1].Nodes[i].num_clust)
""" 
for i in range(len(Cluster2_Nodes)):
    Node[Cluster2_Nodes[i]].num_clust += 1
    
    if (Cluster2_Nodes[i] in Cluster1_Nodes):
        Node[Cluster2_Nodes[i]].num_clust += 1
    if (Cluster2_Nodes[i] in Cluster0_Nodes):
        Node[Cluster2_Nodes[i]].num_clust += 1
"""        
i = 0
for i in range(len(Cluster[2].Nodes)):
    print(Cluster[2].Nodes[i].num_clust)
"""    
print(len(Cluster[0].Nodes))
print(len(Cluster[1].Nodes))
print(len(Cluster[2].Nodes))
"""
i = 0
for i in range(len(Node)):
    print(Node[i].times_assigned)
"""
#%%
#Plotting

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
