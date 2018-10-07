# -*- coding: utf-8 -*-
"""
MDVRP-multi depot vehicle routing problems
Created on Mon Oct  1 20:45:33 2018

@author: heast
"""

"""
Sources:
    1. USE PANDAS DATAFRAME TO STORE INFO
        https://stackoverflow.com/questions/29481485/creating-a-distance-matrix
    2. Weighted Thiessen Polygons
        https://gis.stackexchange.com/questions/17282/create-weighted-thiessen-polygons
    3. Geopandas tutorial
        https://gist.github.com/jorisvandenbossche/7b30ed43366a85af8626
    4. Geopandas mapping help
        http://geopandas.org/mapping.html
    5. Texas Statewide GIS information
        https://tnris.org/data-download/#!/statewide
    6. Plotting with Geopandas
        http://geopandas.org/gallery/plotting_with_geoplot.html#sphx-glr-gallery-plotting-with-geoplot-py
"""

#import libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import random
import math
import geopandas
from scipy.spatial import Voronoi, voronoi_plot_2d, distance_matrix
from random import randint
from shapely.geometry import Point

"""
TODO:
    1. For visualization: Plot each depot location as a different color and fill each zipcode 
        it is responsible for with that color
    2. Plot 1 but with Voronoi Polygon boundaries to see comparison
    3. Probably need to break code up into different files. No need to run GIS multiple times if testing 
        different deliveries
    4. Create excel file that has all depot locations with shp files and all zipcodes with shp files
        Add Rows for what Division Num each zip code bound belongs to and a separate
        column for plotting all bounds out of the same address (i.e. stafford has 6 Centers operating out of one location)
"""

"""
ISSUES:
    1. US Census data does not appear to have all zipcodes listed/attached to file (77001 is not in us_shp)
"""

"""
This block of code reads data from excel files and store it in Data Frames
"""
#read Air Commit Search Results and store in data frame
    #r infront of file path tells python to read string as path not name
xl_air=pd.ExcelFile(r"C:\Users\heast\Documents\Tamu\460\Coding\EAM_zip_Results.xlsx")
df_air = xl_air.parse(xl_air.sheet_names[1])

#creates list of all unique center numbers in df_air
    #these are the only ones we have zipcode locations/assignments for
cent = df_air.loc[:,'Center Num']
cent = cent.drop_duplicates()

#creates list of all unique zip_codes in df_air
zip_bound = df_air.loc[:,'Postal Code']
zip_bound = zip_bound.drop_duplicates()

#read Depot Locations and store in data frame
xl_depot = pd.ExcelFile(r"C:\Users\heast\Documents\Tamu\460\Coding\Building Address.xlsx")
df_depot_loc = xl_depot.parse(xl_depot.sheet_names[0])

#Get center numbers used from air commit and filter depot_loc to only include those
df_depot_loc = df_depot_loc.loc[df_depot_loc['Center Num'].isin(cent)]

#Converts lat/long to point for GIS
df_depot_loc['Coordinates']=list(zip(df_depot_loc.loc[:,'Facility Longitude'],df_depot_loc.loc[:,'Facility Latitude']))
df_depot_loc['Coordinates'] = df_depot_loc['Coordinates'].apply(Point)

#create GeoDataFrame with points created
gdf = geopandas.GeoDataFrame(df_depot_loc, geometry='Coordinates')

"""
End Block for reading data from excel files
"""

"""
This block loads GIS Data
"""
#TEXAS SHAPE FILE--not sure if it includes zip code boundaries
#tx_shp = geopandas.read_file(r"C:\Users\heast\Documents\Tamu\460\Coding\Texas GIS data\uscb10-blk\uscb10-precinct_texas.shp")
#tx_shp.plot(column='CNTY')

#US SHAPE FILE
us_shp = geopandas.read_file(r"C:\Users\heast\Documents\Tamu\460\Coding\US_GIS\cb_2017_us_zcta510_500k.shp")

#converts zipcodes from string to int--may not need temp variable to do this
temp = pd.DataFrame(data=us_shp,columns=['ZCTA5CE10'])
temp = temp.apply(pd.to_numeric)
us_shp.loc[:,'ZCTA5CE10'] = temp

#need to filter zipcodes to only plot those found in air commit
#us_shp = us_shp[(us_shp.ZCTA5CE10>=77000)&(us_shp.ZCTA5CE10<=77899)]
us_shp = us_shp.loc[us_shp['ZCTA5CE10'].isin(zip_bound)]
tmp = df_air.loc[df_air['Postal Code'].isin(us_shp.loc[:,'ZCTA5CE10'])]
tmp = tmp.drop_duplicates('Postal Code')
us_shp['center'] = list(0 for i in range(len(tmp)))
tmp['geometry'] = us_shp['geometry']

