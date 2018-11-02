#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 21 21:20:25 2018

@author: igmcnelis
"""

class cluster:
    def __init__(self, centroid, balance_target, capac):
        
        self.index = 0
        self.Nodes = [centroid]
        self.nodes_idx = [centroid.index]
        self.centroid = centroid 
        
        self.balance_target = balance_target
        self.capac = capac
        self.weight = 0
        
        self.isExtensible = False
        
        self.extensible = []
        self.reachable = []
        self.best_extensible = "None"
        self.best_reachable = "None"

    def calc_centroid(self):
        
        s_long = 0
        s_lat = 0
        
        i = 0
        for i in range(len(self.Nodes)):
            s_long += self.Nodes[i].coords[0]
            s_lat += self.Nodes[i].coords[1]
        
        centr_coords = (s_long/len(self.Nodes), s_lat/len(self.Nodes))
        
        return centr_coords
    
    def print_cluster(self, Node):
        print("Cluster " + str(self.index) + " Information:")
        print(" ") 
        
        if(self.isExtensible == True):
            print("Cluster " + str(self.index) + " is extensible.")
        
        print("Extensible:")
        print(self.extensible)
        print("Reachable:")
        print(self.reachable)
        
        j = 0
        for j in range(len(self.Nodes)):
            print(" ") 
            print("Node " + str(self.Nodes[j].index) + " Information:")
            print(" ") 
            print("Node " + str(self.Nodes[j].index) + " is assigned to Cluster " + str(Node[self.Nodes[j].index].cluster))
            
            if self.Nodes[j].isOutside == False:
                print("Node " + str(self.Nodes[j].index) + " is not outside.")
            else:
                print("Somethin's fucky, Node " + str(self.Nodes[j].index) + " is outside.")
                
            if self.Nodes[j].isExtensible == True:
                print("Node " + str(self.Nodes[j].index) + " is extensible.")
            else:
                print("Node " + str(self.Nodes[j].index) + " is not extensible.")
                
            print(" ")     
            print("Reachable nodes from Node " + str(self.Nodes[j].index) + ":")
            print(self.Nodes[j].reachable)
            
            print(" ")     
            print("Nodes adjacent to Node " + str(self.Nodes[j].index) + ":")
            
            k = 0
            for k in range(len(self.Nodes[j].adj_nodes)):
                print("Node " + str(Node[self.Nodes[j].adj_nodes[k]].index))
                if Node[self.Nodes[j].adj_nodes[k]].isOutside == True:
                    print("Node " + str(Node[self.Nodes[j].adj_nodes[k]].index) + " is outside.")
                if Node[self.Nodes[j].adj_nodes[k]].isReachable == True:
                    print("Node " + str(Node[self.Nodes[j].adj_nodes[k]].index) + " is reachable.")
                    
        print(" ")           
        print("The best reachable node from cluster " + str(self.index) + " is Node " + str(self.best_reachable.index))
        print("The best extensible node fin cluster " + str(self.index) + " is Node " + str(self.best_extensible.index))
