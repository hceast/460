# -*- coding: utf-8 -*-
"""
Created on Wed Oct 24 19:48:21 2018

@author: heast
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from clarke_wright import clarke_wright, format_dat, haversine
import time
from scipy.spatial import Delaunay, Voronoi, voronoi_plot_2d
from collections import defaultdict
from read_customers import get_df
import itertools
from plotting import cw_plot, delaunay_plot
from get_adjacent import get_adjacent, adj_set
from sklearn.cluster import KMeans
from arcgis.gis import GIS
import arcgis.network as network
import arcgis.features as features
import arcgis.features.use_proximity as use_proximity
import arcgis.features.find_locations as find_locations

dist, my_517, my_524, staf_517, staf_524, swee_517, swee_524 = get_df()

all_517 = pd.read_excel(r'C:\Users\heast\Documents\Tamu\460\Coding\new_EAM_Data.xlsx', sheet_name = 'All 5-17')
all_524 = pd.read_excel(r'C:\Users\heast\Documents\Tamu\460\Coding\new_EAM_Data.xlsx', sheet_name = 'All 5-24')

'''
#plot original 
ax = my_517.plot.scatter(x='Longitude', y='Latitude', color='Blue', label='Mykawa', title = 'Current Zoning');
staf_517.plot.scatter(x='Longitude', y='Latitude', color='Green', label='Stafford', ax=ax);
swee_517.plot.scatter(x='Longitude', y='Latitude', color='Red', label='Sweetwater', ax=ax);

#################################################     K-Means Clustering
#generates 3 clusters of customer locations
X = all_517.loc[:,['Longitude','Latitude']].values
kmeans = KMeans(n_clusters=3,random_state=0).fit(X)
kmeans.labels_

#adds assigned cluster to dataframe
all_517['K_means'] = kmeans.labels_

cluster_1 = all_517[all_517['K_means'] == 0]
cluster_2 = all_517[all_517['K_means'] == 1]
cluster_3 = all_517[all_517['K_means'] == 2]

#plot K_means assignment
ax_cluster = cluster_1.plot.scatter(x='Longitude', y='Latitude', color='Green', label='Cluster 1', title = 'Zoning based on K means Clustering');
cluster_2.plot.scatter(x='Longitude', y='Latitude', color='Red', label='Cluster 2', ax=ax_cluster);
cluster_3.plot.scatter(x='Longitude', y='Latitude', color='Blue', label='Cluster 3', ax=ax_cluster);





################################      Nearest Euclidian distance to Depot
all_517['Nearest_Euclidean'] = [3 for i in range(len(all_517))]

for index,row in all_517.iterrows():
    tmp_dist = 9999999999999
    
    for index2,row2 in dist.iterrows():
        if (haversine(row['Longitude'], row['Latitude'], row2['Longitude'], row2['Latitude']) < tmp_dist):
            tmp_dist = haversine(row['Longitude'], row['Latitude'], row2['Longitude'], row2['Latitude'])
            all_517.at[index,'Nearest_Euclidean'] = index2

euc1 = all_517[all_517['Nearest_Euclidean'] == 0]
euc2 = all_517[all_517['Nearest_Euclidean'] == 1]
euc3 = all_517[all_517['Nearest_Euclidean'] == 2]

ax_euc = euc1.plot.scatter(x='Longitude', y='Latitude', color='Blue', label='Mykawa', title = 'Zoning Based on Nearest Euclidian Distance Depot');
euc2.plot.scatter(x='Longitude', y='Latitude', color='Green', label='Stafford', ax=ax_euc);
euc3.plot.scatter(x='Longitude', y='Latitude', color='Red', label='Sweetwater', ax=ax_euc);







###########################     Nearest Manhattan distance to Depot
#abs(x1-x2) + abs(y1-y2) 
#Used sometimes in mapping due to fact that vehicles can travel through buildings 

def manhattan(x1,y1,x2,y2):
    return (abs(x1-x2) + abs(y1-y2))

all_517['Nearest_Manhattan'] = [3 for i in range(len(all_517))]

for index,row in all_517.iterrows():
    tmp_dist = 9999999999999
    
    for index2,row2 in dist.iterrows():
        if (manhattan(row['Longitude'], row['Latitude'], row2['Longitude'], row2['Latitude']) < tmp_dist):
            tmp_dist = manhattan(row['Longitude'], row['Latitude'], row2['Longitude'], row2['Latitude'])
            all_517.at[index,'Nearest_Manhattan'] = index2

man1 = all_517[all_517['Nearest_Manhattan'] == 0]
man2 = all_517[all_517['Nearest_Manhattan'] == 1]
man3 = all_517[all_517['Nearest_Manhattan'] == 2]

ax_man = man1.plot.scatter(x='Longitude', y='Latitude', color='Blue', label='Mykawa', title = 'Zoning Based on Nearest Manhattan Distance Depot');
man2.plot.scatter(x='Longitude', y='Latitude', color='Green', label='Stafford', ax=ax_man);
man3.plot.scatter(x='Longitude', y='Latitude', color='Red', label='Sweetwater', ax=ax_man);
'''

'''
#Nearest geographical distance to depot
#Get gis from arcgis
user_name = ''
password = ''
gis = GIS('https://tamu.maps.arcgis.com', user_name, password)

#download created features using thier id
all_pack_517_features = gis.content.get('6dd8f30e2aa34694bd3354a1b41f2f0e')
dist_features = gis.content.get('fcb253f412ad44bb81a499ed166870e1')

route_service = network.RouteLayer(gis.properties.helperServices.route.url, gis=gis)
print(sorted([i['name'] for i in route_service.retrieve_travel_modes()['supportedTravelModes']]))

car_mode = [i for i in route_service.retrieve_travel_modes()['supportedTravelModes'] if i['name'] == 'Driving Time'][0]
result = use_proximity.find_nearest(all_pack_517_features, dist_features, measurement_type=car_mode,
                                    context={'outSR': {"wkid": 4326}})

df = pd.DataFrame.from_records([i['attributes'] for i in 
                                result['connecting_lines_layer'].layer.featureSet.features])
df[['RouteName', 'Total_Kilometers', 'Total_Minutes']]

writer = pd.ExcelWriter('EAM Time Distance.xlsx')
df.to_excel(writer,'Sheet1')
writer.save()
'''

#Nearest travel time depot
#Balanced and Connected Cluster
#Fair Cake Cutting

#For Each zoning method perform routing analysis
#Clarke-Wright
#ArcGis routing -- probably similar to what is being used
#Simulated Annealing
#Minimum Spanning Tree?
#Genetic?

#Test zoning with additional depots
    #adding new depot
    #Shipping from existing