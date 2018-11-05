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
        self.cluster = "None"
        
        self.isOutside = True
        self.isRoot = False
        
        self.Pred = []
        self.pred_idx = []
        self.child = "None"
        self.distance = "None"
        
        self.isExtensible = False
        self.isReachable = False
        self.reachable = []
        self.reachability = 0
        
        self.best_reach = "None"
        self.best_ext = "None"
        self.preferred_cluster = "None"
        self.min_reachable_dist = "None"
        
        self.num_clust = 0
        
        self.isBoundary = False
        self.best_adj_boundary = "None"
        self.trial_distance = "None"

    def calc_distance(self):
        dist = "None"
        
        if (self.isOutside == True):
            print("Node is not assigned to a cluster.")
            return dist
        elif (self.isRoot == True):
            dist = 0
            return dist
        else:
            dist = 0
            
            i = 1
            while i <= (len(self.Pred) - 1):
                dist += haversine(self.Pred[i-1].coords, self.Pred[i].coords)
                i += 1
            dist += haversine(self.Pred[len(self.Pred) - 1].coords, self.coords)
        
            return dist
    

    def print_node(self, Node):
        print("Node " + str(self.index) + " Information:")
        
        print(" ") 
        if self.isOutside == True:
            print("Node " + str(self.index) + " is outside.")
        else:
            print("Node " + str(self.index) + " is not outside.")
        
        print(" ") 
        if (self.cluster == "None"):
            print("Node " + str(self.index) + " is not assigned to a cluster.")
        else:
            print("Node " + str(self.index) + " is assigned to Cluster " + str(self.cluster) + ".")
            
        print(" ") 
        print("The following nodes are predecessors of Node " + str(self.index))
        print(self.pred_idx)
        print("Node " + str(self.child.index) + " is the immediate successor of Node " + str(self.index))
        print("Distance of Node " + str(self.index) + " is " + str(self.distance))
        
        print(" ") 
        if self.isExtensible == True:
            print("Node " + str(self.index) + " is extensible.")
        else:
            print("Node " + str(self.index) + " is not extensible.")
         
        if self.isReachable == True:
            print("Node " + str(self.index) + " is reachable.")
        else:
            print("Node " + str(self.index) + " is not reachable.")
            
        print(" ")     
        print("Reachable nodes from Node " + str(self.index) + ":")
        print(self.reachable)
        
        print(" ")     
        print("Adjacent nodes to Node " + str(self.index) + ":")
        
        k = 0
        for k in range(len(self.adj_nodes)):
            print("Node " + str(Node[self.adj_nodes[k]].index))
            print("Distance to adj = " + str(haversine(self.coords, Node[self.adj_nodes[k]].coords)))
            if Node[self.adj_nodes[k]].isOutside == True:
                print("Node " + str(Node[self.adj_nodes[k]].index) + " is outside.")
            if Node[self.adj_nodes[k]].isReachable == True:
                print("Node " + str(Node[self.adj_nodes[k]].index) + " is reachable.")
            if Node[self.adj_nodes[k]].isExtensible == True:
                print("Node " + str(Node[self.adj_nodes[k]].index) + " is reachable.")
                
        print(" ")
        print("The best preferred cluster for Node " + str(self.index) + " is Cluster " + str(self.preferred_cluster))
        print("The best extensible node for Node " + str(self.index) + " is Node " + str(self.best_ext.index))
        print("The best reachable node from Node " + str(self.index) + " is Node " + str(self.best_reach.index))
        print("Node " + str(self.index) + " has a minimum reachable distance of " + str(self.min_reachable_dist))

