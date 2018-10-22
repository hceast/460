# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d
from read_customers_local import get_df
from get_adjacent import get_adjacent
from haversine import haversine
from Node import node
from Cluster import cluster

dist_center, mykawa_deliv_517, mykawa_deliv_524, stafford_deliv_517, stafford_deliv_524, sweetwater_deliv_517, sweetwater_deliv_524 = get_df()

deliv_517 = pd.concat([mykawa_deliv_517, stafford_deliv_517, sweetwater_deliv_517], ignore_index = True)
deliv_517 = deliv_517[["Longitude", "Latitude", "Deliv Packages Qty"]].copy()

vor = Voronoi(deliv_517[["Longitude", "Latitude"]], qhull_options="Qbb Qc Qx")
voronoi_plot_2d(vor)
fig = plt.figure()
plt.show()

all_adj = []

i=0
for i in range(len(vor.points)):
    point = (vor.points[i][0], vor.points[i][1])
    adj_pts = get_adjacent(point, vor)
    all_adj.append(adj_pts)
    
se = pd.Series(all_adj)
deliv_517["Adj Nodes"] = se.values

#%%
from Node import node
Node = [node((deliv_517["Longitude"][i], deliv_517["Latitude"][i]), deliv_517["Deliv Packages Qty"][i], deliv_517["Adj Nodes"][i]) for i in range(len(deliv_517))]

Node[0].isOutside = False 
Node[0].Pred = [Node[1], Node[4]]

coords1 = Node[1].coords
coords2 = Node[4].coords
coords3 = Node[0].coords

print(Node[0].distance())
d_comp = haversine(coords1[0], coords1[1], coords2[0], coords2[1]) + haversine(coords2[0], coords2[1], coords3[0], coords3[1])
print(d_comp)

#%%
from Cluster import cluster

Cluster1 = cluster((0,0), 9999)
Cluster1.Nodes = [Node[0], Node[1], Node[2]]

coords1 = Node[0].coords
coords2 = Node[1].coords
coords3 = Node[2].coords

print(Cluster1.calc_centroid())
print((coords1[0]+coords2[0]+coords3[0])/3)
print((coords1[1]+coords2[1]+coords3[1])/3)

