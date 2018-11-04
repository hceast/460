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
deliv_517 = pd.read_excel("May_17_Delivery_Data.xlsx", sheet_name = "Delivery Data")
#Exclude addresses from the data frame, we only need Lat/Longs
deliv_517 = deliv_517[["Longitude", "Latitude", "Delivery Volume"]].copy()

#Establish target weights for balancing
#target_weight = [(deliv_517["Delivery Volume"].sum()/3), (deliv_517["Delivery Volume"].sum()/3), (deliv_517["Delivery Volume"].sum()/3)]
target_weight = [(deliv_517["Delivery Volume"].sum()*(3/8)), (deliv_517["Delivery Volume"].sum()*(3/8)), (deliv_517["Delivery Volume"].sum()*(1/4))]

#Create data frame containing distribution center information
dist_center = pd.read_excel("May_17_Delivery_Data.xlsx", sheet_name = "Centers")
dist_center = dist_center[["Longitude", "Latitude"]].copy()

#Append weight-balance-target volumes to the dataframe. Name the column "Delivery Volume" for sake of simplicity with the
#concatenation below
dist_center["Delivery Volume"] = target_weight

#Make everything one data frame. Facility locations are at the bottom of the data frame.
deliv_517 = pd.concat([deliv_517, dist_center[["Longitude", "Latitude", "Delivery Volume"]]], ignore_index = True)

#Distance Matrix that gives the great-circle distance between each pair of nodes
D_Mat = np.zeros((len(deliv_517), len(deliv_517))) 

i = 0
for i in range(len(deliv_517)):
    coords1 = (deliv_517["Longitude"][i], deliv_517["Latitude"][i])
    
    j = 0
    for j in range(len(deliv_517)):
        coords2 = (deliv_517["Longitude"][j], deliv_517["Latitude"][j])
        D_Mat[i][j] = haversine(coords1, coords2)

#%%
#Create Voronoi diagram that will be the basis for clustering
vor = Voronoi(deliv_517[["Longitude", "Latitude"]], qhull_options = "Qbb Qc Qx")
#voronoi_plot_2d(vor)
#fig = plt.figure()
#plt.show()

#Determine node adjacencies
all_adj = []

i=0
for i in range(len(vor.points)):
    point = (vor.points[i][0], vor.points[i][1])
    adj_pts = get_adjacent(point, vor)
    all_adj.append(adj_pts)

#Append list of node adjacencies to deliv-517 dataframe   
se2 = pd.Series(all_adj)
deliv_517["Adj Nodes"] = se2.values

#%%
"""
Cluster[i].Nodes.append(Cluster[i].centroid.index)

Cluster[i].nodes_idx.append(Cluster[i].centroid.index)
"""
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
#%%
#Import node and cluster class objects
from Node import node
from Cluster import cluster
from Reachable_Extensible import get_reach_and_ext
from Best_Reach_Ext import best_reach_ext_nodes, best_reach_ext_clusters
from Assign_and_Update import assign_and_update
from Plot_Clusters import plot_clusters

#Create Node set
Node = [node(i, (deliv_517["Longitude"][i], deliv_517["Latitude"][i]), deliv_517["Delivery Volume"][i], deliv_517["Adj Nodes"][i]) for i in range(len(deliv_517))]

#Establish set Outside, which tracks the nodes that are not assigned to a cluster
Outside = [Node[i].index for i in range(len(Node))]

#Create set that tracks the nodes that have been assigned to a cluster
Assigned_Nodes = []

#Cluster Initialization:

#Clusters take a Node object that will be the centroid, a balance target for the cluster, and a capacity.
#This line creates 3 clusters with the facilities as the central locations.
Cluster = [cluster(Node[i], deliv_517["Delivery Volume"][i], 999999999) for i in range(465,468)]

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
    
    #Makes sure the centroid node object has the index of the cluster to which it is assigned
    Cluster[i].centroid.cluster = Cluster[i].index
    #Centroid is centroid
    Cluster[i].centroid.isRoot = True
    
    #Update Outside, as the centroids are now part of the clusters
    Cluster[i].centroid.isOutside = False
    Outside.remove(Cluster[i].centroid.index)
    
    #Update Assigned_Nodes
    Assigned_Nodes.append(Cluster[i].centroid.index)
    
    #Calculate distance function value for node, which for the centroid will be zero
    Cluster[i].centroid.distance = Cluster[i].centroid.calc_distance()

#Determine the extensible and reachable nodes
get_reach_and_ext(Cluster, Node)

#Create set containing all Extensible nodes in all clusters
Extensible = []
               
i = 0
for i in range(len(Node)):
    if (Node[i].isExtensible == True):
        Extensible.append(Node[i].index)

#Create set containing all Reachable nodes in all clusters
Reachable = []

i = 0
for i in range(len(Node)):
    if (Node[i].isReachable == True):
        Reachable.append(Node[i].index)

