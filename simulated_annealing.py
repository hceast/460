# -*- coding: utf-8 -*-
"""
Created on Thu Oct 18 15:07:59 2018

@author: heast
"""
from __future__ import division 

import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random
from random import random, randint,uniform,choice
import pandas as pd
import time

'''
TO DO:
    [X] calculate cost matrix before anneal and allow lookup of values
    [] create better neighbor transformations
    [] add constraints
        [] demand
        [] capacity
        [] trip duration
        [] time windows
    [] animate process
    [] Use ClarkeWright as initialization
    [] finish move transformation
    [] 2-opt local search
'''

#Simulated annealing takes a dataframe of customer information -- X,Y coordinate, num packages needed
    #time window constraints...
    #Route is a dictionary storing driver information. There need to be as many dictionary entries as the max available drivers
        #annealing will add and remove from routes in dictionary but will NOT create new dictionary entries.
        #Route also stores information such as cumulative trip duration, capacity used...
            #can be expanded so that individual trucks have different capacities/ trip durations allowed
    #cost_mat is the distance matrix between any two locations (includes depot and all customers)
        #Euclidian distance is used for now but it would be better to import driving time distance
    #T is the temperature -- try 100 but set small so that it can potentially be called multiple times by main program
    #i_max is max iterations before temperature change - initialized to 10 but should be 100-1000
def anneal(df, route, cost_mat, T = 10, i_max = 10):
    old_cost = cost(route)
    best_cost = old_cost
    best_sol = route.copy()
    
    #if there is only one route and has less than two customers return
    if(len(route) == 1):
        if (not (len(route[1]['Path']) > 2)):
            return best_sol, best_cost
        
    #sets parameters for T_min and cooling rate, alpha -- could also be passed as values into function
    T_min = 0.00001
    alpha = .9
    iter_ = 1
    
    #displays parameters used in SA
    param_ = f'Temp = {T}, T_min = {T_min}, Alpha = {alpha}, Max_iter = {i_max}'
    #print('SA parameters:')
    #print(param_)
   
    while T > T_min:
        i = 1
        
        #tracks how many iterations have passed without improvement
        i_improve = 1
        
        while i <= i_max:
            '''
            #if no improvement in solution after 20% of iterations, raise temperature by 10%
            if (i_improve >= i_max * .2):
                T = T * 1.1
                print(T)
                i_improve = -i_max
            else:
                i_improve += 1
            '''
            
            iter_+=1
            new_route = route.copy()
            neighbor(new_route, df, cost_mat)
            init_costs(df,new_route, cost_mat)
            new_cost = cost(new_route)
            
            #ap = acceptance_probability(old_cost, new_cost, T)
            if(new_cost < best_cost):
                    best_sol = new_route.copy()
                    best_cost = new_cost
                    route = best_sol.copy()
                    old_cost = best_cost
                    
            elif np.exp((new_cost - old_cost)/T) > uniform(0,1):
                route = new_route.copy()
                old_cost = new_cost
            i += 1
            
        T = T*alpha
    return best_sol, best_cost

#uses distance for now
    #will be faster if cost matrix calculated before hand and values are called as needed
def cost(route):
    #will probably not use this format however we can modify to include costs such as not meeting
        #travel time of 3.5 hours, adding extra drivers, excess travel distance...
        
    #using formula Cost = aR + bD
    #cost = constant * num Routes + constant * total distance of all routes
    # a = 10000 and b = 1 recommended -- goal to reduce number of drivers
    a = 1000
    b = 10
    tmp_cost = 0
    n_route = 0
    for i in range(len(route)):
        if (len(route[i+1]) > 0):
            n_route = n_route + 1
            
        tmp_cost = tmp_cost + route[i+1]['Cost']
    
    tmp_cost = a * n_route + b * tmp_cost
    return tmp_cost

