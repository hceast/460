#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 12 19:54:59 2018

@author: igmcnelis
"""
#Use ArcGIS geocoder to convert addresses to coordinates
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
