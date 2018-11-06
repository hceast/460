#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 26 13:14:02 2018

@author: igmcnelis
"""

import pandas as pd
import numpy as np
from GetCoords import get_coords
from haversine import haversine

facilities = pd.read_excel("Building Address.xlsx")
facilities = facilities.loc[[13,19,7], :]
#facilities = facilities.loc[[13,19,7],["Facility Address Line 1","Facility City Name","Facility Postal Code", "Latitude", "Longitude"]]
center_capacity = [999999999, 999999999, 999999999]
se = pd.Series(center_capacity)
facilities["Deliv Center Capac"] = se.values 
facilities = facilities[["Facility Name", "Center Name", "Center Num", "Facility Address Line 1", "Facility City Name", "Facility City Name", "Facility Postal Code", "Deliv Center Capac"]].copy()

myk_address = str(facilities.loc[13, "Facility Address Line 1"]) + ", " + facilities.loc[13, "Facility City Name"] + ", " + "TX" + " " + str(facilities.loc[13, "Facility Postal Code"])
myk_coords = get_coords(myk_address)
staff_address = str(facilities.loc[19, "Facility Address Line 1"]) + ", " + facilities.loc[19, "Facility City Name"] + ", " + "TX" + " " + str(facilities.loc[19, "Facility Postal Code"])
staff_coords = get_coords(staff_address)
sweet_address = str(facilities.loc[7, "Facility Address Line 1"]) + ", " + facilities.loc[7, "Facility City Name"] + ", " + "TX" + " " + str(facilities.loc[7, "Facility Postal Code"])
sweet_coords = get_coords(sweet_address)

Lat = [myk_coords[1], staff_coords[1], sweet_coords[1]]
Long = [myk_coords[0], staff_coords[0], sweet_coords[0]]

facilities["Latitude"] = Lat
facilities["Longitude"] = Long

#%%
deliv_517 = pd.concat([pd.read_excel("EAM_Deliveries.xlsx", sheet_name = "Mykawa_517"), pd.read_excel("EAM_Deliveries.xlsx", sheet_name = "Stafford_517"), pd.read_excel("EAM_Deliveries.xlsx", sheet_name = "Sweetwater_517")], ignore_index = True) 

Addresses = []
Long = []
Lat = []
Deliv_Vols = []

i = 0
address = ""
for i in range(len(deliv_517)):
    address = str(deliv_517.loc[i, "Street Num"]) + " " + deliv_517.loc[i, "Street Name"] + " " + deliv_517.loc[i, "City Name"] + ", " + "TX" + ", " + str(deliv_517.loc[i, "Postal Code"])
    Addresses.append(address) 
    
    coords = get_coords(address)
    Long.append(coords[0])
    Lat.append(coords[1])
    
    Deliv_Vols.append( deliv_517.loc[i, "Deliv Packages Qty"] )

deliv_517 = pd.DataFrame()
deliv_517["Delivery Address"] = Addresses
deliv_517["Delivery Volume"] = Deliv_Vols
deliv_517["Longitude"] = Long
deliv_517["Latitude"] = Lat

#%%
#Distance Matrix
D_Mat = np.zeros((len(deliv_517), len(deliv_517))) 

i = 0
for i in range(len(deliv_517)):
    coords1 = (deliv_517["Longitude"][i], deliv_517["Latitude"][i])
    
    j = 0
    for j in range(len(deliv_517)):
        coords2 = (deliv_517["Longitude"][j], deliv_517["Latitude"][j])
        D_Mat[i][j] = haversine(coords1, coords2)
        
Dist_Mat = pd.DataFrame(D_Mat)

writer = pd.ExcelWriter("May_17_Distances.xlsx", engine='xlsxwriter')
Dist_Mat.to_excel(writer, sheet_name = "Distance Matrix")
writer.save()

#%%

writer = pd.ExcelWriter("May_17_Delivery_Data.xlsx", engine='xlsxwriter')
facilities.to_excel(writer, sheet_name = "Centers")
deliv_517.to_excel(writer, sheet_name = "Delivery Data")
writer.save()

#%%
deliv_524 = pd.concat([pd.read_excel("EAM_Deliveries.xlsx", sheet_name = "Mykawa_524"), pd.read_excel("EAM_Deliveries.xlsx", sheet_name = "Stafford_524"), pd.read_excel("EAM_Deliveries.xlsx", sheet_name = "Sweetwater_524")], ignore_index = True)

Addresses = []
Long = []
Lat = []
Deliv_Vols = []

i = 0
address = ""
for i in range(len(deliv_524)):
    address = str(deliv_524.loc[i, "Street Num"]) + " " + deliv_524.loc[i, "Street Name"] + " " + deliv_524.loc[i, "City Name"] + ", " + "TX" + ", " + str(deliv_524.loc[i, "Postal Code"])
    Addresses.append(address) 
    
    coords = get_coords(address)
    Long.append(coords[0])
    Lat.append(coords[1])
    
    Deliv_Vols.append( deliv_524.loc[i, "Deliv Packages Qty"] )

deliv_524 = pd.DataFrame()
deliv_524["Delivery Address"] = Addresses
deliv_524["Delivery Volume"] = Deliv_Vols
deliv_524["Longitude"] = Long
deliv_524["Latitude"] = Lat

#%%
#Distance Matrix
D_Mat = np.zeros((len(deliv_524), len(deliv_524))) 

i = 0
for i in range(len(deliv_524)):
    coords1 = (deliv_524["Longitude"][i], deliv_524["Latitude"][i])
    
    j = 0
    for j in range(len(deliv_524)):
        coords2 = (deliv_524["Longitude"][j], deliv_524["Latitude"][j])
        D_Mat[i][j] = haversine(coords1, coords2)
        
Dist_Mat = pd.DataFrame(D_Mat)

writer = pd.ExcelWriter("May_24_Distances.xlsx", engine='xlsxwriter')
Dist_Mat.to_excel(writer, sheet_name = "Distance Matrix")
writer.save()

#%%

writer = pd.ExcelWriter("May_24_Delivery_Data.xlsx", engine='xlsxwriter')
facilities.to_excel(writer, sheet_name = "Centers")
deliv_524.to_excel(writer, sheet_name = "Delivery Data")
writer.save()

#%%
"""
import pandas as pd