#gets cost of one route
def route_cost(df, path, cost_mat):
    if len(path['Path']) > 0:
        
        #adds cost of travel from depot to first customer and from last customer to depot
        #path['Cost'] = dist([df.loc[path['Path'][0],'X'],df.loc[path['Path'][0],'Y']], [df.loc[0,'X'],df.loc[0,'Y']]) + dist([df.loc[path['Path'][-1],'X'],df.loc[path['Path'][-1],'Y']], [df.loc[0,'X'],df.loc[0,'Y']])
        path['Cost'] = cost_mat[0][path['Path'][0]] + cost_mat[path['Path'][-1]][0]
        
        #adds cost of travel from customer to customer
        for i in range(len(path['Path']) - 1):
            #path['Cost'] = path['Cost'] + dist([df.loc[path['Path'][i],'X'],df.loc[path['Path'][i],'Y']], [df.loc[path['Path'][i+1],'X'],df.loc[path['Path'][i+1],'Y']])
            path['Cost'] = path['Cost'] + cost_mat[path['Path'][i]][path['Path'][i+1]]
    #if route has no customers then 0 cost
    else:
        path['Cost'] = 0
        
def dist(a,b):
    return ((a[0]-b[0])**2 + (a[1]-b[1])**2)**.5

def neighbor_indv(route):
    #gets neighboring solution for an individual
        #route is a dictionary for one drivers routes
    path = route['Path']
    
    #if driver only has one or two route assigned then nothing can be done
    if (len(path) > 2):
        p = uniform(0,1)
        if p < .2:
            # cut sequence somewhere in first half, swap first and second part,
            # cut again at new point in first half and reverse first part 
            i = randint(0,math.floor(len(path)/2))
            path = path[i:] + path[:i]
            
            i = randint(0, math.floor(len(path) / 2))
            tmp = path[:i]
            tmp = tmp[::-1]
            path = tmp + path[i:]
        elif p < .6:
            # move randomly chosen city to a randomly chosen new position in sequence
            i = randint(0, len(path) - 1)
            a = path.pop(i)
            j = randint(1, len(path) - 1)
            path.insert(j,a)
        else:
            p1 = randint(0,math.floor(len(path)/2))
            p2 = randint(math.floor(len(path)/2)+1,len(path)-1)
            tmp = path[p1]
            path[p1] = path[p2]
            path[p2] = tmp
    else:
        print('Too few customers in route')
        
def neighbor(route, df, cost_mat):
    if (len(route)==1):
        neighbor_indv(route[1])
    else:
        neighbor_group(route, df, cost_mat)
    return route

def neighbor_group(route, df, cost_mat):
    p = uniform(0,1)
    
    #keeps track of which routes are used
    used = []
    unused = []
    for i in range(len(route)):
        if len(route[i+1]['Path']) > 0:
            used += [[i+1,len(route[i+1]['Path'])]]
        else:
            unused += [i+1]
    
    #add routes or split routes
    if (p < .4):
        p1 = uniform(0,1)
        
        #if all routes used then add routes
        if (len(unused) == 0):
            add_route(route,used)
            
        #if only one route used then split routes
        elif (len(used) == 1):
            cut_route(route,used,unused)
            
        #otherwise 50/50 chance of adding/splitting
        #add two routes together
        #only if more than one route
        elif(p1 < .5):
            add_route(route,used)
              
        #split one route into two new routes
        else:
            cut_route(route,used,unused)
            
    #take first part of a route and add to another existing route
    else:
        #Taking from one existing route and adding to another
        #Need at least two existing routes
        if (len(used) > 1):
            #print('suffle')
            #pick random route that has customers assigned to it
            i = np.random.randint(len(used))
                
            #route picked needs at least two customers -- otherwise it is ADD
            if (used[i][1] > 1):
                #pick random customer i1 assigned to route
                i1 = np.random.randint(used[i][1]-1)
                
                #get all customers of route up to i1
                tmp = route[used[i][0]]['Path'][:i1 + 1]
                
                #reset route i to only include customers after i1
                route[used[i][0]]['Path'] = route[used[i][0]]['Path'][i1 + 1:]
                
                #pick customer j that is not i
                j = i
                while (j == i):
                    j = np.random.randint(len(used))
                
                route[used[j][0]]['Path'] += tmp
                
                #two opt move on new routes?
                
                
                
def add_route(route, used):
    #print('add')
        
    i = np.random.randint(len(used))
    j = i
    while (j == i):
        j = np.random.randint(len(used))
            
    route[used[j][0]]['Path'] += route[used[i][0]]['Path']
    route[used[i][0]]['Path'] = []

    #perform some operation to ensure routes combined in reasonable manner
    #create large penalty costs and assign it during cost function
    #i.e. having over capacity is a penalty of 10000, more than x trucks is a penalty of ##########...

