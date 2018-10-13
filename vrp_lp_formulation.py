# -*- coding: utf-8 -*-
"""
Created on Tue Oct  9 17:33:23 2018

@author: heast
"""

#from pulp import *
import pulp
import matplotlib.pyplot as plt
import time

'''
Using model formulation from:
    A generalized formulation for vehicle routing problems
        Pedro Munari, Twan Dollevoet, Remy Spliet
'''
start_clock = time.time()

#num drivers assigned to single depot
K = 4

#max capacity of each vehicle--assume same for each vehicle for now
Q = 15

#first and last points of locations represent depot
    #x,y coordinates of all customers
locations = \
                [(4, 4), # depot
                 (2, 8), (8, 8), # row 0
                 (0, 7), (1, 7),
                 (5, 6), (7, 6),
                 (3, 5), (6, 5),
                 (5, 3), (8, 3),
                 (1, 2), (2, 2),
                 (3, 1), (6, 1),
                 (0, 0), (7, 0),
                 (4, 4)] # depot
                
#demands of all customers
    #depot has demand 0
demands = \
            [0, # depot
             1, 1, # 1, 2
             2, 4, # 3, 4
             2, 4, # 5, 6
             8, 8, # 7, 8
             1, 2, # 9,10
             1, 2, # 11,12
             4, 4, # 13, 14
             8, 8, # 15, 16
             0] # depot
    
#used for creating model with pulp
cols = [i for i in range(len(locations))]
rows = cols

#calculate c_ij
c = []

print("Calculating distance matrix: ", time.time()-start_clock)
for i in range(len(locations)):
    c += [[pow(pow(locations[i][0] - locations[j][0],2) + pow(locations[i][1] - locations[j][1],2),.5) for j in range(len(locations))]]

print("Creating problem variables", time.time()-start_clock)
#Problem Variable to contain problem
prob = pulp.LpProblem("Vehicle Routing Problem", pulp.LpMinimize)

#Problem Variables created
#xij is binary 1 if route from customer i to j
x = pulp.LpVariable.dicts("X", (rows,cols),0,1,pulp.LpInteger)

#continuous decision variable corresponding to cumulated
    #demand on the route 
    #not sure how to use yet
y = pulp.LpVariable.dicts("Y", cols,0,Q, pulp.LpInteger)
    
#Objective function - minimize sum of euclidian distance travelled
prob += pulp.lpSum(pulp.lpSum(x[i][j] * c[i][j] for j in cols) for i in cols),"Min distance"
    
#2.2 all customers visited exactly once
for i in range(1,len(locations)-1):
    
    #need to sum all x_ij where i != j
        #not sure how to do that without adding second loop
    x_ij = []
    for j in range(1,len(locations)):
        if i != j:
            x_ij += [x[i][j]]
    prob += pulp.lpSum(x_ij) == 1,""

#2.3 correct flow of vehicles through the arcs
    #if vehicle arrives at node, it must leave node
for h in range(1, len(locations)-1):
    x_ih = []
    x_hj = []
    
    for i in range(0, len(locations) - 1):
        if i != h:
            x_ih += [x[i][h]]
    for j in range(1, len(locations)):
        if j != h:
            x_hj += [x[h][j]]
    
    prob += (pulp.lpSum(x_ih) - pulp.lpSum(x_hj)) == 0,""

    #prob += (pulp.lpSum([x[i][h] for i in range(0,len(locations)-1) if i != h]) - (pulp.lpSum([x[h][j] for j in range(1,len(locations)) if j != h])))

#2.4 limits maximum routes to K vehicles
prob += pulp.lpSum([x[0][j] for j in range(1, len(locations) - 1)]) <= K,""

#2.5 ensures vehicle capacity not exceeded
for i in range(len(locations)):
    for j in range(len(locations)):
        prob += y[j] >= y[i] + (demands[j] * x[i][j]) - (Q * (1 - x[i][j])),""
        #prob += y[j] >= y[i] + demands[j] * x[i][j],""

#2.6 ensures vehicle capacity not exceeded
#for i in range(len(locations)):
    #prob += demands[i] <= y[i] <= Q,""
    #prob += y[i] >= demands[i],""

print("Begin solver: ", time.time()-start_clock)
# The problem is solved using PuLP's choice of Solver
prob.solve()
    
# The status of the solution is printed to the screen
print("Status:", pulp.LpStatus[prob.status])
print("Time elapsed (s): ", time.time() - start_clock)  
print("Time elapsed (min): ",(time.time() - start_clock)/60)           

#print routes generated
fig = plt.figure()
ax = fig.add_subplot(111)

ax.scatter([i[0] for i in locations],[j[1] for j in locations])

for i in range(0,len(locations)):
    for j in range(0, len(locations)):
        if pulp.value(x[i][j]) == 1:
            print(i, " - ", j)
            ax.plot((locations[i][0], locations[j][0]), (locations[i][1], locations[j][1]), 'ro-')

'''
stuff happening wrong between 10 and 2
'''
for i in range(len(locations)):
    print(i,": ",pulp.value(y[i]))