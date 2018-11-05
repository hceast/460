#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  4 14:26:59 2018

@author: igmcnelis
"""
from Node import node
from Cluster import cluster
from haversine import haversine

def best_reach_ext_nodes(Node):
    i = 0
    for i in range(len(Node)):
        min_dist = "None"
        
        if (Node[i].isExtensible == True):
            
            j = 0
            for j in range(len(Node[i].adj_nodes)):
                
                if (Node[Node[i].adj_nodes[j]].isReachable == True):
                    dist = Node[i].distance + haversine(Node[i].coords, Node[Node[i].adj_nodes[j]].coords)
                    
                    if (min_dist == "None"):
                        min_dist = dist
                        Node[i].best_reach = Node[Node[i].adj_nodes[j]]
                    elif (dist < min_dist):
                        min_dist = dist
                        Node[i].best_reach = Node[Node[i].adj_nodes[j]]
                        
        if (Node[i].isReachable == True):
            
            j = 0
            for j in range(len(Node[i].adj_nodes)):
                
                if (Node[Node[i].adj_nodes[j]].isExtensible == True):
                    dist = Node[Node[i].adj_nodes[j]].distance + haversine(Node[Node[i].adj_nodes[j]].coords, Node[i].coords)
                    
                    if (min_dist == "None"):
                        min_dist = dist
                        Node[i].best_ext = Node[Node[i].adj_nodes[j]]
                        Node[i].preferred_cluster = Node[Node[i].adj_nodes[j]].cluster
                    elif (dist < min_dist):
                        min_dist = dist
                        Node[i].best_ext = Node[Node[i].adj_nodes[j]]
                        Node[i].preferred_cluster = Node[Node[i].adj_nodes[j]].cluster
                        
            Node[i].min_reachable_dist = min_dist
            
def best_reach_ext_clusters(Cluster):
    i = 0
    for i in range(len(Cluster)):
        
        if (Cluster[i].isExtensible == True):
            min_dist = "None"
            
            j = 0
            for j in range(len(Cluster[i].Nodes)):
                
                if(Cluster[i].Nodes[j].isExtensible == True):
                    if (min_dist == "None"):
                        min_dist = Cluster[i].Nodes[j].best_reach.min_reachable_dist
                        Cluster[i].best_extensible = Cluster[i].Nodes[j]
                        Cluster[i].best_reachable = Cluster[i].Nodes[j].best_reach
                    elif (Cluster[i].Nodes[j].best_reach.min_reachable_dist < min_dist):
                        min_dist = Cluster[i].Nodes[j].best_reach.min_reachable_dist
                        Cluster[i].best_extensible = Cluster[i].Nodes[j]
                        Cluster[i].best_reachable = Cluster[i].Nodes[j].best_reach
    