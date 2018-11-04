# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
# Importing packages
import random
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d
from adjacent import get_adjacent
from haversine import haversine

#Reads in the excel file that contains all of the May 17th deliveries, and constructs a data frame
deliv_517 = pd.read_excel("May_17_Delivery_Data.xlsx", sheet_name = "Delivery Data")
#Exclude addresses from the data frame
deliv_517 = deliv_517[["Longitude", "Latitude", "Delivery Volume"]].copy()

#Create data frame for distribution center information
dist_center = pd.read_excel("May_17_Delivery_Data.xlsx", sheet_name = "Centers")
dist_center = dist_center[["Longitude", "Latitude"]].copy()

#Establish target weights for balancing
target_weight = (deliv_517["Delivery Volume"].sum()/3)
avg_weight = deliv_517["Delivery Volume"].mean()

#Create center capacities. Arbitrarily high for simplicity.
se1 = [999999999, 999999999, 999999999]
dist_center["Delivery Volume"] = se1

#Make everything one data frame. Facility location are at the bottom of the data frame.
deliv_517 = pd.concat([deliv_517, dist_center[["Longitude", "Latitude", "Delivery Volume"]]], ignore_index = True)

#%%
#Create voronoi diagram that will be basis for clustering
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
#Import node and cluster class objects
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
#The last three nodes are the facilities. We are using them as the initial nodes in order to build the algorithm.
#Clusters take a Node object that will be the centroid, a target weight for the cluster, and a capacity.
Cluster = [cluster(Node[i], target_weight, deliv_517["Delivery Volume"][i]) for i in range(465,468)]

#Give cluster indices in order to easily identify them
i = 0
for i in range(len(Cluster)):
    Cluster[i].index = i
    
