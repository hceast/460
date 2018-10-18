# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 11:24:21 2018

@author: heast
"""

#import pulp
import pandas as pd
import matplotlib.pyplot as plt
from math import radians, cos, sin, asin, sqrt


####################
### may want to establish neighbor, c, cap, and max duration as global variables
    #so they dont all need to be passed


#############

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

def feasible_merge(i,j,route,df_customer, neighbor, c, cap, max_dur):
    #checks if combining two routes results in a valid merge
        #capcity
        #if two nodes already belong to the same route
        #can add time constraints in future
    
    #if either of two nodes are interior-- may not be correct (one interior may be allowed)
    if ((df_customer.loc[i-1,'Status'] == 2) or (df_customer.loc[j-1,'Status'] == 2)):
        return False
    
    #gets index in route that i and j belong to
    r_i = df_customer.loc[i-1,'Route_Index']
    r_j = df_customer.loc[j-1,'Route_Index']
    
    #if both nodes belong to same route
    if(r_i == r_j):
        return False
    
    #if vehicle capacity exceeded
    if(route.loc[r_i,'Demand'] + route.loc[r_j,'Demand'] > cap):    
        #print('merging',i,'and',j,'exceeds vehicle capacity')
        return False
   
    #max trip duration cannot be exceeded
    if ((route.loc[r_i,'Travel_time'] + route.loc[r_j,'Travel_time'] - c[0][i] - c[0][j]) > max_dur):
        return False
    
    #checks if to nodes share an edge in the Voronoi diagram
    #next_nei is true if j is a neighbor of a neighbor of i
    next_nei = False
    if (j not in neighbor[i]):
        #relaxation to allow next neighbor delivery -- if j is a neighbor of one of i's neighbors
        for i1 in set(neighbor[i]):
            if (j in neighbor[i1]):
                next_nei = True
                break
        if(not next_nei):
            return False
    
    return True

def calc_cost(locations, route, c):
    cost = 0
    
    for index,row in route.iterrows():
        for i in range(len(route.loc[index,'Path'])):
            if (i == 0):
                cost = cost + c[0][route.loc[index,'Path'][i]]
            if (i == (len(route.loc[index,'Path']) - 1)):
                cost = cost + c[0][route.loc[index,'Path'][i]]
                break
            cost = cost + c[route.loc[index,'Path'][i]][route.loc[index,'Path'][i+1]]
    
    return cost
                    
def travel_time(route, index, c):
    #estimate vehicle speed ~25-30mph
    v_speed = 25
    v_speed = v_speed/60 #miles/minute
    #buffer window for loading/unloading time ~15 minutes
    buffer = 15  #minutes
    
    #get loading and unloading times for all customers
    time = buffer * len(route.loc[index,'Path'])
    for i in range(len(route.loc[index,'Path'])):
        if (i == 0):
            time = time + c[0][route.loc[index,'Path'][i]] * v_speed
        if (i == (len(route.loc[index,'Path']) - 1)):
            time = time + c[0][route.loc[index,'Path'][i]] * v_speed
            break
        time = time + c[route.loc[index,'Path'][i]][route.loc[index,'Path'][i + 1]] * v_speed
    return time    


def clarke_wright(locations, demand, neighbor, cap):     
    #max allowed route duration-- expand to be duration only including trips to customers
        #also expand to factor in 3.5 hours needed for a driver
    max_dur = 300   #5 hours -- 300 minutes
    #number of all nodes excluding depot
    n_customers = len(locations)-1
    
    #calculate c_ij
    c = []
    for i in range(n_customers +1):
        #c += [[pow(pow(locations[i][0] - locations[j][0],2) + pow(locations[i][1] - locations[j][1],2),.5) for j in range(len(locations))]]
         c += [[haversine(locations[i][0], locations[i][1], locations[j][0], locations[j][1]) for j in range(n_customers + 1)]]
    
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
    #cap = 15
    
    #create pandas multi index and savings list
    ind = []
    s = []
    route = pd.DataFrame({'Demand':demand.loc[1:,0].values})
    route['Path'] = [[i] for i in range(1,n_customers+1)]
    route['Travel_time'] = [travel_time(route, i, c) for i in range(n_customers)]
    route['Num_Stops'] = [1 for i in range(n_customers)]
    for i in range(1, n_customers+1):
        for j in range(i+1,n_customers+1):
            ind += [(i,j)]
            s += [c[0][i] + c[0][j] - c[i][j]]
            
    index = pd.MultiIndex.from_tuples(ind, names=['i','j'])
    df = pd.DataFrame({'Savings':s},index=index)
    df = df.sort_values(by=['Savings'], ascending = False)
    
    #create list of if nodes are unused (0), added(1), interior(2)
        #only need to update route index for nodes whose status become added
    df_customer = pd.DataFrame({'Status': [0 for i in range(n_customers)],'Route_Index':[i for i in range(n_customers)]})
    
    #print(df)
    #iterate through all savings
    #for each combination of savings (i,j)
    for row in df.itertuples():
        #if savings not postive, break
        if (row.Savings < 0):
            break
        
        #savings is positive, check if valid combination
        
        #capacity constraint-- can only add if demand is lower than capacity
        #inside loop constraint- can only add to route that touches depot--beginning or end of list
        
        #row.Index[0] is customer i, row.Index[1] is customer j
        
        #checking feasibility first
        if(feasible_merge(row.Index[0],row.Index[1],route,df_customer, neighbor, c, cap, max_dur)):
            #if both i and j are unused
            if(df_customer.loc[row.Index[0]-1,'Status'] == 0 and df_customer.loc[row.Index[1]-1,'Status'] == 0):
                r_i = df_customer.loc[row.Index[0]-1,'Route_Index']
                r_j = df_customer.loc[row.Index[1]-1,'Route_Index']
                
               ########Create function that handles updating dataframe and handling route merges
                
                #merge two routes
                route.at[r_i,'Path'] = route.loc[r_i,'Path'] + [row.Index[1]]
                
                #record new cumulative demand
                route.at[r_i,'Demand'] = route.loc[r_i,'Demand'] + route.loc[r_j,'Demand']
                
                #record new route travel time
                route.at[r_i,'Travel_time'] = travel_time(route, r_i, c)
                
                #record new number of stops for route
                route.at[r_i,'Num_Stops'] = route.loc[r_i,'Num_Stops'] + route.loc[r_j,'Num_Stops']
                
                #delete row for j
                route = route.drop([r_j])
                       
                #status i = added, status j = added
                df_customer.at[row.Index[0]-1,'Status'] = 1
                df_customer.at[row.Index[1]-1,'Status'] = 1
                
                #record new route index for j
                df_customer.at[row.Index[1]-1,'Route_Index'] = r_i
                #print('both unused Combine:',row.Index[0],'and', row.Index[1], '--', route.loc[r_i,'Path'])
        #if i added and j unused
            elif(df_customer.loc[row.Index[0]-1,'Status'] == 1 and df_customer.loc[row.Index[1]-1,'Status'] == 0):
                r_i = df_customer.loc[row.Index[0]-1,'Route_Index']
                r_j = df_customer.loc[row.Index[1]-1,'Route_Index']
                
                #merge two routes
                #if i is at front- add j to front
                if(route.loc[r_i,'Path'][0] == row.Index[0]):
                    #if travel time not acceptable
                    #break
                    route.at[r_i,'Path'] = [row.Index[1]] + route.loc[r_i,'Path']
                    
                #if i is at end- add j to back
                else:
                    route.at[r_i,'Path'] = route.loc[r_i,'Path'] + [row.Index[1]]
                
                #record new cumulative demand
                route.at[r_i,'Demand'] = route.loc[r_i,'Demand'] + route.loc[r_j,'Demand']
                
                #record new route travel time
                route.at[r_i,'Travel_time'] = travel_time(route, r_i, c)
                
                #record new number of stops for route
                route.at[r_i,'Num_Stops'] = route.loc[r_i,'Num_Stops'] + route.loc[r_j,'Num_Stops']
                
                #delete row for j
                route = route.drop([r_j])
                       
                #status i = interior, status j = added
                df_customer.at[row.Index[0]-1,'Status'] = 2
                df_customer.at[row.Index[1]-1,'Status'] = 1
                
                #record new route index for j
                df_customer.at[row.Index[1]-1,'Route_Index'] = r_i
                #print('i added, j unused, Combine:',row.Index[0],'and', row.Index[1], '--', route.loc[r_i,'Path'])
                
            #if i unused and j added
            elif(df_customer.loc[row.Index[0]-1,'Status'] == 0 and df_customer.loc[row.Index[1]-1,'Status'] == 1):
                r_i = df_customer.loc[row.Index[0]-1,'Route_Index']
                r_j = df_customer.loc[row.Index[1]-1,'Route_Index']
                
                #merge two routes
                #if j is at front- add i to front
                if(route.loc[r_j,'Path'][0] == row.Index[1]):
                    route.at[r_j,'Path'] = [row.Index[0]] + route.loc[r_j,'Path']
                    
                #if j is at end- add i to back
                else:
                    route.at[r_j,'Path'] = route.loc[r_j,'Path'] + [row.Index[0]]
                
                #record new cumulative demand
                route.at[r_j,'Demand'] = route.loc[r_i,'Demand'] + route.loc[r_j,'Demand']
                
                #record new route travel time
                route.at[r_j,'Travel_time'] = travel_time(route, r_j, c)
                
                #record new number of stops for route
                route.at[r_j,'Num_Stops'] = route.loc[r_i,'Num_Stops'] + route.loc[r_j,'Num_Stops']
                
                #delete row for i
                route = route.drop([r_i])
                       
                #status i = added, status j = interior
                df_customer.at[row.Index[0]-1,'Status'] = 1
                df_customer.at[row.Index[1]-1,'Status'] = 2
                
                #record new route index for i
                df_customer.at[row.Index[0]-1,'Route_Index'] = r_j
                #print('i unused, j added, Combine:',row.Index[0],'and', row.Index[1], '--', route.loc[r_j,'Path'])
                
            #if i and j added
            elif(df_customer.loc[row.Index[0]-1,'Status'] == 1 and df_customer.loc[row.Index[1]-1,'Status'] == 1):
                #if mergence feasible
                    #merge two routes
                    #status i = interior, status j = interior
                
                r_i = df_customer.loc[row.Index[0]-1,'Route_Index']
                r_j = df_customer.loc[row.Index[1]-1,'Route_Index']
                
                #merge two routes
                
                #true if i,j is the beginning node in respective route,
                i_begin = (route.loc[r_i,'Path'][0] == row.Index[0])
                j_begin = (route.loc[r_j,'Path'][0] == row.Index[1])
                
                #need to change row index of opposite side of route j
                if(j_begin):
                    df_customer.at[route.loc[r_j,'Path'][-1]-1,'Route_Index'] = r_i
                else:
                    df_customer.at[route.loc[r_j,'Path'][0]-1,'Route_Index'] = r_i
                
                #if i is at end and j is at front
                if(not(i_begin) and j_begin):
                    #add route j to end of route i
                    route.at[r_i,'Path'] = route.loc[r_i,'Path'] + route.loc[r_j,'Path']
                    
                #if i is at end and j is at end
                elif(not(i_begin) and not(j_begin)):
                    #reverse array holding route j and add to end of i
                    route.loc[r_j,'Path'].reverse()
                    route.at[r_i,'Path'] = route.loc[r_i,'Path'] + route.loc[r_j,'Path']
                #if i is at front and j is at front
                elif(i_begin and j_begin):
                    #reverse array holding route j and add to beginning of i
                    route.loc[r_j,'Path'].reverse()
                    route.at[r_i,'Path'] = route.loc[r_j,'Path'] + route.loc[r_i,'Path']
                #if i is at front and j is at end
                else:
                    #add j to beginning of i
                    route.at[r_i,'Path'] = route.loc[r_j,'Path'] + route.loc[r_i,'Path']
                
                #record new cumulative demand
                route.at[r_i,'Demand'] = route.loc[r_i,'Demand'] + route.loc[r_j,'Demand']
                
                #record new route travel time
                route.at[r_i,'Travel_time'] = travel_time(route, r_i, c)
                
                #record new number of stops for route
                route.at[r_i,'Num_Stops'] = route.loc[r_i,'Num_Stops'] + route.loc[r_j,'Num_Stops']
                
                #delete row for i
                route = route.drop([r_j])
                       
                #status i = interior, status j = interior
                df_customer.at[row.Index[0]-1,'Status'] = 2
                df_customer.at[row.Index[1]-1,'Status'] = 2
                #print('i added, j added, Combine:',row.Index[0],'and', row.Index[1])
                #print('i added, j added, Combine:',row.Index[0],'and', row.Index[1], '--', route.loc[r_i,'Path'])
                
        
        #if i and j = interior
            #skip
        
        '''
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
            '''
    cost = calc_cost(locations, route, c)
    #display routes created       
    #print(route)
    #print('Total Cost:',cost)
    return route


"""
Example 15.8 Vehicle Routing Problem
http://support.sas.com/documentation/cdl/en/ormpug/67517/HTML/default/viewer.htm#ormpug_decomp_examples14.htm
"""
def test():
    
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
    demand = \
                [0, # depot
                 1, 1, # 1, 2
                 2, 4, # 3, 4
                 2, 4, # 5, 6
                 8, 8, # 7, 8
                 1, 2, # 9,10
                 1, 2, # 11,12
                 4, 4, # 13, 14
                 8, 8] # 15, 16
    
    demands = pd.DataFrame(demand)
    #demands = pd.read_csv(r"C:\Users\heast\Documents\Tamu\460\Coding\git\Deliv_517.txt", header = None)
    #demands = demands.loc[:207]
    
    #vehicle capacity
    cap = 15
    route = clarke_wright(locations, demands, cap)
    
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
    

    
