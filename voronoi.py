#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 13 20:43:44 2018

@author: igmcnelis
"""
from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

Coords = np.array([[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]])
#Coords = pd.read_csv("Coords_517.txt", sep = ",", header = None)

vor = Voronoi(Coords, qhull_options="Qbb Qc Qx")
voronoi_plot_2d(vor)
plt.show()
fig = plt.figure()
plt.hold(True)

#%%
input_points = vor.points
ridge = vor.ridge_points

point = (input_points[0][0], input_points[0][1])

i = 0
for i in range(len(input_points)):
    if (point[0] == input_points[i][0]) and (point[1] == input_points[i][1]):
        point_index = i
        break
    else:
        i += 1

print(point_index)

#point_index = 4
adjacent_points_ridge = []
i = 0
for i in range(len(ridge)):
    if (ridge[i][0] == point_index):
        adjacent_points_ridge.append(ridge[i][1])
        i += 1
        
    elif (ridge[i][1] == point_index):
        adjacent_points_ridge.append(ridge[i][0])
        i += 1
    
    else:
        i += 1
    
    

#%%
verts = vor.vertices

reg_verts_index = vor.regions

i = 0
j = 0
reg_verts = [0 for i in range(len(reg_verts_index))]

for i  in range(len(reg_verts_index)):
    reg_verts[i] = [0 for i in range(len(reg_verts_index[i]))]
    for j in range (len(reg_verts_index[i])):
        if (reg_verts_index[i][j]) >= 0:
            reg_verts[i][j] = [verts[(reg_verts_index[i][j])][0], verts[(reg_verts_index[i][j])][1]]
        else:
            reg_verts[i][j] = -1

'''
NodeList = []
#for i in range(len(Coords)):
#    NodeList.append("Node" + str(i + 1))

from Node import Node

i = 0
Node = Node(0, reg[0], (point_index[0][0], point_index[0][1]), reg_verts[0])
'''
#%%
# Mark the Voronoi vertices.
plt.plot(vor.vertices[:,0], vor.vertices[:, 1], 'ko', ms=8)

for vpair in vor.ridge_vertices:
    if vpair[0] >= 0 and vpair[1] >= 0:
        v0 = vor.vertices[vpair[0]]
        v1 = vor.vertices[vpair[1]]
        # Draw a line from v0 to v1.
        plt.plot([v0[0], v1[0]], [v0[1], v1[1]], 'k', linewidth=2)

plt.show()
#%