#Update cluster information
i = 0
for i in range(len(Cluster)):
    
    #Assign the centroid into the cluster's Node list
    Cluster[i].Nodes.append(Cluster[i].centroid)
    Cluster[i].nodes_idx.append(Cluster[i].centroid.index)
    #Assign the associated cluster to its centroid
    Cluster[i].centroid.cluster = Cluster[i].index
    #Centroid is centroid
    Cluster[i].centroid.isRoot = True
    
    #Update Outside, as the centroids are part of clusters
    Cluster[i].centroid.isOutside = False
    Outside.remove(Cluster[i].centroid.index)
    
    #Update Assigned_Nodes
    Assigned_Nodes.append(Cluster[i].centroid.index)
    
    #Update predecessor path information
    #Centroids have no predecessors
    Cluster[i].centroid.Pred = -1
    Cluster[i].centroid.pred_idx = -1
    
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
                Node[Cluster[i].Nodes[j].adj_nodes[k]].isReachable == True
                #Add to the list of nodes reachable from the clustered node.
                Cluster[i].Nodes[j].reachable.append(Cluster[i].Nodes[j].adj_nodes[k])
                #Add the adjacent node to the cluster's list of adjacent nodes if it is not
                #already accounted for in the set.
                if (Cluster[i].Nodes[j].adj_nodes[k] not in Cluster[i].reachable):
                    Cluster[i].reachable.append(Cluster[i].Nodes[j].adj_nodes[k])
            else:
                Node[Cluster[i].Nodes[j].adj_nodes[k]].isReachable == False
        # If a clustered node is adjacent to outside nodes, it is extensible.
        if (Cluster[i].Nodes[j].reachable != []):
            Cluster[i].Nodes[j].isExtensible = True
            #Add extensible nodes to the cluster's list of extensible nodes
            if (Cluster[i].Nodes[j].index not in Cluster[i].extensible):
                Cluster[i].extensible.append(Cluster[i].Nodes[j].index)
        else:
            Cluster[i].Nodes[j].isExtensible = False
    #If a cluster has an extensible node, it is extensible
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
        if (Cluster[i].extensible[j] not in Extensible):
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
for l in range(0, 550):    
    
    #Determine the best reachable node for each cluster
    i = 0
    for i in range(len(Cluster)):
        best_dist = "None"
        #Step through each cluster's extensible set.
        j = 0
        for j in range(len(Cluster[i].extensible)):
            #Look at the nodes reachable from a given extensible node
            k = 0
            for k in range(len(Node[Cluster[i].extensible[j]].reachable)):
                #min_reachable_dist = (Extensible node's distance from the centroid) + (Distance from the extensible node to the reachable node)
                Node[Node[Cluster[i].extensible[j]].reachable[k]].min_reachable_dist = Node[Cluster[i].extensible[j]].distance + haversine(Node[Cluster[i].extensible[j]].coords, Node[Node[Cluster[i].extensible[j]].reachable[k]].coords)
                #Determine the reachable node that is closest to the center of the cluster. Store the indecies of this reachable node and it's associated extensible node.
                if(best_dist == "None"):
                    best_dist = Node[Node[Cluster[i].extensible[j]].reachable[k]].min_reachable_dist
                    Cluster[i].best_extensible = Cluster[i].extensible[j]
                    Cluster[i].best_reachable = Node[Cluster[i].extensible[j]].reachable[k]
                if (Node[Node[Cluster[i].extensible[j]].reachable[k]].min_reachable_dist < best_dist):
                    best_dist = Node[Node[Cluster[i].extensible[j]].reachable[k]].min_reachable_dist
                    Cluster[i].best_extensible = Cluster[i].extensible[j]
                    Cluster[i].best_reachable = Node[Cluster[i].extensible[j]].reachable[k]
    
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
        #Deviation should the best reachable node we are examining be added
        new_deviation = ""
        
        current_deviation = abs(Cluster[i].weight - Cluster[i].balance_target)
        new_deviation = abs((Cluster[i].weight + Node[Cluster[i].best_reachable].weight) - Cluster[i].balance_target)
        
        Weight_Improvement.append(current_deviation - new_deviation)
        #Weighted against distance. Acceptable results alone. Catastrophic when used with tiebreaker.
        #Weight_Improvement.append((current_deviation - new_deviation)*(1/Node[Cluster[i].best_reachable].min_reachable_dist))
    
    #Select cluster to be the cluster that has the node that provides the best improvement w.r.t. the weight criterion
    C_star = Weight_Improvement.index(max(Weight_Improvement))
    """
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
        
        #Pick a random cluster from the tied clusters
        choice = random.randint(min(range(len(candidates))), max(range(len(candidates))))
        C_star = candidates[choice]
        
        #Find the one that also minimizes distance.
        Min_Reach_Dist = []
        
        i = 0
        for i in range(len(candidates)):
            Min_Reach_Dist.append(Node[Cluster[candidates[i]].best_reachable].min_reachable_dist)
        
        C_star = candidates[Min_Reach_Dist.index(min(Min_Reach_Dist))]
        
        Card = []
        
        i = 0
        for i in range(len(candidates)):
            Card.append(len(Cluster[candidates[i]].Nodes))
        
        C_star = candidates[Card.index(min(Card))]
        
    else:
        C_star = Weight_Improvement.index(max(Weight_Improvement))
    """    
    #Once you know your C_star, you know your q_star which is associated with a p_star
    q_star = Cluster[C_star].best_reachable
    p_star = Cluster[C_star].best_extensible
                    
    #Add q_star to Cluster
    Cluster[C_star].Nodes.append(Node[q_star])
    Cluster[C_star].nodes_idx.append(q_star)
    Node[q_star].cluster = Cluster[C_star].index
    
    #Update cluster weight and capacity
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
    #Set q_star as the immediate successor of p_star
    Node[p_star].child = q_star
    
    #Calculate distance function value for node
    Node[q_star].distance = 0
    Node[q_star].distance = Node[q_star].calc_distance()
    
    #Updating extensible and reachable information. I applied the same code I wrote here above when
    #calculating this for the centroids. I'm gonna make it a function.
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
    #Global sets
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
