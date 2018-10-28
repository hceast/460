#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 21 21:20:25 2018

@author: igmcnelis
"""
from scipy.spatial import Voronoi
from adjacent import get_adjacent

class cluster:
    def __init__(self, centroid, balance_target, capac):
        
        self.index = 0
        self.Nodes = []
        self.nodes_idx = []
        self.centroid = centroid 
        
        self.balance_target = balance_target
        self.capac = capac
        self.weight = 0
        
        self.isExtensible = False
        
        self.extensible = []
        self.reachable = []
        self.best_extensible = 0
        self.best_reachable = 0

    def calc_centroid(self):
        
        s_long = 0
        s_lat = 0
        
        i = 0
        for i in range(len(self.Nodes)):
            s_long += self.Nodes[i].coords[0]
            s_lat += self.Nodes[i].coords[1]
        
        centr_coords = (s_long/len(self.Nodes), s_lat/len(self.Nodes))
        
        return centr_coords
