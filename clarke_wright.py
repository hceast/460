# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 11:24:21 2018

@author: heast
"""

import pulp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import radians, cos, sin, asin, sqrt

def haversine(long1, lat1, long2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    long1, lat1, long2, lat2 = map(radians, [long1, lat1, long2, lat2])

    # haversine formula 
    dlong = long2 - long1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlong/2)**2
    c_ = 2 * asin(sqrt(a)) 
    r_ = 3956 # Radius of earth in kilometers. Use 6371 for miles
    return c_ * r_

'''
Clarke and wright algorithm for vehicle routing on a single depot

takes all customer addresses as input. Address of depot is first address in list
takes all demands of each customer as a separate list

want to have both inputs stored in one dataframe eventually
'''
def clarke_wright(locations, demand):     
    #calculate c_ij
    c = []
    for i in range(len(locations)):
        #c += [[pow(pow(locations[i][0] - locations[j][0],2) + pow(locations[i][1] - locations[j][1],2),.5) for j in range(len(locations))]]
         c += [[haversine(locations[i][0], locations[i][1], locations[j][0], locations[j][1]) for j in range(len(locations))]]
    
    #cost in var c
    #demand in var demands
    
    #Clarke Wright- 3 steps
    #1. compute savings s(i,j) for all pairs of customers
    #2. Choose pair with largest savings and check if combining them is feasible
        #if yes- combine routes
        #if no- go to next largest
    #3. Continue step 3 while all savings positive
        #stop when all positive savings have been considered
    
    #cost from i to j
    #cost matrix from book
    #c = [[0,20,57,51,50,10,15,90],[20,0,51,10,55,25,30,53],[57,51,0,50,20,30,10,47],[51,10,50,0,50,11,60,38],[50,55,20,50,0,50,60,10],[10,25,30,11,50,0,20,90],[15,30,10,60,60,20,0,12],[90,53,47,38,10,90,12,0]]
    #c =[[0,4,4,2.83,4,5,2,4.24],[4,0,5.66,6.32,8,8.54,4.47,3.16],[4,5.66,0,2.83,5.66,8.06,6,7.62],[2.83,6.32,2.83,0,2.83,5.39,4.47,7.07],[4,8,5.66,2.83,0,3,4.47,7.62],[5,8.54,8.06,5.39,3,0,4.12,7], [2,4.47,6,4.47,4.47,4.12,0,3.16],[4.24,3.16,7.62,7.07,7.62,7,3.16,0]]
    
    #demand at each customer
        #dummy demand of 0 at depot
    #demand from book
    #demand = [0,46,55,33,30,24,75,30]
    #demand = [0,12,12,6,16,15,10,8]
    
    
    #capacity of each truck
    #cap = 80
    cap = 300
    
    
    #create pandas multi index and savings list
    ind = []
    s = []
    route = pd.DataFrame({'Demand':demand.loc[1:,0].values})
    route['Path'] = [[i] for i in range(1,len(c))]
    #route[1] = [np.nan for i in range(1,len(c))]
    
    for i in range(1, len(c)):
        
        for j in range(i+1,len(c)):
            ind += [(i,j)]
            s += [c[0][i] + c[0][j] - c[i][j]]
            
    #a = [0 for i in range(len(ind))]       
    index = pd.MultiIndex.from_tuples(ind, names=['i','j'])
    df = pd.DataFrame({'Savings':s},index=index)
    df = df.sort_values(by=['Savings'], ascending = False)
    
    #iterate through all savings
    for row in df.itertuples():
        #if savings not postive, break
        if (row.Savings < 0):
            break
        
        #savings is positive, check if valid combination
        
        #capacity constraint-- can only add if demand is lower than capacity
        #inside loop constraint- can only add to route that touches depot--beginning or end of list
        
        #iterate through all routes created
        for i,r in route.iterrows():
            tmp_bool = False
            
            #adding j to end of i
            #if customer i looked at is last customer visited in route
            if (r['Path'][-1] == row.Index[0]):
                for i1,r1 in route.iterrows():
                    #if customer j is not added to any route and if demand satisfied
                    if (r1['Path'][0] == row.Index[1] and r1['Path'][-1] == row.Index[1] and (r['Demand'] + r1['Demand'] <= cap)):
                        #record new capacity
                        route.at[i,'Demand'] = r['Demand'] + r1['Demand']
                            
                        #j becomes new end of path
                        route.at[i,'Path'] = route.loc[i,'Path'] + [row.Index[1]]
                            
                        #delete row for j
                        route = route.drop([i1])
                            
                        #set flag
                        tmp_bool = True
                        
                    #go to next savings
                    if (tmp_bool):
                        break
            #if customer i is first customer visited in route
            elif (r['Path'][0] == row.Index[0]):
                for i1,r1 in route.iterrows():
                    #if customer j is not added to any route
                    if (r1['Path'][0] == row.Index[1] and r1['Path'][-1] == row.Index[1] and (r['Demand'] + r1['Demand'] <= cap)):
                        #record new capacity
                        route.at[i,'Demand'] = r['Demand'] + r1['Demand']
                        
                        #j becomes new end of path
                        route.at[i,'Path'] = [row.Index[1]] + route.loc[i,'Path']
                        
                        #delete row for j
                        route = route.drop([i1])
                        
                        #set flag
                        tmp_bool = True
                        
                    #go to next savings
                    if (tmp_bool):
                        break
            #if customer j is last customer visited in route
            elif (r['Path'][-1] == row.Index[1]):
                for i1,r1 in route.iterrows():
                    #if customer i is not added to any route
                    if (r1['Path'][0] == row.Index[0] and r1['Path'][-1] == row.Index[0] and (r['Demand'] + r1['Demand'] <= cap)):
                        #record new capacity
                        route.at[i,'Demand'] = r['Demand'] + r1['Demand']
                        
                        #i becomes new end of path
                        route.at[i,'Path'] = route.loc[i,'Path'] + [row.Index[0]]
                        
                        #delete row for i
                        route = route.drop([i1])
                        
                        #set flag
                        tmp_bool = True
                        
                    #go to next savings
                    if (tmp_bool):
                        break
             #if customer j is first customer visited in route
            elif (r['Path'][0] == row.Index[1]):
                for i1,r1 in route.iterrows():
                    #if customer i is not added to any route
                    if (r1['Path'][0] == row.Index[0] and r1['Path'][-1] == row.Index[0] and (r['Demand'] + r1['Demand'] <= cap)):
                        #record new capacity
                        route.at[i,'Demand'] = r['Demand'] + r1['Demand']
                        
                        #i becomes new end of path
                        route.at[i,'Path'] = [row.Index[0]] + route.loc[i,'Path']
                        
                        #delete row for i
                        route = route.drop([i1])
                        
                        #set flag
                        tmp_bool = True
                        
                    #go to next savings
                    if (tmp_bool):
                        break
            if (tmp_bool):
                break
     
    #display routes created       
    print(route)
    
    return route


"""
Example 15.8 Vehicle Routing Problem
http://support.sas.com/documentation/cdl/en/ormpug/67517/HTML/default/viewer.htm#ormpug_decomp_examples14.htm
"""






