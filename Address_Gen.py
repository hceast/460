#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  9 16:04:43 2018

@author: igmcnelis
"""

import pandas as pd

#Read in formatted Excel file
xlsx = pd.ExcelFile("Building Address.xlsx")
#Construct a DataFrame for each sheet
mykawa = xlsx.parse(0)
stafford = xlsx.parse(1)
sweetwater = xlsx.parse(2)


#This creates lists using the columns containing the address components
S_Num = mykawa.loc[:, "Street Num"]
S_Name = mykawa.loc[:, "Street Name"]
City = mykawa.loc[:, "City Name"]
Zip = mykawa.loc[:, "Postal Code"]

#Create Addresses in within an array
i = 0
Addresses = []
Address = ""

while (i < len(S_Num)):
    Address = str(S_Num[i]) + " " + S_Name[i] + " " + City[i] + ", " + "TX" + ", " + str(Zip[i])
    Addresses.append(Address) 
    i += 1


#Reapt for Stafford
S_Num = stafford.loc[:, "Street Num"]
S_Name = stafford.loc[:, "Street Name"]
City = stafford.loc[:, "City Name"]
Zip = stafford.loc[:, "Postal Code"]

i = 0
Address = ""
while (i < len(S_Num)):
    Address = str(S_Num[i]) + " " + S_Name[i] + " " + City[i] + ", " + "TX" + ", " + str(Zip[i])
    Addresses.append(Address) 
    i += 1


#Repeat for Sweetwater
S_Num = sweetwater.loc[:, "Street Num"]
S_Name = sweetwater.loc[:, "Street Name"]
City = sweetwater.loc[:, "City Name"]
Zip = sweetwater.loc[:, "Postal Code"]

i = 0
Address = ""
while (i < len(S_Num)):
    Address = str(S_Num[i]) + " " + S_Name[i] + " " + City[i] + ", " + "TX" + ", " + str(Zip[i])
    Addresses.append(Address) 
    i += 1

#%%
#Write to .txt file
file = open("Addresses517.txt", "w")
i = 0
Address = ""
while (i < len(Addresses)):
    Address = str(Addresses[i])
    file.write(Address + "\n")
    i += 1
    if i == (len(Addresses) - 1):
        file.close

#%%