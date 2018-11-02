# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
# Importing packages
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d
from adjacent import get_adjacent
from haversine import haversine

#Reads in the excel file that contains all of the May 17th deliveries, and constructs a data frame
deliv_517 = pd.read_excel("May_17_Delivery_Data.xlsx", sheet_name = "Delivery Data")
#Exclude addresses from the data frame
deliv_517 = deliv_517[["Longitude", "Latitude", "Delivery Volume"]].copy()

#Establish target weights for balancing
target_weight = (deliv_517["Delivery Volume"].sum()/3)
avg_weight = deliv_517["Delivery Volume"].mean()

#Create data frame for distribution center information
dist_center = pd.read_excel("May_17_Delivery_Data.xlsx", sheet_name = "Centers")
dist_center = dist_center[["Longitude", "Latitude"]].copy()

#Create center capacities. Arbitrarily high for simplicity.
se1 = [999999999, 999999999, 999999999]
dist_center["Delivery Volume"] = se1

#Make everything one data frame. Facility locations are at the bottom of the data frame.
deliv_517 = pd.concat([deliv_517, dist_center[["Longitude", "Latitude", "Delivery Volume"]]], ignore_index = True)

#Distance Matrix
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

#Append list of node adjacencies to dataframe   
se2 = pd.Series(all_adj)
deliv_517["Adj Nodes"] = se2.values

#%%
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
#%%
#Import node and cluster class objects
from Node import node
from Cluster import cluster

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
#The last three nodes are the facilities. We are using them as the initial centroids in order to build the algorithm.
#Clusters take a Node object that will be the centroid, a target weight for the cluster, and a capacity.
Cluster = [cluster(Node[i], target_weight, deliv_517["Delivery Volume"][i]) for i in range(465,468)]
"""
Cluster = []
Cluster.append(cluster(Node[376], target_weight, 999999999))
Cluster.append(cluster(Node[49], target_weight, 999999999))
Cluster.append(cluster(Node[68], target_weight, 999999999))
"""
#Give clusters indicies for easy indentification
i = 0
for i in range(len(Cluster)):
    Cluster[i].index = i
    
#Update cluster information
i = 0
for i in range(len(Cluster)):
    """
    #Assign the centroid into the cluster's Node list
    Cluster[i].Nodes.append(Cluster[i].centroid)
    Cluster[i].nodes_idx.append(Cluster[i].centroid.index)
    """
    #Assign the associated cluster to its centroid
    Cluster[i].centroid.cluster = Cluster[i].index
    #Centroid is centroid
    Cluster[i].centroid.isRoot = True
    
    #Update Outside, as the centroids are part of the clusters
    Cluster[i].centroid.isOutside = False
    Outside.remove(Cluster[i].centroid.index)
    
    #Update Assigned_Nodes
    Assigned_Nodes.append(Cluster[i].centroid.index)
    
    #Calculate distance function value for node, which for the centroid will be zero
    Cluster[i].centroid.distance = Cluster[i].centroid.calc_distance()

#Determine the extensible and reachable nodes
i = 0
for i in range(len(Cluster)):
    #Initalize sets at cluster level
    Cluster[i].reachable = []
    Cluster[i].extensible = []
    
    j = 0
    for j in range(len(Cluster[i].Nodes)):
        #There is no extensible set at the node level. Initialize the reachable set
        Cluster[i].Nodes[j].reachable = []
        #Loop through the list of adjacnet nodes for every node in the node set.
        #If a node is an element of outside, and is adjacent to a node that is assigned 
        #to a cluster, it is a reachable node. Additionally, the clustered node that 
        #is adjacent to this outside node is therefore extensible.
        k = 0
        for k in range(len(Cluster[i].Nodes[j].adj_nodes)):
            if (Node[Cluster[i].Nodes[j].adj_nodes[k]].isOutside == True):
                #If adjacent to a clustered node and outside, node is reachable
                Node[Cluster[i].Nodes[j].adj_nodes[k]].isReachable = True
                #Add to the list of nodes reachable from the clustered node.
                Cluster[i].Nodes[j].reachable.append(Cluster[i].Nodes[j].adj_nodes[k])
                #Add the adjacent node to the cluster's list of adjacent nodes if it is not
                #already accounted for in the set.
                if (Cluster[i].Nodes[j].adj_nodes[k] not in Cluster[i].reachable):
                    Cluster[i].reachable.append(Cluster[i].Nodes[j].adj_nodes[k])
            else:
                Node[Cluster[i].Nodes[j].adj_nodes[k]].isReachable = False
        # If a clustered node is adjacent to outside nodes, it is extensible.
        if (len(Cluster[i].Nodes[j].reachable) != 0):
            Cluster[i].Nodes[j].isExtensible = True
            #Add extensible nodes to the cluster's list of extensible nodes
            if (Cluster[i].Nodes[j].index not in Cluster[i].extensible):
                Cluster[i].extensible.append(Cluster[i].Nodes[j].index)
        else:
            Cluster[i].Nodes[j].isExtensible = False
    #If a cluster has an extensible node, it is extensible
    if (len(Cluster[i].extensible) != 0):
        Cluster[i].isExtensible = True
    else:
        Cluster[i].isExtensible = False

