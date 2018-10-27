#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 17 13:40:17 2018

@author: igmcnelis

This function takes the coordinates of a node of interest, along with the 
outputs of scipy.spatial's voronoi function (vor).
"""

from scipy.spatial import Delaunay, Voronoi, voronoi_plot_2d
from collections import defaultdict

def get_adjacent(point, vor):

    #Create a nested list that stores the vertices for every Thiessen polygon
    verts = vor.vertices
    reg_verts_index = vor.regions
    
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
    input_points = vor.points
    reg = vor.point_region
    
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
    ridge = vor.ridge_points
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
    
    return adj_nodes

#gets adjacent nodes from Voronoi and creates set of neighbors
#delaunay neighbors and thiesen neighbors are showing pretty different results
def adj_set(p):
    #using "Qbb Qc Qx" still has empty sets
    #vor = Voronoi(p, qhull_options="Qbb Qc Qx")
    vor = Voronoi(p, qhull_options="QJ")
    
    nei = defaultdict(set)
    for index in range(len(p)):
        tmp = get_adjacent(p[index], vor)
        for i in range(len(tmp)):
            nei[index].add(tmp[i])
        
    return nei

    