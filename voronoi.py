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
point = (Coords[0][0], Coords[1][0])

get_adjacent(point, vor)
#[145, 142, 6, 167, 206, 144]

#%%
#Generate necessary lists for operations to be performed
reg = vor.point_region
input_points = vor.points
ridge = vor.ridge_points  
verts = vor.vertices
reg_verts_index = vor.regions

#Create a nested list that stores the vertices for every Thiessen polygon
i = 0
j = 0
reg_verts = [[] for i in range(len(reg_verts_index))]

for i  in range(len(reg_verts_index)):
    if (-1 in reg_verts_index[i]):
        reg_verts_index[i].remove(-1)
    reg_verts[i] = [0 for i in range(len(reg_verts_index[i]))]
    for j in range (len(reg_verts_index[i])):
        reg_verts[i][j] = [verts[(reg_verts_index[i][j])][0], verts[(reg_verts_index[i][j])][1]]

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
point_region_verts = reg_verts[point_region]


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
for i in range(len(point_region_verts)):
    vertex = (point_region_verts[i][0], point_region_verts[i][0]) 
    for j in range(len(reg_verts)):
        if (j != point_region):
            if (len(reg_verts[j]) == 1):
                if (vertex[0] == reg_verts[j][0][0]) and (vertex[1] == reg_verts[j][0][1]):
                        adj_reg_verts.append(j)
            else:
                for k in range(len(reg_verts[j])):
                    if (vertex[0] == reg_verts[j][k][0]) and (vertex[1] == reg_verts[j][k][1]):
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
adj_nodes = adj_pts_verts
#adj_points_ridge.append(100)

i = 0
j = 0

for i in range(len(adj_points_ridge)):
    if (adj_points_ridge[i] not in adj_pts_verts):
        adj_nodes.append(adj_points_ridge[i])
            
#%%
NodeList = []
#for i in range(len(Coords)):
#    NodeList.append("Node" + str(i + 1))

from Node import Node

i = 0
Node = Node(0, reg[0], (point_index[0][0], point_index[0][1]), reg_verts[0])

#%%
"""
# Mark the Voronoi vertices.
plt.plot(vor.vertices[:,0], vor.vertices[:, 1], 'ko', ms=8)

for vpair in vor.ridge_vertices:
    if vpair[0] >= 0 and vpair[1] >= 0:
        v0 = vor.vertices[vpair[0]]
        v1 = vor.vertices[vpair[1]]
        # Draw a line from v0 to v1.
        plt.plot([v0[0], v1[0]], [v0[1], v1[1]], 'k', linewidth=2)

plt.show()
"""
#%