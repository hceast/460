# -*- coding: utf-8 -*-
"""
Created on Fri Oct 12 18:45:11 2018

@author: heast
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from clarke_wright import clarke_wright, format_dat
import time
from scipy.spatial import Delaunay, Voronoi, voronoi_plot_2d
from collections import defaultdict
from read_customers import get_df
import itertools
from plotting import cw_plot, delaunay_plot
from get_adjacent import get_adjacent, adj_set

start_clock = time.time()

dist, my_517, my_524, staf_517, staf_524, swee_517, swee_524 = get_df()


############# Only runs for single depot
###file_loc = pd.read_csv(r"C:\Users\heast\Documents\Tamu\460\Coding\git\Coords_517.txt", sep = ",", header = None)
###locations = np.concatenate(([[-95.3211,29.6759]],file_loc.loc[0:206].values), axis = 0)

#demands = pd.read_csv(r"C:\Users\heast\Documents\Tamu\460\Coding\git\Deliv_517.txt", header = None)
##demands = demands.loc[:207]

locations, demands = format_dat(my_517, dist)


#capcity of vehicle
cap = 150

nei = adj_set(locations)

#calculate list of adjacent polygons in Voronoi diagram
tri = Delaunay(locations, qhull_options = 'QJ')
neighbor = defaultdict(set)
for p in tri.vertices:
    for i,j in itertools.combinations(p,2):
        neighbor[i].add(j)
        neighbor[j].add(i)
        
plt.triplot(locations[:,0], locations[:,1], tri.simplices.copy())
plt.plot(locations[1:,0], locations[1:,1], 'o')
plt.plot(locations[0,0], locations[0,1], 'ro', markersize = 15)
plt.show()

#for i in range(len(neighbor)):
#    print(i,':',neighbor[i])
        
route = clarke_wright(locations, demands, neighbor, cap)
route2 = clarke_wright(locations, demands, nei, cap)

    
'''
for i in range(len(neighbor)):
    print(i,':',neighbor[i])
#Plot voronoi
vor = Voronoi(locations)
fig = voronoi_plot_2d(vor)

for i,p in enumerate(locations):
    plt.text(p[0], p[1], '#%d' % i, ha='center')
plt.show()
'''

print("Time elapsed (s): ", time.time()-start_clock)
print("Time elapsed (min): ", (time.time()-start_clock)/60)

color_line = ['bo-','go-','ro-','co-','mo-','yo-']

#print routes generated
fig = plt.figure()
ax = fig.add_subplot(111)

ax.scatter([i[0] for i in locations],[j[1] for j in locations])

color_i = 0
for index,row in route.iterrows():
    if(color_i == 5):
        color_i = 0
    for i in range(len(row.Path)):
        if (i == 0):
            #(x,depot_x), (y, depot_y)
            #print(0, " ", row.Path[i])
            ax.plot((locations[row.Path[i]][0], locations[0][0]), (locations[row.Path[i]][1], locations[0][1]), color_line[color_i])
        
        elif (i == len(row.Path) - 1):
            #print(row.Path[i], " ", 0)
            ax.plot((locations[row.Path[i]][0], locations[0][0]), (locations[row.Path[i]][1], locations[0][1]), color_line[color_i])
            break
        
        if(len(row.Path) > 1):
            #print(row.Path[i], " " , row.Path[i+1])
            ax.plot((locations[row.Path[i]][0], locations[row.Path[i+1]][0]), (locations[row.Path[i]][1], locations[row.Path[i+1]][1]), color_line[color_i])
    color_i = color_i + 1