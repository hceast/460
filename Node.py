#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 14 19:22:53 2018

@author: igmcnelis
"""

class Node:
    def __init__(self, node_index, region, coords, region_vertices, ridges):
        self.node_index = node_index
        self.region = region
        self.coords = coords
        self.region_vertices = region_vertices
        self.ridges = ridges
                