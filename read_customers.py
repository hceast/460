# -*- coding: utf-8 -*-
"""
Created on Wed Oct 17 10:13:54 2018

@author: heast
"""

import pandas as pd
import arcgis
from arcgis.gis import GIS
from arcgis.geocoding import Geocoder, get_geocoders
from arcgis.geocoding import geocode

'''
This reads the customer data for the Mykawa, Sweetwater, and Stafford Centers into a dataframe

creates separate data frame for each day for each distribution center

Days used are 5/17 and 5/24
6 dataframes created

'''

############## Enter info to gis 
# gis = GIS("portal url", "username", "password")
# gis = GIS("https://tamu.maps.arcgis.com", "username", "password")

#Combines addresses into on cell assuming it is given in a dataframe and the information
# is contained in columns called 'Street Num', 'Street Name', and 'City Name'
def combine_address(p):
    address = []
    for i,row in p.iterrows():
        address += [p.loc[i,'Street Num'] + ' ' +  p.loc[i,'Street Name'] + ' ' + p.loc[i,'City Name'] + ' Texas, ' + p.loc[i,'Postal Code']]
    return address

#converts address into latitude and longitude
def lat_long(p):
    long = []
    lat = []
    for index, row in p.iterrows():
        long += [geocode(p.loc[index,'Address'])[0]['location']['x']]
        lat += [geocode(p.loc[index,'Address'])[0]['location']['y']]
    
    return long,lat

def format_data():
    ################ Distribution Center addresses
    dist_center = pd.read_excel(r'C:\Users\heast\Documents\Tamu\460\Coding\Building Address.xlsx', sheet_name = 'Untitled Analysis')
    dist_center = dist_center.loc[[13,19,7],['Facility Name','Facility Latitude','Facility Longitude']]
    dist_center = pd.DataFrame(data = dist_center.values, index = [i for i in range(len(dist_center))], columns = ['Facility','Latitude','Longitude'])
    
    ##################################################################################################
        
    ################  MYKAWA CENTER
    mykawa_deliv = pd.read_excel(r'C:\Users\heast\Documents\Tamu\460\Coding\Questions.xlsx', sheet_name = '7723-Mykawa')
    
    mykawa_deliv_517 = mykawa_deliv.loc[:207,:'Unnamed: 10']
    mykawa_deliv_524 = mykawa_deliv.loc[:247,'EAM 5/24/2018':'Unnamed: 22']
    
    #headers to go on dataframe when formatted properly -- same header for all centers
    column_names = mykawa_deliv_517.loc[0]
    
    mykawa_deliv_517 = pd.DataFrame(data = mykawa_deliv_517.loc[1:].values, index = [i for i in range(0,len(mykawa_deliv_517)-1)], columns = column_names)
    mykawa_deliv_524 = pd.DataFrame(data = mykawa_deliv_524.loc[1:].values, index = [i for i in range(0,len(mykawa_deliv_524)-1)], columns = column_names)
    
    ##### Combine addresses to one column (Address)
    mykawa_deliv_517['Address'] = combine_address(mykawa_deliv_517)
    mykawa_deliv_524['Address'] = combine_address(mykawa_deliv_524)
    ##################################################################################################
    
    
    ############### STAFFORD CENTER
    stafford_deliv = pd.read_excel(r'C:\Users\heast\Documents\Tamu\460\Coding\Questions.xlsx', sheet_name = '7744-Stafford')
    
    stafford_deliv_517 = stafford_deliv.loc[:,:'Unnamed: 10']
    stafford_deliv_524 = stafford_deliv.loc[:69,'EAM.1':'Unnamed: 22']
    
    stafford_deliv_517 = pd.DataFrame(data = stafford_deliv_517.loc[1:].values, index = [i for i in range(0,len(stafford_deliv_517)-1)], columns = column_names)
    stafford_deliv_524 = pd.DataFrame(data = stafford_deliv_524.loc[1:].values, index = [i for i in range(0,len(stafford_deliv_524)-1)], columns = column_names)
    
    ##### Combine addresses to one column (Address)
    stafford_deliv_517['Address'] = combine_address(stafford_deliv_517)
    stafford_deliv_524['Address'] = combine_address(stafford_deliv_524)
    ###################################################################################################
    
    
    ############### SWEETWATER CENTER
    sweetwater_deliv = pd.read_excel(r'C:\Users\heast\Documents\Tamu\460\Coding\Questions.xlsx', sheet_name = '7716-Sweetwater')
    
    sweetwater_deliv_517 = sweetwater_deliv.loc[:,:'Unnamed: 10']
    sweetwater_deliv_524 = sweetwater_deliv.loc[:139,'EAM.1':'Unnamed: 22']
    
    sweetwater_deliv_517 = pd.DataFrame(data = sweetwater_deliv_517.loc[1:].values, index = [i for i in range(0,len(sweetwater_deliv_517)-1)], columns = column_names)
    sweetwater_deliv_524 = pd.DataFrame(data = sweetwater_deliv_524.loc[1:].values, index = [i for i in range(0,len(sweetwater_deliv_524)-1)], columns = column_names)
    
    ##### Combine addresses to one column (Address)
    sweetwater_deliv_517['Address'] = combine_address(sweetwater_deliv_517)
    sweetwater_deliv_524['Address'] = combine_address(sweetwater_deliv_524)
    ##################################################################################################

