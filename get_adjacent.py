#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 17 13:40:17 2018

@author: igmcnelis

This function takes the coordinates of a node of interest, along with the 
outputs of scipy.spatial's voronoi function (vor).
"""

def get_adjacent(point, vor):

    #Generate necessary lists for operations to be performed
    reg = vor.point_region
    input_points = vor.points
    ridge = vor.ridge_points  
    reg_verts_idx = vor.regions
    
    i = 0

    for i  in range(len(reg_verts_idx)):
        if (-1 in reg_verts_idx[i]):
            reg_verts_idx[i].remove(-1)
    
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
        if (vertex != -1):
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
    
    return adj_nodes
    