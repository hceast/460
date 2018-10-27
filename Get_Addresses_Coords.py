#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 14:29:32 2018

@author: igmcnelis
"""

import pandas as pd

#Read in the re-formatted Excel file
xlsx1 = pd.ExcelFile("EAM_Delivery_Data_517.xlsx")
#Construct a DataFrame for each sheet
mykawa = xlsx1.parse(0)
stafford = xlsx1.parse(1)
sweetwater = xlsx1.parse(2)


#Read in the Facility Address Excel file
xlsx2 = pd.ExcelFile("Building Address.xlsx")
#Construct DataFrame
facilities = xlsx2.parse(0)

#%%
#For Facilities
S_NameNum = facilities.loc[:, "Facility Address Line 1"]
City = facilities.loc[:, "Facility City Name"]
Zip = facilities.loc[:, "Facility Postal Code"]

#Create Addresses for Faciities in within a list FacAddresses[]
i = 0
j = 0
FacAddresses = []
address = ""

while (i < len(S_NameNum)):
    address = str(S_NameNum[i]) + " " + City[i] + ", " + "TX" + ", " + str(Zip[i])
    if (len(FacAddresses) == 0):
        FacAddresses.append(address) 
        print(len(FacAddresses))
        i += 1
        j = 0
    elif (address == str(FacAddresses[j])):
        print(len(FacAddresses))
        i += 1
    else:
        FacAddresses.append(address) 
        print(len(FacAddresses))
        i += 1
        j = len(FacAddresses) - 1

#%%
#This creates lists using the columns containing the address components 
S_Num = mykawa.loc[:, "Street Num"]
S_Name = mykawa.loc[:, "Street Name"]
City = mykawa.loc[:, "City Name"]
Zip = mykawa.loc[:, "Postal Code"]
DV_mykawa = mykawa.loc[:, "Deliv Packages Qty"]

#Create Addresses in within a list Addresses[]
DV = [0]
Addresses = [FacAddresses[9]]

i = 0
address = ""
while (i < len(S_Num)):
    Address = str(S_Num[i]) + " " + S_Name[i] + " " + City[i] + ", " + "TX" + ", " + str(Zip[i])
    Addresses.append(Address) 
    DV.append(DV_mykawa[i])
    i += 1


#Reapt above for Stafford
S_Num = stafford.loc[:, "Street Num"]
S_Name = stafford.loc[:, "Street Name"]
City = stafford.loc[:, "City Name"]
Zip = stafford.loc[:, "Postal Code"]
DV_stafford = stafford.loc[:, "Deliv Packages Qty"]

DV.append(0)
Addresses.append(FacAddresses[11])

i = 0
address = ""
while (i < len(S_Num)):
    address = str(S_Num[i]) + " " + S_Name[i] + " " + City[i] + ", " + "TX" + ", " + str(Zip[i])
    Addresses.append(address)
    DV.append(DV_stafford[i])
    i += 1


#Repeat above for Sweetwater
S_Num = sweetwater.loc[:, "Street Num"]
S_Name = sweetwater.loc[:, "Street Name"]
City = sweetwater.loc[:, "City Name"]
Zip = sweetwater.loc[:, "Postal Code"]
DV_sweetwater = sweetwater.loc[:, "Deliv Packages Qty"]

DV.append(0)
Addresses.append(FacAddresses[6])

i = 0
address = ""
while (i < len(S_Num)):
    address = str(S_Num[i]) + " " + S_Name[i] + " " + City[i] + ", " + "TX" + ", " + str(Zip[i])
    Addresses.append(address)
    DV.append(DV_sweetwater[i])
    i += 1
         
#%%
#Write Addresses to a text file
file = open("Addresses_517.txt", "w")
i = 0
address = ""
while (i < len(Addresses)):
    address = str(Addresses[i])
    file.write(address + "\n")
    i += 1
    if i == (len(Addresses) - 1):
        file.close
        
#%%
#Write Delivery Volumes to a text file
file = open("DelivVols_517.txt", "w")
i = 0
address = ""
while (i < len(DV)):
    d_vol = str(DV[i])
    file.write(d_vol + "\n")
    i += 1
    if i == (len(DV) - 1):
        file.close

#%%  
#Conversion using get_coords
from GetCoords import get_coords  
        
i = 0
CoordMat = []
while (i < len(Addresses)):
    coords = get_coords(Addresses[i])
    CoordMat.append(coords)
    i += 1

#%%
#Write list of coordinate pairs to a text file
file = open("Coords_517.txt", "w")
i = 0
coords = "" 
while (i < len(CoordMat)):
    coords = CoordMat[i]
    file.write(str(coords[0]) + ", " + str(coords[1]) + "\n")
    i += 1
    if i == (len(Addresses) - 1):
        file.close
        
#%%
        