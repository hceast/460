# -*- coding: utf-8 -*-
"""
Created on Wed Oct 17 22:47:33 2018

@author: heast
"""

import pandas as pd
import matplotlib.pyplot as plt
from math import radians, cos, sin, asin, sqrt
from clarke_wright import clarke_wright
import time
from scipy.spatial import Delaunay, Voronoi, voronoi_plot_2d
from collections import defaultdict
import itertools
from read_customers import get_df
import numpy as np
import string

#plots clarke_wright routing given a dataframe p of one center's customers
#currently runs all clarke-wright calculations and then plots - doesnt just take calculated routes
# and plot those
def cw_plot(p, d):
    #Capacity of truck
    capacity = 150
    
    #demand of each customer-- depot has 0 demand and is first
    demand = np.concatenate(([0],p.loc[:,'Deliv Packages Qty'].values))
    demands = pd.DataFrame(demand)
    
    #find location address
    for index,row in d.iterrows():
        if (d.loc[index,'Center Num'] == p.loc[0,'Center Num']):
            
            break
    
    #locations of customers - depot is first
    locations = np.concatenate(([[d.loc[index,'Longitude'], d.loc[index,'Latitude']]], np.concatenate(([p.loc[:,'Longitude']],[p.loc[:,'Latitude']])).T))
    
    #Delaunay triangulation to find nearest neighbors
    tri = Delaunay(locations, qhull_options = 'QJ')
    neighbor = defaultdict(set)
    for point in tri.vertices:
        for i,j in itertools.combinations(point,2):
            neighbor[i].add(j)
            neighbor[j].add(i)
    
    #creates routing with clarke wright
    route = clarke_wright(locations, demands, neighbor, capacity)
    
    #print routes generated
    fig = plt.figure()
    plt.ylabel('Latitude')
    plt.xlabel('Longitude')
    
    title = d.loc[index,'Facility'].title() + ' Routing ' + str(p.loc[0,'Day Date'].month) + '/' + str(p.loc[0,'Day Date'].day) + '/' + str(p.loc[0,'Day Date'].year)
    plt.title(title)
    ax = fig.add_subplot(111)
    
    color_line = ['bo-','go-','ro-','co-','mo-','yo-']

    ax.scatter([i[0] for i in locations],[j[1] for j in locations])
    
    
    ########## do this a better way
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
    #return locations
    
def delaunay_plot(p, d):
    #find location address
    for index,row in d.iterrows():
        if (d.loc[index,'Center Num'] == p.loc[0,'Center Num']):
            break
    
    #locations of customers - depot is first
    locations = np.concatenate(([[d.loc[index,'Longitude'], d.loc[index,'Latitude']]], np.concatenate(([p.loc[:,'Longitude']],[p.loc[:,'Latitude']])).T))
        
    tri = Delaunay(locations, qhull_options = 'QJ')
    #neighbor = defaultdict(set)
    #for p in tri.vertices:
    #    for i,j in itertools.combinations(p,2):
    #        neighbor[i].add(j)
    #        neighbor[j].add(i)
            
    plt.triplot(locations[:,0], locations[:,1], tri.simplices.copy())
    plt.plot(locations[1:,0], locations[1:,1], 'o')
    plt.plot(locations[0,0], locations[0,1], 'ro', markersize = 15)
    plt.ylabel('Latitude')
    plt.xlabel('Longitude')
    
    title = 'Delaunay Triangulation: ' + d.loc[index,'Facility'].title() + ' ' + str(p.loc[0,'Day Date'].month) + '/' + str(p.loc[0,'Day Date'].day) + '/' + str(p.loc[0,'Day Date'].year)
    plt.title(title)
    plt.show()

def main():
    dist, my_517, my_524, staf_517, staf_524, swee_517, swee_524 = get_df()
    
    cw_plot(my_517, dist)
    cw_plot(my_524, dist)
    cw_plot(staf_517, dist)
    cw_plot(staf_524, dist)
    cw_plot(swee_517, dist)
    cw_plot(swee_524, dist)