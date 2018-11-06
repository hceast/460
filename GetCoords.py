#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 12 19:54:59 2018

@author: igmcnelis

Uses ArcGIS geocoder to convert addresses to coordinates.
The fucntion takes a a sting that is an address as an argument.
To call function, type the following into Python console:
    get_coords("1234 Fake Address Drive, City, TX 77000")
    
Note: The address doesn't need to be exactly in that format. The geocoder will find the address that comes closest.
"""
#Uses ArcGIS geocoder to convert addresses to coordinates
#Import Packages
from arcgis.gis import GIS
from arcgis.geocoding import geocode
dev_gis = GIS()

def get_coords(address):
    
    address = str(address)
    geocode_result = geocode(address)[0]
    location = geocode_result["location"]
    coords = (location["x"], location["y"])
    
    return coords
