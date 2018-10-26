#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 14 19:22:53 2018
@author: igmcnelis
"""

from haversine import haversine

class node:
    def __init__(self, index, coords, deliv_vol, adj_nodes):
        
        self.index = index
        self.coords = coords
        self.weight = deliv_vol
        self.adj_nodes = adj_nodes
        self.cluster = 0
        
        self.isOutside = True
        self.isRoot = False
        self.isExtensible = False
        self.isReachable = False
        
        self.Pred = []
        self.pred_idx = []
        self.child = 0
        #self.best_neighbor = []
        
        self.distance = -1
        self.min_reachable_dist = 0
        
        self.reachable = []

    def calc_distance(self):
        dist = self.distance
        
        if (self.isOutside == True):
            print("Node is not assigned to a cluster.")
            return -1
        elif (self.isRoot == True):
            dist = 0
        else:
            i = 1
            while i <= (len(self.Pred) - 1):
                dist += haversine(self.Pred[i-1].coords, self.Pred[i].coords)
                i += 1
            dist += haversine(self.Pred[len(self.Pred) - 1].coords, self.coords)
        
        return dist
    
"""
    def print_node(self, attr):
        print(self.Pred)

                
