#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 13 20:43:44 2018

@author: igmcnelis
"""
from scipy.spatial import Voronoi, voronoi_plot_2d
from scipy.spatial import Delaunay
from collections import defaultdict
import itertools
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

#Read-in Delivery coordinates
#Coords = np.array([[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]])
Coords = pd.read_csv("Coords_517.txt", sep = ",", header = None)

#%%
#Create and plot the Voronoi diagram
vor = Voronoi(Coords, qhull_options="Qbb Qc Qx")
voronoi_plot_2d(vor)
fig = plt.figure()
plt.show()

#%%
#Perform Delaunay triangulation, and get node adjacencies
Del_tri = Delaunay(Coords, qhull_options = "QJ")
neighbors = Del_tri.neighbors 
Del_nei = defaultdict(set)
for p in Del_tri.vertices:
    for i,j in itertools.combinations(p,2):
        Del_nei[i].add(j)
        Del_nei[j].add(i)
        
#Print node adjacenices to the console
for i in range(len(Del_nei)):
    print(i, ":", Del_nei[i])
    
#Plot Delaunay triangulation
plt.triplot(Coords.values[:, 0], Coords.values[:, 1], Del_tri.simplices.copy())
plt.plot(Coords.values[:, 0], Coords.values[:, 1], "o")
#plt.triplot(Coords[:, 0], Coords[:, 1], Del_tri.simplices.copy())
#plt.plot(Coords[:, 0], Coords[:, 1], "o")
plt.figure()
plt.show()
#%%
#Create plot of overlay of Delaunay triangulation onto the Voronoi diagram
img = voronoi_plot_2d(vor)

plt.triplot(Coords.values[:, 0], Coords.values[:, 1], Del_tri.simplices.copy())
plt.plot(Coords.values[:, 0], Coords.values[:, 1], "o")
fig = plt.figure()
fig.add_subplot()     
    
#%%
#Determining node adjacency based on neighboring Thiessen polygons:
from get_adjacent import get_adjacent

#Given a node with known coordinates:
#point = (0, 0)
point = (Coords[0][14], Coords[1][14])

get_adjacent(point, vor)


#%%
#Generate necessary lists for operations to be performed
reg = vor.point_region
input_points = vor.points
ridge = vor.ridge_points  
verts = vor.vertices
reg_verts_idx = vor.regions

i = 0

for i  in range(len(reg_verts_idx)):
    if (-1 in reg_verts_idx[i]):
        reg_verts_idx[i].remove(-1)

#Given a node with known coordinates:
#point = (1, 1)
point = (Coords[0][14], Coords[1][14])

#Determine critical node information:
#Locate the node the within the Voronoi diagram and save its index
i = 0
for i in range(len(input_points)):
    if (point[0] == input_points[i][0]) and (point[1] == input_points[i][1]):
        point_index = i
        break
    else:
        i += 1
    
#Get the region of the node, i.e. the index of the point's Thiessen poly w/in the Voronoi diagram
point_region = reg[point_index]


#Get the vertices of the region
pt_region_verts = reg_verts_idx[point_region]


#Determine adjacencies:
#Create a list that determines node adjacency based on Voronoi ridges
adj_points_ridge = []

i = 0
for i in range(len(ridge)):
    if (ridge[i][0] == point_index):
        adj_points_ridge.append(ridge[i][1])
        i += 1
        
    elif (ridge[i][1] == point_index):
        adj_points_ridge.append(ridge[i][0])
        i += 1
    
    else:
        i += 1

#Create a list of Thiessen polys that share vertices with the given node's polygon 
adj_reg_verts = []
vertex = ""

i = 0
j = 0
k = 0
for i in range(len(pt_region_verts)):
    vertex = pt_region_verts[i]
    for j in range(len(reg_verts_idx)):
        if (j != point_region):
            for k in range(len(reg_verts_idx[j])):
                if (reg_verts_idx[j][k] == vertex):
                    if (j not in adj_reg_verts):
                        adj_reg_verts.append(j)
                        
#Converts region back to points                        
adj_pts_verts = []

i = 0
j = 0
for i in range(len(adj_reg_verts)):
    for j in range(len(reg)):
        if (reg[j] == adj_reg_verts[i]):
            adj_pts_verts.append(j)
            break

#Determine final node adjacency list:
adj_nodes = []

i = 0
for i in range(len(adj_points_ridge)):
    adj_nodes.append(adj_points_ridge[i])

#adj_points_ridge.append(100)

i = 0
j = 0

for i in range(len(adj_pts_verts)):
    if (adj_pts_verts[i] not in adj_nodes):
        adj_nodes.append(adj_pts_verts[i])

#%%
from get_adjacent import get_adjacent

all_adj = []

i=0
for i in range(len(vor.points)):
    point = (vor.points[i][0], vor.points[i][1])
    adj_pts = get_adjacent(point, vor)
    all_adj.append(adj_pts)
    
#%