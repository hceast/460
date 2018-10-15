#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 13 15:52:33 2018

@author: igmcnelis
"""

import pulp
import time
import pandas as pd
import numpy as np
from haversine import haversine

#Read in data
Coords = pd.read_csv("Coords_517.txt", sep = ",", header = None)
Deliv_Vols = pd.read_csv("DelivVols_517.txt", sep = "\n", header = None)


#Create lists for individual delivery quantities (q), Create Node Set N and Edge Set E
#Delivery quantites
q = Deliv_Vols.loc[0:208, 0]
#Truck Capacity
Q = 50

#Num of Trucks
V = 20

#Node Set N
N = []
i = 0
while i < 208:
    N.append((Coords.loc[i, 0], Coords.loc[i, 1]))
    i += 1

N.append(N[0])

#Create Distance matrix, which is the set of all edges e_ij, or E
E = np.zeros(shape = (len(N), len(N)))
i = 0
j = 0

for i in range(len(N)):
    for j in range(len(N)):
        E[i][j] = haversine(N[i][0], N[i][1], N[j][0], N[j][1])
        

#Nodes and Trucks for LP
Trucks = [i for i in range(1, V+1)]
Node1 = [i for i in range(len(N)-1)]
Node2 = [i for i in range(1, len(N))]


#Create Problem
prob = pulp.LpProblem("Vehicle Routing Problem", pulp.LpMinimize)

#Create Decision Variable
#I_ijk is binary 1 if truck k goes from customer i to j
I = pulp.LpVariable.dicts("I_kij", (Trucks, Node1, Node2), 0, 1, pulp.LpInteger)

#Objective function - minimize cumulative euclidian distance over all routes K
prob += pulp.lpSum(pulp.lpSum(pulp.lpSum(E[i][j] * I[k][i][j] for j in Node2) for i in Node1) for k in Trucks),"Minimize Distance"

#Constraint 1
for j in Node2:
    prob += pulp.lpSum(pulp.lpSum(I[k][i][j] for i in Node1) for k in Trucks) == 1,""

#Constraint 2
for k in Trucks:
    
    for n in range(0, len(N)):
        for i in range(0, len(N)-1):
            if i != n:
                j = n

        for j in range(1, len(N)):
            if j != n:
                i = n
       
        prob += (pulp.lpSum(I[k][i][j]) - pulp.lpSum(I[k][i][j])) == 0,""
        
#Constraint 3
for k in Trucks:
     prob += pulp.lpSum(pulp.lpSum(I[k][i][j] for i in Node1[0]) for j in Node2) <= 1,""

#Constraint 4
for k in Trucks:
    for j in Node2:
        for i in Node1:
            prob += pulp.lpSum(q[j]*I[k][i][j] for j in range(1, j)) >= pulp.lpSum(q[i]*I[k][i][j] for i in range(0, i)) + (q[j]*I[k][i][j]) -  (Q*(1-I[k][i][j]))

