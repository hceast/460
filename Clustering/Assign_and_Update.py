#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  4 14:52:45 2018

@author: igmcnelis
"""
from Node import node
from Cluster import cluster

def assign_and_update(C_star, q_star, p_star):
    
    #Once you know your C_star, you know your q_star which is associated with a p_star
    q_star = C_star.best_reachable
    p_star = C_star.best_extensible
                    
    #Add q_star to Cluster
    C_star.Nodes.append(q_star)
    C_star.nodes_idx.append(q_star.index)
    q_star.cluster = C_star
    
    #Update cluster weight and capacity
    C_star.weight += q_star.weight
    C_star.capac -= q_star.weight
    
    #Update predecessor path information about q_star
    q_star.Pred.extend(p_star.Pred)
    q_star.Pred.append(p_star)
    q_star.pred_idx.extend(p_star.pred_idx)
    q_star.pred_idx.append(p_star.index)
    #Set q_star as the immediate successor of p_star
    p_star.child = q_star
    
    #Calculate distance function value for node
    q_star.distance = q_star.calc_distance()