deliv_517 = pd.concat([pd.read_excel("EAM_Deliveries.xlsx", sheet_name = "Mykawa_517"), pd.read_excel("EAM_Deliveries.xlsx", sheet_name = "Stafford_517"), pd.read_excel("EAM_Deliveries.xlsx", sheet_name = "Sweetwater_517")], ignore_index = True)
deliv_517 = deliv_517[["Postal Code", "Facility Loc Num", "Deliv Packages Qty"]].copy()

zip_codes = []

i = 0
for i in range(len(deliv_517)):
    if (deliv_517["Postal Code"][i] not in zip_codes):
        zip_codes.append(deliv_517["Postal Code"][i])

Zip_Vols = []
Assoc_Fac = []        

i = 0
for i in range(len(zip_codes)):
    pkg_vol = 0
    
    j = 0
    for j in range(len(deliv_517)):
        if(deliv_517["Postal Code"][j] == zip_codes[i]):
            pkg_vol += deliv_517["Deliv Packages Qty"][j]
            
    j = 0
    for j in range(len(deliv_517)):
        if(deliv_517["Postal Code"][j] == zip_codes[i]):
            Assoc_Fac.append(deliv_517["Facility Loc Num"][j])
            break
    
    Zip_Vols.append(pkg_vol)
    
zip_517 = pd.DataFrame()
zip_517["Zip Code"] = zip_codes
zip_517["Zip Delivery Volume"] = Zip_Vols
zip_517["Assigned Facility"] = Assoc_Fac

#%%

writer = pd.ExcelWriter("May_17_Zip_Data.xlsx", engine='xlsxwriter')
zip_517.to_excel(writer, sheet_name = "Zip Data")
writer.save()

#%%
import pandas as pd

deliv_524 = pd.concat([pd.read_excel("EAM_Deliveries.xlsx", sheet_name = "Mykawa_524"), pd.read_excel("EAM_Deliveries.xlsx", sheet_name = "Stafford_524"), pd.read_excel("EAM_Deliveries.xlsx", sheet_name = "Sweetwater_524")], ignore_index = True)
deliv_524 = deliv_524[["Postal Code", "Facility Loc Num", "Deliv Packages Qty"]].copy()

zip_codes = []

i = 0
for i in range(len(deliv_524)):
    if (deliv_524["Postal Code"][i] not in zip_codes):
        zip_codes.append(deliv_524["Postal Code"][i])

Zip_Vols = []
Assoc_Fac = []        

i = 0
for i in range(len(zip_codes)):
    pkg_vol = 0
    
    j = 0
    for j in range(len(deliv_524)):
        if(deliv_524["Postal Code"][j] == zip_codes[i]):
            pkg_vol += deliv_524["Deliv Packages Qty"][j]
            
    j = 0
    for j in range(len(deliv_524)):
        if(deliv_524["Postal Code"][j] == zip_codes[i]):
            Assoc_Fac.append(deliv_524["Facility Loc Num"][j])
            break
    
    Zip_Vols.append(pkg_vol)
    
zip_524 = pd.DataFrame()
zip_524["Zip Code"] = zip_codes
zip_524["Zip Delivery Volume"] = Zip_Vols
zip_524["Assigned Facility"] = Assoc_Fac

#%%

writer = pd.ExcelWriter("May_24_Zip_Data.xlsx", engine='xlsxwriter')
zip_524.to_excel(writer, sheet_name = "Zip Data")
writer.save()
"""