#-----------------------------------------------------------------------
# Name:        tests_huff (huff package)
# Purpose:     Tests for Huff Model package functions
# Author:      Thomas Wieland 
#              ORCID: 0000-0001-5168-9846
#              mail: geowieland@googlemail.com              
# Version:     1.1.2
# Last update: 2025-05-03 13:32
# Copyright (c) 2025 Thomas Wieland
#-----------------------------------------------------------------------


from huff.ors import Client
from huff.models import load_geodata, create_interaction_matrix


# Isochrones test:

output_path = "."

ors_client = Client(
    auth = "5b3ce3597851110001cf62480a15aafdb5a64f4d91805929f8af6abd"
    )

isochrone_ORS = ors_client.isochrone (
    locations = [[7.593301534652711, 47.54329763735186], [9.207916,49.153868]], 
    save_output = True, 
    output_filepath = "test_isochrones.shp", 
    intersections="false"
    )

isochrone_ORS.summary()

# Matrix test:

matrix_ORS = ors_client.matrix(
    locations=[[9.70093,48.477473],[9.207916,49.153868],[37.573242,55.801281],[115.663757,38.106467]],
    save_output=True,
    output_filepath="test_matrix.csv"
    )

matrix_ORS.summary()


# Huff model test data:

Haslach = load_geodata(
    "data/Haslach.shp",
    location_type="origins",
    unique_id="BEZEICHN"
    )

Haslach.summary()

Haslach.define_marketsize("pop")

Haslach.define_transportcosts_weighting(
    param_lambda=-2.2
    )

Haslach.summary()


Haslach_supermarkets = load_geodata(
    "data/Haslach_supermarkets.shp",
    location_type="destinations",
    unique_id="LFDNR"
    )

Haslach_supermarkets.summary()

Haslach_supermarkets.isochrones(
    save_output=True,
    ors_auth = "5b3ce3597851110001cf62480a15aafdb5a64f4d91805929f8af6abd",
    output_filepath="Haslach_supermarkets_iso.shp"
    )

Haslach_supermarkets.define_attraction("VKF_qm")

Haslach_supermarkets.define_attraction_weighting(
    param_gamma=0.9
    )

Haslach_supermarkets.summary()


haslach_interactionmatrix = create_interaction_matrix(
    Haslach,
    Haslach_supermarkets
    )

interaction_matrix = haslach_interactionmatrix.transport_costs(
    ors_auth="5b3ce3597851110001cf62480a15aafdb5a64f4d91805929f8af6abd"
    )

interaction_matrix = interaction_matrix.flows()

huff_model = interaction_matrix.marketareas()

print(interaction_matrix.get_interaction_matrix_df())

print(huff_model.get_market_areas_df())