###### reads excel file of all data that was created above
def get_df():
    dist_center = pd.read_excel(r'C:\Users\heast\Documents\Tamu\460\Coding\new_EAM_Data.xlsx', sheet_name = 'Centers')
    mykawa_deliv_517 = pd.read_excel(r'C:\Users\heast\Documents\Tamu\460\Coding\new_EAM_Data.xlsx', sheet_name = 'Mykawa 5-17')
    mykawa_deliv_524 = pd.read_excel(r'C:\Users\heast\Documents\Tamu\460\Coding\new_EAM_Data.xlsx', sheet_name = 'Mykawa 5-24')
    stafford_deliv_517 = pd.read_excel(r'C:\Users\heast\Documents\Tamu\460\Coding\new_EAM_Data.xlsx', sheet_name = 'Stafford 5-17')
    stafford_deliv_524 = pd.read_excel(r'C:\Users\heast\Documents\Tamu\460\Coding\new_EAM_Data.xlsx', sheet_name = 'Stafford 5-24')
    sweetwater_deliv_517 = pd.read_excel(r'C:\Users\heast\Documents\Tamu\460\Coding\new_EAM_Data.xlsx', sheet_name = 'Sweetwater 5-17')
    sweetwater_deliv_524 = pd.read_excel(r'C:\Users\heast\Documents\Tamu\460\Coding\new_EAM_Data.xlsx', sheet_name = 'Sweetwater 5-24')
    
    return dist_center, mykawa_deliv_517, mykawa_deliv_524, stafford_deliv_517, stafford_deliv_524, sweetwater_deliv_517, sweetwater_deliv_524

def add_lat_long():
    ########### Get lat/long from arcgis
    long,lat = lat_long(mykawa_deliv_517)
    mykawa_deliv_517['Longitude'] = long
    mykawa_deliv_517['Latitude'] = lat
    
    long,lat = lat_long(mykawa_deliv_524)
    mykawa_deliv_524['Longitude'] = long
    mykawa_deliv_524['Latitude'] = lat
    
    long,lat = lat_long(stafford_deliv_517)
    stafford_deliv_517['Longitude'] = long
    stafford_deliv_517['Latitude'] = lat
    
    long,lat = lat_long(stafford_deliv_524)
    stafford_deliv_524['Longitude'] = long
    stafford_deliv_524['Latitude'] = lat
    
    long,lat = lat_long(sweetwater_deliv_517)
    sweetwater_deliv_517['Longitude'] = long
    sweetwater_deliv_517['Latitude'] = lat
    
    long,lat = lat_long(sweetwater_deliv_524)
    sweetwater_deliv_524['Longitude'] = long
    sweetwater_deliv_524['Latitude'] = lat
    
    
    ####### Write data to Excel file
    writer = pd.ExcelWriter(r'C:\Users\heast\Documents\Tamu\460\Coding\new_EAM_Data.xlsx', engine='xlsxwriter')
    
    dist_center.to_excel(writer, sheet_name='Centers')
    
    mykawa_deliv_517.to_excel(writer, sheet_name='Mykawa 5-17')
    mykawa_deliv_524.to_excel(writer, sheet_name='Mykawa 5-24')
    
    stafford_deliv_517.to_excel(writer, sheet_name='Stafford 5-17')
    stafford_deliv_524.to_excel(writer, sheet_name='Stafford 5-24')
    
    sweetwater_deliv_517.to_excel(writer, sheet_name='Sweetwater 5-17')
    sweetwater_deliv_524.to_excel(writer, sheet_name='Sweetwater 5-24')
    
    writer.save()
