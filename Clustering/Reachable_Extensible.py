#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  4 13:47:30 2018

@author: igmcnelis

"""
from Node import node
from Cluster import cluster

def get_reach_and_ext(Cluster, Node):
    #Takes two lists, Cluster and Nodes, that should be lists of the cluster and node class objects
    #Determines the extensible and reachable node sets for the clusters, and the reachable node sets
    #for every extensible node.
    
    i = 0
    for i in range(len(Cluster)):
        #Reset the sets at the cluster level
        Cluster[i].reachable = []
        Cluster[i].extensible = []
        
        j = 0
        #Step through the set of all nodes in Cluster[i]
        for j in range(len(Cluster[i].Nodes)):
            #There is no extensible set at the node level. Reset the reachable set for the node that is selected
            Cluster[i].Nodes[j].reachable = []
            #Loop through the list of adjacent nodes for every node in the node set.
            #If a node is an element of outside, and is adjacent to a node that is assigned 
            #to a cluster, it is a reachable node. Additionally, the clustered node that 
            #is adjacent to this outside node is extensible.
            k = 0
            for k in range(len(Cluster[i].Nodes[j].adj_nodes)):
                if (Node[Cluster[i].Nodes[j].adj_nodes[k]].isOutside == True):
                    #If adjacent to a clustered node and outside, node is reachable.
                    Node[Cluster[i].Nodes[j].adj_nodes[k]].isReachable = True
                    #Add to the list of nodes reachable from Cluster[i].Node[j]
                    Cluster[i].Nodes[j].reachable.append(Cluster[i].Nodes[j].adj_nodes[k])
                    #Add the adjacent node to the cluster's list of adjacent nodes if it is not
                    #already present in the list.
                    if (Cluster[i].Nodes[j].adj_nodes[k] not in Cluster[i].reachable):
                        Cluster[i].reachable.append(Cluster[i].Nodes[j].adj_nodes[k])
                else:
                    #If the adjacent node is not outside, it cannot be reachable
                    Node[Cluster[i].Nodes[j].adj_nodes[k]].isReachable = False
            #If a clustered node is adjacent to an outside nodes, it is extensible.
            if (len(Cluster[i].Nodes[j].reachable) != 0):
                #So long as there is at least 1 node that is reachable from Cluster[i].Node[j],
                #Cluster[i].Node[j] is extensible
                Cluster[i].Nodes[j].isExtensible = True
                #Add extensible nodes to the cluster's list of extensible nodes if it is not
                #already present in the list.
                if (Cluster[i].Nodes[j].index not in Cluster[i].extensible):
                    Cluster[i].extensible.append(Cluster[i].Nodes[j].index)
            else:
                #If there are no nodes that are reachable from Cluster[i].Node[j], it is not extensible.
                Cluster[i].Nodes[j].isExtensible = False
        #If a cluster has at least 1 extensible node, the cluster is extensible
        if (len(Cluster[i].extensible) != 0):
            Cluster[i].isExtensible = True
        else:
            Cluster[i].isExtensible = False
    
    #Loop through the node set and inspect all of the nodes that are classified reachable and track the number
    #of extensible nodes that are adjacent to the reachable node. If there are no extensible nodes that are adjacent
    #to the reachable node, it shouldn't be reachable. Correct the discrepency.
    i = 0
    for i in range(len(Node)):
        if (Node[i].isReachable == True):
            num_ext = 0
            
            j = 0
            for j in range(len(Node[i].adj_nodes)):
                if (Node[Node[i].adj_nodes[j]].isExtensible == True):
                    num_ext += 1
            
            if (num_ext == 0):
                Node[i].isReachable = False
            
 