def cut_route(route,used,unused):
    #print('cut')

    #used_2 is all used routes that have at least 2 deliveries on the route
    used_2 = []
    for i in range(len(used)):
        if (used[i][1] > 1):
            used_2 += [used[i][0]]
           
    #i is the route being split
    i = np.random.randint(len(used_2))
    
    #j is the customer address being split at
    j = np.random.randint(len(route[used_2[i]]['Path'])-1)
    
    #get all deliveries up to j
    tmp = route[used_2[i]]['Path'][:j+1]
    
    #set route as all deliveries after j
    route[used_2[i]]['Path'] = route[used_2[i]]['Path'][j+1:]
    
    #assign deliveries up to j to a new route
    route[unused[0]]['Path'] = tmp
    
def move(df, route, cost_mat):
    #move neighborhood transformation from - A Simulated Annealing Algorithm for the Capacitated Vehicle Routing Problem.
    #finds # pairs of customers that have the shortest distance to eachother
    
    #paper recommends 5 but may not be feasible- test with 2
    pair_num = 5
    
    #initialize with a large distance
    pair = [[0,0,999999999]]
    
    #iterate through all used routes
    for i in range(1,len(route)+1):
        if (len(route[i]['Path']) > 0):
            #check if last customer in route to depot is in top 5  shortest
            for k in range(len(pair)):
                #insert info into pair before first route that has longer distance
                if (cost_mat[route[i]['Path'][-1]][0] < pair[k][2]):
                    pair.insert(k,[route[i]['Path'][-1],0,cost_mat[route[i]['Path'][-1]][0]])
                    break
            
            #check all other customers in route
            for j in range(len(route[i]['Path']) - 1):
                for k in range(len(pair)):
                    if (cost_mat[route[i]['Path'][j]][route[i]['Path'][j + 1]] < pair[k][2]):
                        pair.insert(k,[route[i]['Path'][j],route[i]['Path'][j+1],cost_mat[route[i]['Path'][j]][route[i]['Path'][j + 1]]])
                        break
                        
    #filter data to only include top # shortest
    pair = pair[:pair_num]
    
    #select 5 random customers that do not include depot or customers in the second column of pair
    #generates list of valid customers
    valid = [i for i in range(1,len(df))]
    for i in range(len(pair)):
        for j in range(len(valid)):
            if (pair[i][1] == valid[j]):
                valid.pop(j)
                break
    
    #select pair_num of random customers
            
    #remove these customers from route and add to new random route
def acceptance_probability(old_cost, new_cost, T):
    return math.exp((new_cost - old_cost)/T)

#updates route cost for all routes
def init_costs(df, routes, cost_mat):
    for i in range(len(routes)):
        route_cost(df,routes[i+1], cost_mat)

def plot_route(df, routes):
    fig, ax = plt.subplots()
    ax.grid = True
    ax.set_xlim(0,10)
    ax.set_ylim(0,10)
    x,y = [],[]
    for i in range(len(routes)):
        x += [df.loc[0,'X']]
        y += [df.loc[0,'Y']]
        
        p = routes[i+1]['Path']
        for j in range(len(p)):
            
            x += [df.loc[p[j],'X']]
            y += [df.loc[p[j],'Y']]
    
        x += [df.loc[0,'X']]
        y += [df.loc[0,'Y']]
    
    ax.plot(x, y, 'k-')
    plt.show()
    
def dist_mat(df):
    c = [[99999.0 for i in range(len(df))] for i in range(len(df))]
    for i in range(len(df)):
        for j in range(i, len(df)):
            c[i][j] = dist([df.loc[i,'X'], df.loc[i,'Y']], [df.loc[j,'X'], df.loc[j,'Y']])
            c[j][i] = c[i][j]
    return c

#prints route information
def route_stat(route):
    n_route = 0
    avg_cost = 0.0
    total_cost = 0.0
    min_cost = 99999999.9
    max_cost = 0.0
    
    for i in range(len(route)):
        
        if (len(route[i+1]['Path']) > 0):
            n_route = n_route + 1
            total_cost = total_cost + route[i+1]['Cost']
            
            if (min_cost > route[i+1]['Cost']):
                min_cost = route[i+1]['Cost']
            if (max_cost < route[i+1]['Cost']):
                max_cost = route[i+1]['Cost']
    
    avg_cost = total_cost / n_route
    
    str1 = f'Number of Routes = {n_route}, Total Cost = {total_cost}'
    str2 = f'avg_cost = {avg_cost}, Min cost = {min_cost}, Max Cost = {max_cost}'
    print('\n')
    print(str1)
    print(str2)

