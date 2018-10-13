# -*- coding: utf-8 -*-
"""
Created on Fri Oct 12 18:45:11 2018

@author: heast
"""

import pulp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from clarke_wright import clarke_wright

file_loc = pd.read_csv(r"C:\Users\heast\Documents\Tamu\460\Coding\git\Coords_517.txt", sep = ",", header = None)
locations = np.concatenate(([[-95.3211,29.6759]],file_loc.loc[0:206].values), axis = 0)

#Sample addresses - first pair is depot
'''
locations = \
                [(4, 4), # depot
                 (2, 0), (8, 0), # row 0
                 (0, 1), (1, 1),
                 (5, 2), (7, 2),
                 (3, 3), (6, 3),
                 (5, 5), (8, 5),
                 (1, 6), (2, 6),
                 (3, 7), (6, 7),
                 (0, 8), (7, 8)]
demands = \
            [0, # depot
             1, 1, # 1, 2
             2, 4, # 3, 4
             2, 4, # 5, 6
             8, 8, # 7, 8
             1, 2, # 9,10
             1, 2, # 11,12
             4, 4, # 13, 14
             8, 8] # 15, 16
''' 
demands = pd.read_csv(r"C:\Users\heast\Documents\Tamu\460\Coding\git\Deliv_517.txt", header = None)
#demands = [1 for i in range(len(locations))]
#demands = file_demand.loc[0:207].values
demands = demands.loc[:207]
route = clarke_wright(locations, demands)

#print routes generated
fig = plt.figure()
ax = fig.add_subplot(111)

ax.scatter([i[0] for i in locations],[j[1] for j in locations])

for index,row in route.iterrows():
    for i in range(len(row.Path)):
        if (i == 0):
            #(x,depot_x), (y, depot_y)
            #print(0, " ", row.Path[i])
            ax.plot((locations[row.Path[i]][0], locations[0][0]), (locations[row.Path[i]][1], locations[0][1]), 'ro-')
        
        elif (i == len(row.Path) - 1):
            #print(row.Path[i], " ", 0)
            ax.plot((locations[row.Path[i]][0], locations[0][0]), (locations[row.Path[i]][1], locations[0][1]), 'ro-')
            break
        
        #print(row.Path[i], " " , row.Path[i+1])
        ax.plot((locations[row.Path[i]][0], locations[row.Path[i+1]][0]), (locations[row.Path[i]][1], locations[row.Path[i+1]][1]), 'ro-')
