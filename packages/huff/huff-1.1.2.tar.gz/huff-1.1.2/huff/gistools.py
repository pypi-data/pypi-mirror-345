#-----------------------------------------------------------------------
# Name:        gistools (huff package)
# Purpose:     GIS tools
# Author:      Thomas Wieland 
#              ORCID: 0000-0001-5168-9846
#              mail: geowieland@googlemail.com              
# Version:     1.1.2
# Last update: 2025-05-03 13:30
# Copyright (c) 2025 Thomas Wieland
#-----------------------------------------------------------------------


import geopandas as gp
from math import pi, sin, cos, acos


def distance_matrix(
    sources: list,
    destinations: list,
    unit: str = "m",
    ):

    def euclidean_distance (
        source: list,
        destination: list,
        unit: str = "m"
        ):

        lon1 = source[0]
        lat1 = source[1]
        lon2 = destination[0]
        lat2 = destination[1]

        lat1_r = lat1*pi/180
        lon1_r = lon1*pi/180
        lat2_r = lat2*pi/180
        lon2_r = lon2*pi/180

        distance = 6378 * (acos(sin(lat1_r) * sin(lat2_r) + cos(lat1_r) * cos(lat2_r) * cos(lon2_r - lon1_r)))
        if unit == "m": 
            distance = distance*1000
        if unit == "mile": 
            distance = distance/1.60934

        return distance

    matrix = []

    for source in sources:
        row = []
        for destination in destinations:
            dist = euclidean_distance(
                source, 
                destination, 
                unit
                )
            row.append(dist)
        matrix.append(row)

    return matrix


def overlay_difference(
    polygon_gdf: gp.GeoDataFrame, 
    sort_col: str = None,
    ):

    if sort_col is not None:
        polygon_gdf = polygon_gdf.sort_values(by=sort_col).reset_index(drop=True)
    else:
        polygon_gdf = polygon_gdf.reset_index(drop=True)

    new_geometries = []
    new_data = []

    for i in range(len(polygon_gdf) - 1, 0, -1):
        current_polygon = polygon_gdf.iloc[i].geometry
        previous_polygon = polygon_gdf.iloc[i - 1].geometry
        difference_polygon = current_polygon.difference(previous_polygon)

        if difference_polygon.is_empty or not difference_polygon.is_valid:
            continue

        new_geometries.append(difference_polygon)
        new_data.append(polygon_gdf.iloc[i].drop("geometry"))

    inner_most_polygon = polygon_gdf.iloc[0].geometry
    if inner_most_polygon.is_valid:
        new_geometries.append(inner_most_polygon)
        new_data.append(polygon_gdf.iloc[0].drop("geometry"))

    polygon_gdf_difference = gp.GeoDataFrame(
        new_data, geometry=new_geometries, crs=polygon_gdf.crs
    )

    return polygon_gdf_difference