#probably filter using same method for depots from above


#column is the category for the chlorpleth map--try to set a category for which dist_center belongs
#to which zipcode
#filters df_air to be zipcodes we have access to in shape file
df_air = df_air.loc[df_air['Postal Code'].isin(us_shp.loc[:,'ZCTA5CE10'])]

#currently iterating through all of tmp and us_shp
#100% positive this is inefficient and there is a better way to do this
for index,row in us_shp.iterrows():
    for Index,Row in tmp.iterrows():
        if (row['ZCTA5CE10']==Row['Postal Code']):
            us_shp.at[index,'center'] = tmp.at[Index,'Center Num']
            tmp.at[Index,'geometry'] = us_shp.at[index,'geometry']
            break

test = geopandas.GeoDataFrame(tmp, geometry='geometry')
     
#plots a choropleth map of delivery boundaries and adds dist. centers
base = us_shp.plot(column='center', cmap = 'magma')
gdf.plot(ax=base,color='red')
base.set_title('Distribution center zip code boundaries')
base.set_xlabel('Latitude')
base.set_ylabel('Longitude')
vor = Voronoi(np.array([[29.1504,-95.4299],[29.8064,-94.9745],[30.0557,-94.1311],[25.9085,-97.4438],[30.6793,-96.3495],[30.3545,-95.4268],[29.6395,-95.2895],[29.7593,-95.3655],[29.6005,-95.1687],[29.6759,-95.3211],[29.9398,-93.8868],[29.6194,-95.5557],[29.3585,-94.9471],[28.7692,-96.9791]]))
fig = voronoi_plot_2d(vor)

test.plot(column = 'Center Num', cmap = 'tab20')

##trying to plot each individual delivery zone
for index,row in df_depot_loc.iterrows():
    #tmp_ax = plt.figure()
    tmp_ax = us_shp[us_shp['center'] == row['Center Num']].plot()
    string = "delivery zone for Center Num: " + str(row['Center Num'])
    tmp_ax.set_title(string)
    gdf[gdf['Center Num'] == row['Center Num']].plot(ax = tmp_ax,color='red')

    
"""
End loading of GIS data
"""
"""
This block generates fake addresses and depots for testing
"""
#number of addresses to generate
size = 50
#large fake number to initialize depot distance
large_distance = 100000

#X = np.random.rand(size,2)*10
dat = {'xcord':(np.random.rand(size,1)*10).flatten(), 'ycord':(np.random.rand(size,1)*10).flatten(), 'depot_id':[0]*size,'depot_x':[0]*size,'depot_y':[0]*size,'depot_dist':[large_distance]*size}

#create dataframe to store x,y coordinates and other info
#df = pd.DataFrame(X,columns = ['xcord','ycord'], index = range(len(X)))
df = pd.DataFrame(data=dat)

#fixed dummy depot locations
Y = np.array([[2,2],[2,8],[8,2],[8,8],[5,5]])

"""
End Block for creating fake customers/depots
"""

"""
This block calculates distance between each pair of customer
and distance from customer to depot
Currently all distances are Euclidian---should use GIS to gain obstructed distance
"""
#create distance matrix of euclidian distance between each customer
dist = pd.DataFrame(distance_matrix(df[['xcord','ycord']], df[['xcord','ycord']]), index=df.index, columns=df.index)

#min distance to depot
for i in range(len(df)):
    for j in range(len(Y)):
        d = pow(pow(df.loc[i,'xcord']-Y[j,0],2)+pow(df.loc[i,'ycord']-Y[j,1],2),.5)
        if (d < df.loc[i,'depot_dist']):
            df.loc[i,'depot_id'] = j
            df.loc[i,'depot_x'] = Y[j,0]
            df.loc[i,'depot_y'] = Y[j,1]
            df.loc[i,'depot_dist'] = d

"""
End Block of distance calculations
"""

"""
This block deals with plotting locations
creates Thiessen/Voronoi Polygons for each depot location
Plots Voronoi polygons and depot/customer locations
Voronoi polygons are unweighted euclidian distance--try to plot weighted/obstructed distances
"""


vor = Voronoi(Y)
fig = voronoi_plot_2d(vor)
plt.axis([-1,11,-1,11])
ax1 = fig.add_subplot(111)

#for i in range(len(d_i)):
    #plots line connecting address to nearest center
 #   ax1.plot((x[i],x_d[d_i[i]]), (y[i],y_d[d_i[i]]), 'ro-')

ax1.scatter(df.loc[:,'xcord'],df.loc[:,'ycord'])
ax1.scatter(Y[:,0],Y[:,1], c='r')

"""
End Plotting block
"""