#%%
l = 0
for l in range(0, 454):    
    
    #Identify the best reachable node for every extensible node, and the best extensible
    #node for every reachable node.
    best_reach_ext_nodes(Node)
    #Identify the best reachable and extensible nodes for each cluster.
    best_reach_ext_clusters(Cluster)
    
    #Selected cluster, selected reachable (q_star) and selected extensible (p-star)
    C_star = ""
    q_star = ""
    p_star = ""    
    """
    #Determine C_Star
    Card = []
        
    i = 0
    for i in range(len(Cluster)):
        Card.append(len(Cluster[i].Nodes))
    """
    Weight_Improvement = []
    
    i = 0
    for i in range(len(Cluster)):
        #Current deviation from target weight
        current_deviation = ""
        current_deviation = abs(Cluster[i].weight - Cluster[i].balance_target)
        #Deviation should the best reachable node we are examining be added
        new_deviation = ""
        new_deviation = abs((Cluster[i].weight + Cluster[i].best_reachable.weight) - Cluster[i].balance_target)
        
        #Weight_Improvement.append(current_deviation - new_deviation)
        
        #Weighted against distance. Acceptable results alone. Catastrophic when used with tiebreaker.
        Weight_Improvement.append((current_deviation - new_deviation)*(1/Cluster[i].best_reachable.min_reachable_dist))
    
    #Select cluster to be the cluster that has the node that provides the best improvement w.r.t. the weight criterion
    #C_star = Weight_Improvement.index(max(Weight_Improvement))
    """
    #Cardinality Tiebreak
    min_card = min(Card)
    candidates = []
    
    #Find the ones that tie
    i = 0
    for i in range(len(Card)):
        if (Card[i] == min_card):
            candidates.append(i)
    #If there are no ties, select the cluster as above
    if (len(candidates) > 1):

        #Find the one that also minimizes distance.
        Min_Reach_Dist = []
        
        i = 0
        for i in range(len(candidates)):
            Min_Reach_Dist.append(Cluster[candidates[i]].best_reachable.min_reachable_dist)
        
        C_star = candidates[Min_Reach_Dist.index(min(Min_Reach_Dist))]

        Weight_Improvement = []
    
        i = 0
        for i in range(len(candidates)):
            #Current deviation from target weight
            current_deviation = ""
            current_deviation = abs(Cluster[candidates[i]].weight - Cluster[i].balance_target)
            #Deviation should the best reachable node we are examining be added
            new_deviation = ""
            new_deviation = abs((Cluster[i].weight + Cluster[i].best_reachable.weight) - Cluster[i].balance_target)
            
           # Weight_Improvement.append(current_deviation - new_deviation)
            Weight_Improvement.append((current_deviation - new_deviation)*(1/Cluster[i].best_reachable.min_reachable_dist))
            
        C_star = candidates[Weight_Improvement.index(max(Weight_Improvement))]

    else:
        C_star = Card.index(min(Card))
    """
    
    #Weightbalance Tiebreak
    best_improvement = max(Weight_Improvement)
    candidates = []
    
    #Find the ones that tie
    i = 0
    for i in range(len(Weight_Improvement)):
        if (Weight_Improvement[i] == best_improvement):
            candidates.append(i)
    #If there are no ties, select the cluster as above
    if (len(candidates) > 1):
        """
        #Find the one that also minimizes distance.
        Min_Reach_Dist = []
        
        i = 0
        for i in range(len(candidates)):
            Min_Reach_Dist.append(Cluster[candidates[i]].best_reachable.min_reachable_dist)
        
        C_star = candidates[Min_Reach_Dist.index(min(Min_Reach_Dist))]
        """
        Card = []
        
        i = 0
        for i in range(len(candidates)):
            Card.append(len(Cluster[candidates[i]].Nodes))
        
        C_star = Cluster[candidates[Card.index(min(Card))]]

    else:
        C_star = Cluster[Weight_Improvement.index(max(Weight_Improvement))]
    
    #Once you know your C_star, you know your q_star which is associated with a p_star
    q_star = C_star.best_reachable
    p_star = C_star.best_extensible
    
    #Update Outside
    q_star.isOutside = False
    if (q_star.index in Outside):
        Outside.remove(q_star.index)
    q_star.isReachable = False

    #Update Assigned_Nodes
    Assigned_Nodes.append(q_star.index)
    
    #Assign q_star to C_star, update C_star, update Node set.
    assign_and_update(C_star, q_star, p_star)
    
    #Update extensible and reachable information.
    get_reach_and_ext(Cluster, Node)
    
    #Create set containing all Extensible nodes in all clusters
    Extensible = []
                   
    i = 0
    for i in range(len(Node)):
        if (Node[i].isExtensible == True):
            Extensible.append(Node[i].index)
    
    #Create set containing all Reachable nodes in all clusters
    Reachable = []
    
    i = 0
    for i in range(len(Node)):
        if (Node[i].isReachable == True):
            Reachable.append(Node[i].index)

#%%
#Plotting and output information

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

print(len(Cluster[0].Nodes))
print(len(Cluster[1].Nodes))
print(len(Cluster[2].Nodes))

print(Cluster[0].weight)
print(Cluster[1].weight)
print(Cluster[2].weight)
