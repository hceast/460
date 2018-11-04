#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  4 16:01:41 2018

@author: igmcnelis
"""

def priority_weight(Cluster):
    
    Weight_Improvement = []
    
    i = 0
    for i in range(len(Cluster)):
        #Current deviation from target weight
        current_deviation = ""
        current_deviation = abs(Cluster[i].weight - Cluster[i].balance_target)
        #Deviation should the best reachable node we are examining be added
        new_deviation = ""
        new_deviation = abs((Cluster[i].weight + Cluster[i].best_reachable.weight) - Cluster[i].balance_target)
        
        #Weight_Improvement.append(current_deviation - new_deviation)
        
        #Weighted against distance. Acceptable results alone. Catastrophic when used with tiebreaker.
        Weight_Improvement.append((current_deviation - new_deviation)*(1/Cluster[i].best_reachable.min_reachable_dist))
        
    #Weightbalance Tiebreak
    best_improvement = max(Weight_Improvement)
    candidates = []
    
    #Find the ones that tie
    i = 0
    for i in range(len(Weight_Improvement)):
        if (Weight_Improvement[i] == best_improvement):
            candidates.append(i)
    #If there are no ties, select the cluster as above
    if (len(candidates) > 1):
        """
        #Find the one that also minimizes distance.
        Min_Reach_Dist = []
        
        i = 0
        for i in range(len(candidates)):
            Min_Reach_Dist.append(Cluster[candidates[i]].best_reachable.min_reachable_dist)
        
        C_star = candidates[Min_Reach_Dist.index(min(Min_Reach_Dist))]
        """
        Card = []
        
        i = 0
        for i in range(len(candidates)):
            Card.append(len(Cluster[candidates[i]].Nodes))
        
        C_star = Cluster[candidates[Card.index(min(Card))]]

    else:
        C_star = Cluster[Weight_Improvement.index(max(Weight_Improvement))]
        
    return C_star

def priority_card(Cluster):

    Card = []
        
    i = 0
    for i in range(len(Cluster)):
        Card.append(len(Cluster[i].Nodes))
    
    min_card = min(Card)
    candidates = []
    
    #Find the ones that tie
    i = 0
    for i in range(len(Card)):
        if (Card[i] == min_card):
            candidates.append(i)
    #If there are no ties, select the cluster as above
    if (len(candidates) > 1):
        """
        #Find the one that also minimizes distance.
        Min_Reach_Dist = []
        
        i = 0
        for i in range(len(candidates)):
            Min_Reach_Dist.append(Cluster[candidates[i]].best_reachable.min_reachable_dist)
        
        C_star = candidates[Min_Reach_Dist.index(min(Min_Reach_Dist))]
        """
        Weight_Improvement = []
        
        i = 0
        for i in range(len(candidates)):
            #Current deviation from target weight
            current_deviation = ""
            current_deviation = abs(Cluster[candidates[i]].weight - Cluster[i].balance_target)
            #Deviation should the best reachable node we are examining be added
            new_deviation = ""
            new_deviation = abs((Cluster[i].weight + Cluster[i].best_reachable.weight) - Cluster[i].balance_target)
            
           # Weight_Improvement.append(current_deviation - new_deviation)
            Weight_Improvement.append((current_deviation - new_deviation)*(1/Cluster[i].best_reachable.min_reachable_dist))
            
        C_star = Cluster[candidates[Weight_Improvement.index(max(Weight_Improvement))]]

    else:
        C_star = Cluster[Card.index(min(Card))]

    return C_star