def line(p1, p2):
    A = (p1[1] - p2[1])
    B = (p2[0] - p1[0])
    C = (p1[0]*p2[1] - p2[0]*p1[1])
    return A, B, -C

def intersection(p1, p2, p3, p4):
    L1 = line(p1,p2)
    L2 = line(p3,p4)
    
    D  = L1[0] * L2[1] - L1[1] * L2[0]
    Dx = L1[2] * L2[1] - L1[1] * L2[2]
    Dy = L1[0] * L2[2] - L1[2] * L2[0]
    if D != 0:
        x = Dx / D
        y = Dy / D
        
        if ((x > p1[0]) and (x > p2[0])) or ((x < p1[0]) and (x < p2[0])) or ((x > p3[0]) and (x > p4[0])) or ((x < p3[0]) and (x < p4[0])):
            return False
        
        return True
    else:
        return False
    
#searches for crossing in individual route
#does not work for arcgis mapping -- only euclidian
def two_opt(df, route):
    #need at least three distinct customers before crossing can occur
    if (len(route) <= 2):
        print('too small for crossing')
        return
    
    path = []
    path += [0]
    for i in range(len(route)):
        path += [route[i]]
    path += [0]
    
    #bool for if crossing was found
    #if crossing found, restart search after iteration
    cross = True
    
    #hopefully wont make infinite loop
    while cross:
        cross = False
        #find crossing between v1, v2 and v3,v4
        for i in range(len(path)-2):
            for j in range(i + 2, len(path)-1):
                #including j in range i+2 should prevent this
                # check if two nodes are the same -- if they are then crossing is impossible
                if ((i == j) or (i == j+1) or (i+1 == j)):
                    break
                
                v1 = df.loc[path[i]]
                v2 = df.loc[path[i+1]]
                v3 = df.loc[path[j]]
                v4 = df.loc[path[j+1]]
                
                #checks if edge v1-v2 and v3-v4 intersect in the line segments
                #if no intersection, break
                if (not intersection([v1.X,v1.Y],[v2.X,v2.Y],[v3.X,v3.Y],[v4.X,v4.Y])):
                   break
                
                #if j is 0 then swap v1 and v4
                if (j < i):
                    cross = True
                    tmp = path[i]
                    path[i] = path[j+1]
                    path[j+1] = tmp
                    
                #otherwise swap v2 and v3
                else:
                    print(path)
                    print(i,i+1,j,j+1,'cross')
                    print('swap',i+1,j)
                    cross = True
                    tmp = path[i+1]
                    path[i+1] = path[j]
                    path[j] = tmp
        
                
        path = path[1:len(path)-1]
        
        route = path
        return path
    
#first address represents depot
df = pd.DataFrame({'X':[5,1,8,4,2,9,7,6,6,0,7],'Y':[5,6,8,0,0,1,7,8,5,1,8]})

route = {}
for i in range(1,len(df)):
    route[i] = {'Path':[i],'Cost':0.0}
    
cost_mat = dist_mat(df)

init_costs(df, route, cost_mat)
#plot_route(df,route)
print('Original cost:',cost(route))

best_route, best_cost = anneal(df, route, cost_mat, 100, 500)
route_stat(best_route)

plot_route(df,best_route)

r = [1,2,3,4,5,6,7,8,9,10]
b = {}
b[1] = {'Path':r,'Cost':0.0}

plot_route(df,b)

a = two_opt(df,r)
b = {}
b[1] = {'Path':a,'Cost':0.0}

plot_route(df,b)

'''
fig = plt.figure()
ax = fig.add_subplot(111)
tmp = [depot] + sol1 + [depot]
tmp_x,tmp_y = get_cols(tmp)
line1, = ax.plot(tmp_x,tmp_y,'r-') 
plt.title('Total Cost:' + ("%.3f" % cost1))
print(sol1,'\n',cost1)
'''









