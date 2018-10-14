#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 13 20:43:44 2018

@author: igmcnelis
"""
from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

Coords = np.array([[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]])

vor = Voronoi(Coords)

voronoi_plot_2d(vor)
plt.show()

fig = plt.figure()
plt.hold(True)

#%%
# Mark the Voronoi vertices.
plt.plot(vor.vertices[:,0], vor.vertices[:, 1], 'ko', ms=8)

for vpair in vor.ridge_vertices:
    if vpair[0] >= 0 and vpair[1] >= 0:
        v0 = vor.vertices[vpair[0]]
        v1 = vor.vertices[vpair[1]]
        # Draw a line from v0 to v1.
        plt.plot([v0[0], v1[0]], [v0[1], v1[1]], 'k', linewidth=2)

plt.show()
#%%
from freud import voronoi

vor = voronoi.Voronoi
Coords = np.array([[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]], dtype=np.float32)
first_shell = vor.computeNeighbors(Coords).getNeighbors(1)
second_shell = vor.computeNeighbors(Coords).getNeighbors(2)
print('First shell:', first_shell)
print('Second shell:', second_shell)

#%%