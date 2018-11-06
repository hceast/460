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

#Establish target weights for balancing
#target_weight = [(delivs["Delivery Volume"].sum()/3), (delivs["Delivery Volume"].sum()/3), (delivs["Delivery Volume"].sum()/3)]
target_weight = [(delivs["Delivery Volume"].sum()*(3/8)), (delivs["Delivery Volume"].sum()*(3/8)), (delivs["Delivery Volume"].sum()*(1/4))]

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
voronoi_plot_2d(vor)
fig = plt.figure()
plt.show()

#Determine node adjacencies
all_adj = []

i=0
for i in range(len(vor.points)):
    point = (vor.points[i][0], vor.points[i][1])
    adj_pts = get_adjacent(point, vor)
    all_adj.append(adj_pts)

#Append list of node adjacencies to deliv-517 dataframe   
se2 = pd.Series(all_adj)
delivs["Adj Nodes"] = se2.values

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
from Decision_Criteria import priority_weight, priority_card

#Create Node set
Node = [node(i, (delivs["Longitude"][i], delivs["Latitude"][i]), delivs["Delivery Volume"][i], delivs["Adj Nodes"][i]) for i in range(len(delivs))]

#Establish set Outside, which tracks the nodes that are not assigned to a cluster
Outside = [Node[i].index for i in range(len(Node))]

#Create set that tracks the nodes that have been assigned to a cluster
Assigned_Nodes = []

#Cluster Initialization:

#Clusters take a Node object that will be the centroid, a balance target for the cluster, and a capacity.
#This line creates 3 clusters with the facilities as the central locations.
Cluster = [cluster(Node[i], delivs["Delivery Volume"][i], 999999999) for i in range(465,468)]

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
while (len(Outside) > 10):
#l = 0
#for l in range(0, 456):
    
    #Identify the best reachable node for every extensible node, and the best extensible
    #node for every reachable node.
    best_reach_ext_nodes(Node)
    #Identify the best reachable and extensible nodes for each cluster.
    best_reach_ext_clusters(Cluster)
    
    #Selected cluster, selected reachable (q_star) and selected extensible (p-star)
    C_star = ""
    q_star = ""
    p_star = "" 
    
    #Determine C_star
    C_star = priority_card(Cluster)
    #C_star = priority_weight(Cluster)
    
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

Cluster0_Nodes = Cluster[0].nodes_idx
Cluster1_Nodes = Cluster[1].nodes_idx
Cluster2_Nodes = Cluster[2].nodes_idx

for i in range(len(Cluster0_Nodes)):
    Node[Cluster0_Nodes[i]].num_clust += 1
    
    if (Cluster0_Nodes[i] in Cluster1_Nodes):
        Node[Cluster0_Nodes[i]].num_clust += 1
    if (Cluster0_Nodes[i] in Cluster2_Nodes):
        Node[Cluster0_Nodes[i]].num_clust += 1
        
i = 0
for i in range(len(Cluster[0].Nodes)):
    print(Cluster[0].Nodes[i].num_clust)
    
for i in range(len(Cluster1_Nodes)):
    Node[Cluster1_Nodes[i]].num_clust += 1
    
    if (Cluster1_Nodes[i] in Cluster0_Nodes):
        Node[Cluster1_Nodes[i]].num_clust += 1
    if (Cluster1_Nodes[i] in Cluster2_Nodes):
        Node[Cluster1_Nodes[i]].num_clust += 1
        
i = 0
for i in range(len(Cluster[1].Nodes)):
    print(Cluster[1].Nodes[i].num_clust)
    
for i in range(len(Cluster2_Nodes)):
    Node[Cluster2_Nodes[i]].num_clust += 1
    
    if (Cluster2_Nodes[i] in Cluster1_Nodes):
        Node[Cluster2_Nodes[i]].num_clust += 1
    if (Cluster2_Nodes[i] in Cluster0_Nodes):
        Node[Cluster2_Nodes[i]].num_clust += 1
        
i = 0
for i in range(len(Cluster[2].Nodes)):
    print(Cluster[2].Nodes[i].num_clust)

#%%
                
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

Boundary = []

i = 0            
for i in range(len(Node)):
    if (Node[i].isBoundary == True):
        Boundary.append(Node[i].index)
        


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

#%%
Facility_Affiliations = []

i = 0
for i in range(len(Node)):
    if (Node[i].cluster == 0):
        Facility_Affiliations.append("Mykawa")
    if (Node[i].cluster == 1):
        Facility_Affiliations.append("Stafford")
    if (Node[i].cluster == 2):
        Facility_Affiliations.append("Sweetwater")
    if (Node[i].cluster == "None"):
        Facility_Affiliations.append("None")
"""        
delivs["Facility Affiliations"] = Facility_Affiliations

writer = pd.ExcelWriter("May_24_Clustering_Results.xlsx", engine='xlsxwriter')
delivs.to_excel(writer, sheet_name = "Clustering Results")
writer.save()
"""