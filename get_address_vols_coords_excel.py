#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 26 13:14:02 2018

@author: igmcnelis
"""

import pandas as pd
from GetCoords import get_coords

facilities = pd.read_excel("Building_Address.xlsx")
facilities = facilities.loc[[13,19,7],["Facility Name","Latitude","Longitude"]]
center_capacity = [999999999, 999999999, 999999999]
se = pd.Series(center_capacity)
facilities["Deliv Center Capac"] = se.values 
#facilities = pd.DataFrame(data = facilities.values, index = [i for i in range(len(facilities))], columns = ['Facility','Latitude','Longitude'])

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
"""
writer = pd.ExcelWriter("May_17_Delivery_Data.xlsx", engine='xlsxwriter')
facilities.to_excel(writer, sheet_name = "Centers")
deliv_517.to_excel(writer, sheet_name = "Delivery Data")
writer.save()
"""
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
"""
writer = pd.ExcelWriter("May_24_Delivery_Data.xlsx", engine='xlsxwriter')
facilities.to_excel(writer, sheet_name = "Centers")
deliv_524.to_excel(writer, sheet_name = "Delivery Data")
writer.save()
"""
#%%
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