i = 0
for i in range(len(Node)):
    if (Node[i].isReachable == True):
        num_ext = 0
        
        j = 0
        for j in range(len(Node[i].adj_nodes)):
            if (Node[Node[i].adj_nodes[j]].isExtensible == True):
                num_ext += 1
        
        if (num_ext == 0):
            Node[i].isReachable = False

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
l = 0
for l in range(0, 468):    
    
    i = 0
    for i in range(len(Node)):
        min_dist = "None"
        
        if (Node[i].isExtensible == True):
            
            j = 0
            for j in range(len(Node[i].adj_nodes)):
                
                if (Node[Node[i].adj_nodes[j]].isReachable == True):
                    dist = Node[i].distance + haversine(Node[i].coords, Node[Node[i].adj_nodes[j]].coords)
                    
                    if (min_dist == "None"):
                        min_dist = dist
                        Node[i].best_reach = Node[Node[i].adj_nodes[j]]
                    elif (dist < min_dist):
                        min_dist = dist
                        Node[i].best_reach = Node[Node[i].adj_nodes[j]]
                        
        if (Node[i].isReachable == True):
            
            j = 0
            for j in range(len(Node[i].adj_nodes)):
                
                if (Node[Node[i].adj_nodes[j]].isExtensible == True):
                    dist = Node[Node[i].adj_nodes[j]].distance + haversine(Node[Node[i].adj_nodes[j]].coords, Node[i].coords)
                    
                    if (min_dist == "None"):
                        min_dist = dist
                        Node[i].best_ext = Node[Node[i].adj_nodes[j]]
                        Node[i].preferred_cluster = Node[Node[i].adj_nodes[j]].cluster
                    elif (dist < min_dist):
                        min_dist = dist
                        Node[i].best_ext = Node[Node[i].adj_nodes[j]]
                        Node[i].preferred_cluster = Node[Node[i].adj_nodes[j]].cluster
                        
            Node[i].min_reachable_dist = min_dist
            
    i = 0
    for i in range(len(Cluster)):
        min_dist = "None"
        
        j = 0
        for j in range(len(Cluster[i].Nodes)):
            
            if(Cluster[i].Nodes[j].isExtensible == True):
                if (min_dist == "None"):
                    min_dist = Cluster[i].Nodes[j].best_reach.min_reachable_dist
                    Cluster[i].best_extensible = Cluster[i].Nodes[j]
                    Cluster[i].best_reachable = Cluster[i].Nodes[j].best_reach
                elif (Cluster[i].Nodes[j].best_reach.min_reachable_dist < min_dist):
                    min_dist = Cluster[i].Nodes[j].best_reach.min_reachable_dist
                    Cluster[i].best_extensible = Cluster[i].Nodes[j]
                    Cluster[i].best_reachable = Cluster[i].Nodes[j].best_reach
    
    #Selected cluster, selected reachable (q_star) and selected extensible (p-star)
    C_star = ""
    q_star = ""
    p_star = ""    

    #The best reachable node from each cluster is determined. The cluster to extend is selected to maximize the improvement in reaching the target weight
    #The option to weigh the improvement agaisnt min reachable distance is included. Ties are broken with min reachable distance
    #Best results have been obtained with this decision criterion with no tiebreaker. Me thinks I've fucked up the coding for the tiebreakers. All the
    #tiebreakers perform dismally.
     
    Weight_Improvement = []
    
    i = 0
    for i in range(len(Cluster)):
        #Current deviation from target weight
        current_deviation = ""
        current_deviation = abs(Cluster[i].weight - Cluster[i].balance_target)
        #Deviation should the best reachable node we are examining be added
        new_deviation = ""
        new_deviation = abs((Cluster[i].weight + Cluster[i].best_reachable.weight) - Cluster[i].balance_target)
        
        Weight_Improvement.append(current_deviation - new_deviation)
        #Weighted against distance. Acceptable results alone. Catastrophic when used with tiebreaker.
        #Weight_Improvement.append((current_deviation - new_deviation)*(1/Node[Cluster[i].best_reachable].min_reachable_dist))
    
    #Select cluster to be the cluster that has the node that provides the best improvement w.r.t. the weight criterion
    #C_star = Weight_Improvement.index(max(Weight_Improvement))
    
    #Tiebreak
    best_improvement = max(Weight_Improvement)
    candidates = []
    
    #Find the ones that tie
    i = 0
    for i in range(len(Weight_Improvement)):
        if (Weight_Improvement[i] == best_improvement):
            candidates.append(i)
    #If there are no ties, select the cluster as above
    if (len(candidates) > 1):
        
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
        
        C_star = candidates[Card.index(min(Card))]
        """
    else:
        C_star = Weight_Improvement.index(max(Weight_Improvement))
       
    #Once you know your C_star, you know your q_star which is associated with a p_star
    q_star = Cluster[C_star].best_reachable
    p_star = Cluster[C_star].best_extensible
                    
    #Add q_star to Cluster
    Cluster[C_star].Nodes.append(q_star)
    Cluster[C_star].nodes_idx.append(q_star.index)
    q_star.cluster = C_star
    
    #Update cluster weight and capacity
    Cluster[C_star].weight += q_star.weight
    Cluster[C_star].capac -= q_star.weight
    
    #Update Outside
    q_star.isOutside = False
    if (q_star.index in Outside):
        Outside.remove(q_star.index)
    q_star.isReachable = False
    
    #Update Assigned_Nodes
    Assigned_Nodes.append(q_star.index)
    
    #Update predecessor path information about q_star
    q_star.Pred.extend(p_star.Pred)
    q_star.Pred.append(p_star)
    q_star.pred_idx.extend(p_star.pred_idx)
    q_star.pred_idx.append(p_star.index)
    #Set q_star as the immediate successor of p_star
    p_star.child = q_star
    
    #Calculate distance function value for node
    q_star.distance = q_star.calc_distance()
    
    #Updating extensible and reachable information. I applied the same code I wrote here above when
    #calculating this for the centroids. I'm gonna make it a function.
    i = 0
    for i in range(len(Cluster)):
        #Initalize sets at cluster level
        Cluster[i].reachable = []
        Cluster[i].extensible = []
        
        j = 0
        for j in range(len(Cluster[i].Nodes)):
            #There is no extensible set at the node level. Initialize the reachable set
            Cluster[i].Nodes[j].reachable = []
            #Loop through the list of adjacnet nodes for every node in the node set.
            #If a node is an element of outside, and is adjacent to a node that is assigned 
            #to a cluster, it is a reachable node. Additionally, the clustered node that 
            #is adjacent to this outside node is therefore extensible.
            k = 0
            for k in range(len(Cluster[i].Nodes[j].adj_nodes)):
                if (Node[Cluster[i].Nodes[j].adj_nodes[k]].isOutside == True):
                    #If adjacent to a clustered node and outside, node is reachable
                    Node[Cluster[i].Nodes[j].adj_nodes[k]].isReachable = True
                    #Add to the list of nodes reachable from the clustered node.
                    Cluster[i].Nodes[j].reachable.append(Cluster[i].Nodes[j].adj_nodes[k])
                    #Add the adjacent node to the cluster's list of adjacent nodes if it is not
                    #already accounted for in the set.
                    if (Cluster[i].Nodes[j].adj_nodes[k] not in Cluster[i].reachable):
                        Cluster[i].reachable.append(Cluster[i].Nodes[j].adj_nodes[k])
                else:
                    Node[Cluster[i].Nodes[j].adj_nodes[k]].isReachable = False
            # If a clustered node is adjacent to outside nodes, it is extensible.
            if (len(Cluster[i].Nodes[j].reachable) != 0):
                Cluster[i].Nodes[j].isExtensible = True
                #Add extensible nodes to the cluster's list of extensible nodes
                if (Cluster[i].Nodes[j].index not in Cluster[i].extensible):
                    Cluster[i].extensible.append(Cluster[i].Nodes[j].index)
            else:
                Cluster[i].Nodes[j].isExtensible = False
        #If a cluster has an extensible node, it is extensible
        if (len(Cluster[i].extensible) != 0):
            Cluster[i].isExtensible = True
        else:
            Cluster[i].isExtensible = False
    
    i = 0
    for i in range(len(Node)):
        if (Node[i].isReachable == True):
            num_ext = 0
            
            j = 0
            for j in range(len(Node[i].adj_nodes)):
                if (Node[Node[i].adj_nodes[j]].isExtensible == True):
                    num_ext += 1
            
            if (num_ext == 0):
                Node[i].isReachable = False
    
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
