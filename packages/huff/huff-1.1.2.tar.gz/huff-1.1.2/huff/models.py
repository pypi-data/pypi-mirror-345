#-----------------------------------------------------------------------
# Name:        models (huff package)
# Purpose:     Huff Model classes and functions
# Author:      Thomas Wieland 
#              ORCID: 0000-0001-5168-9846
#              mail: geowieland@googlemail.com              
# Version:     1.1.2
# Last update: 2025-05-03 13:29
# Copyright (c) 2025 Thomas Wieland
#-----------------------------------------------------------------------


import pandas as pd
import geopandas as gp
import numpy as np
import time
from huff.ors import Client, TimeDistanceMatrix, Isochrone
from huff.gistools import overlay_difference, distance_matrix


class CustomerOrigins:

    def __init__(
        self,
        geodata_gpd, 
        geodata_gpd_original, 
        metadata
        ):

        self.geodata_gpd = geodata_gpd
        self.geodata_gpd_original = geodata_gpd_original
        self.metadata = metadata

    def get_geodata_gpd(self):

        return self.geodata_gpd

    def get_geodata_gpd_original(self):

        return self.geodata_gpd_original

    def get_metadata(self):
        
        return self.metadata

    def summary(self):

        metadata = self.metadata

        print("Huff Model Customer Origins")
        print("No. locations              " + str(metadata["no_points"]))
        
        if metadata["marketsize_col"] is None:
            print("Market size column         not defined")
        else:
            print("Market size column         " + metadata["marketsize_col"])
        
        if metadata["weighting"][0]["func"] is None and metadata["weighting"][0]["param"] is None:
            print("Transport cost weighting   not defined")
        else:
            print("Transport cost weighting   " + metadata["weighting"][0]["func"] + " with lambda = " + str(metadata["weighting"][0]["param"]))
        
        print("Unique ID column           " + metadata["unique_id"])
        print("Input CRS                  " + str(metadata["crs_input"]))

        return metadata
    
    def define_marketsize(
        self,
        marketsize_col
        ):

        geodata_gpd_original = self.geodata_gpd_original
        metadata = self.metadata

        if marketsize_col not in geodata_gpd_original.columns:
            raise KeyError ("Column " + marketsize_col + " not in data")
        else:
            metadata["marketsize_col"] = marketsize_col

        self.metadata = metadata

        return self

    def define_transportcosts_weighting(
        self,
        func = "power",
        param_lambda = -2
        ):

        metadata = self.metadata

        metadata["weighting"][0]["func"] = func
        metadata["weighting"][0]["param"] = param_lambda

        self.metadata = metadata

        return self

class SupplyLocations:

    def __init__(
        self,
        geodata_gpd, 
        geodata_gpd_original, 
        metadata
        ):

        self.geodata_gpd = geodata_gpd
        self.geodata_gpd_original = geodata_gpd_original
        self.metadata = metadata

    def get_geodata_gpd(self):
        return self.geodata_gpd

    def get_geodata_gpd_original(self):
        return self.geodata_gpd_original

    def get_metadata(self):
        return self.metadata

    def summary(self):

        metadata = self.metadata

        print("Huff Model Supply Locations")
        print("No. locations         " + str(metadata["no_points"]))

        if metadata["attraction_col"][0] is None or metadata["attraction_col"] == []:
            print("Attraction column(s)  not defined")
        else:
            print("Attraction column(s)  " + ",".join(metadata["attraction_col"]))
        
        if metadata["weighting"][0]["func"] is None and metadata["weighting"][0]["param"] is None:
            print("Attraction weighting  not defined")
        else:
            print("Attraction weighting  " + metadata["weighting"][0]["func"] + " with gamma = " + str(metadata["weighting"][0]["param"]))
        
        print("Unique ID column      " + metadata["unique_id"])
        print("Input CRS             " + str(metadata["crs_input"]))

        return metadata

    def define_attraction(
        self,
        attraction_col
        ):

        geodata_gpd_original = self.geodata_gpd_original
        metadata = self.metadata

        if attraction_col not in geodata_gpd_original.columns:
            raise KeyError ("Column " + attraction_col + " not in data")
        else:
            metadata["attraction_col"][0] = attraction_col

        self.metadata = metadata

        return self
    
    def define_attraction_weighting(
        self,
        func = "power",
        param_gamma = 1
        ):

        metadata = self.metadata

        if metadata["attraction_col"] is None:
            raise ValueError ("Attraction column is not yet defined. Use SupplyLocations.define_attraction()")
        
        metadata["weighting"][0]["func"] = func
        metadata["weighting"][0]["param"] = param_gamma
        self.metadata = metadata

        return self

    def add_var(
        self,
        var: str = None,
        func: str = None,
        param: float = None
        ):

        metadata = self.metadata

        if metadata["attraction_col"] is None:
            raise ValueError ("Attraction column is not yet defined. Use SupplyLocations.define_attraction()")

        no_attraction_vars = len(metadata["attraction_col"])
        new_key = no_attraction_vars

        metadata["attraction_col"] = metadata["attraction_col"] + [var] 

        metadata["weighting"][new_key] = {
            "func": func,
            "param": param
            }

        self.metadata = metadata

        return self
    
    def add_new_destinations(
        self,
        new_destinations,
        ):
        
        geodata_gpd_original = self.get_geodata_gpd_original()
        geodata_gpd = self.get_geodata_gpd()
        metadata = self.get_metadata()

        new_destinations_gpd_original = new_destinations.get_geodata_gpd_original()
        new_destinations_gpd = new_destinations.get_geodata_gpd()
        new_destinations_metadata = new_destinations.get_metadata()

        if list(new_destinations_gpd_original.columns) != list(geodata_gpd_original.columns):
            raise KeyError("Supply locations and new destinations data have different column names.")
        if list(new_destinations_gpd.columns) != list(geodata_gpd.columns):
            raise KeyError("Supply locations and new destinations data have different column names.")

        geodata_gpd_original = geodata_gpd_original.append(
            new_destinations_gpd_original, 
            ignore_index=True
            )
        
        geodata_gpd = geodata_gpd.append(
            new_destinations_gpd, 
            ignore_index=True
            )
        
        metadata["no_points"] = metadata["no_points"]+new_destinations_metadata["no_points"]
        
        self.geodata_gpd = geodata_gpd
        self.geodata_gpd_original = geodata_gpd_original
        self.metadata = metadata

        return self
    
    def isochrones(
        self,
        segments: list = [900, 600, 300],
        range_type: str = "time",
        intersections: str = "true",
        profile: str = "driving-car",
        donut: bool = True,
        ors_server: str = "https://api.openrouteservice.org/v2/",
        ors_auth: str = None,
        timeout = 10,
        delay = 1,
        save_output: bool = True,
        output_filepath: str = "isochrones.shp",
        output_crs: str = "EPSG:4326"
        ):

        geodata_gpd = self.get_geodata_gpd()
        metadata = self.get_metadata()

        coords = [(point.x, point.y) for point in geodata_gpd.geometry]
        
        unique_id_col = metadata["unique_id"]
        unique_id_values = geodata_gpd[unique_id_col].values

        ors_client = Client(
            server = ors_server,
            auth = ors_auth
            )
        
        isochrones_gdf = gp.GeoDataFrame(columns=[unique_id_col, "geometry"])
        
        i = 0

        for x, y in coords:
            
            isochrone_output = ors_client.isochrone(
                locations = [[x, y]],
                segments = segments,
                range_type = range_type,
                intersections = intersections,
                profile = profile,
                timeout = timeout,
                save_output = False,
                output_crs = output_crs
                )
            
            if isochrone_output.status_code != 200:
                continue        
            
            isochrone_gdf = isochrone_output.get_isochrones_gdf()
            
            if donut:
                isochrone_gdf = overlay_difference(
                    polygon_gdf = isochrone_gdf, 
                    sort_col = "segment"
                    )
                
            time.sleep(delay)

            isochrone_gdf[unique_id_col] = unique_id_values[i]

            isochrones_gdf = pd.concat(
                [
                    isochrones_gdf, 
                    isochrone_gdf
                    ], 
                ignore_index=True
                )
            
            i = i+1

        isochrones_gdf.set_crs(
            output_crs, 
            allow_override=True, 
            inplace=True
            )
            
        if save_output:

            isochrones_gdf.to_file(filename = output_filepath)

        return isochrones_gdf

class InteractionMatrix:

    def __init__(
        self, 
        interaction_matrix_df,
        customer_origins,
        supply_locations
        ):

        self.interaction_matrix_df = interaction_matrix_df
        self.customer_origins = customer_origins
        self.supply_locations = supply_locations
    
    def get_interaction_matrix_df(self):
        return self.interaction_matrix_df
    
    def get_customer_origins(self):
        return self.customer_origins

    def get_supply_locations(self):
        return self.supply_locations
    
    def summary(self):

        customer_origins_metadata = self.get_customer_origins().get_metadata()
        supply_locations_metadata = self.get_supply_locations().get_metadata()

        print("Huff Model Interaction Matrix")
        print("----------------------------------")
        print("Supply locations   " + str(supply_locations_metadata["no_points"]))
        if supply_locations_metadata["attraction_col"][0] is None:
            print("Attraction column  not defined")
        else:
            print("Attraction column  " + supply_locations_metadata["attraction_col"][0])
        print("Customer origins   " + str(customer_origins_metadata["no_points"]))
        if customer_origins_metadata["marketsize_col"] is None:
            print("Market size column not defined")
        else:
            print("Market size column " + customer_origins_metadata["marketsize_col"])
        print("----------------------------------")
        print("Weights")
        if supply_locations_metadata["weighting"][0]["func"] is None and supply_locations_metadata["weighting"][0]["param"] is None:
            print("Gamma              not defined")
        else:
            print("Gamma              " + str(supply_locations_metadata["weighting"][0]["param"]) + " (" + supply_locations_metadata["weighting"][0]["func"] + ")")
        if customer_origins_metadata["weighting"][0]["func"] is None and customer_origins_metadata["weighting"][0]["param"] is None:
            print("Lambda             not defined")
        else:
            print("Lambda            " + str(customer_origins_metadata["weighting"][0]["param"]) + " (" + customer_origins_metadata["weighting"][0]["func"] + ")")     
        print("----------------------------------")

    def transport_costs(
        self,
        network: bool = True,
        range_type: str = "time",
        time_unit: str = "minutes",
        distance_unit: str = "kilometers",
        ors_server: str = "https://api.openrouteservice.org/v2/",
        ors_auth: str = None,
        save_output: bool = False,
        output_filepath: str = "transport_costs_matrix.csv"
        ):

        if not network and range_type == "time":
            print ("Calculating euclidean distances (network = False). Setting range_type = 'distance'")
            range_type = "distance"
        
        interaction_matrix_df = self.get_interaction_matrix_df()

        customer_origins = self.get_customer_origins()
        customer_origins_geodata_gpd = customer_origins.get_geodata_gpd()
        customer_origins_metadata = customer_origins.get_metadata()
        customer_origins_uniqueid = customer_origins_metadata["unique_id"]
        customer_origins_coords = [[point.x, point.y] for point in customer_origins_geodata_gpd.geometry]
        customer_origins_ids = customer_origins_geodata_gpd[customer_origins_uniqueid].tolist()

        supply_locations = self.get_supply_locations()
        supply_locations_geodata_gpd = supply_locations.get_geodata_gpd()
        supply_locations_metadata = supply_locations.get_metadata()
        supply_locations_uniqueid = supply_locations_metadata["unique_id"]
        supply_locations_coords = [[point.x, point.y] for point in supply_locations_geodata_gpd.geometry]
        supply_locations_ids = supply_locations_geodata_gpd[supply_locations_uniqueid].tolist()
   
        locations_coords = customer_origins_coords + supply_locations_coords        
        
        customer_origins_index = list(range(len(customer_origins_coords)))
        locations_coords_index = list(range(len(customer_origins_index), len(locations_coords)))

        if network:

            ors_client = Client(
                server = ors_server,
                auth = ors_auth
                )
            time_distance_matrix = ors_client.matrix(
                locations = locations_coords,
                save_output = save_output,
                output_filepath = output_filepath, 
                sources = customer_origins_index,
                destinations = locations_coords_index,
                range_type = range_type
                )
            
            if time_distance_matrix.get_metadata() is None:
                raise ValueError ("No transport costs matrix was built.")

            transport_costs_matrix = time_distance_matrix.get_matrix()
            transport_costs_matrix_config = time_distance_matrix.get_config()
            range_type = transport_costs_matrix_config["range_type"]

            transport_costs_matrix["source"] = transport_costs_matrix["source"].astype(int)
            transport_costs_matrix["source"] = transport_costs_matrix["source"].map(
                dict(enumerate(customer_origins_ids))
                )
            
            transport_costs_matrix["destination"] = transport_costs_matrix["destination"].astype(int)
            transport_costs_matrix["destination"] = transport_costs_matrix["destination"].map(
                dict(enumerate(supply_locations_ids))
                )
            
            transport_costs_matrix["source_destination"] = transport_costs_matrix["source"].astype(str)+"_"+transport_costs_matrix["destination"].astype(str)
            transport_costs_matrix = transport_costs_matrix[["source_destination", range_type]]

            interaction_matrix_df = interaction_matrix_df.merge(
                transport_costs_matrix,
                left_on="ij",
                right_on="source_destination"
                )
            
            interaction_matrix_df["t_ij"] = interaction_matrix_df[range_type]
            if time_unit == "minutes":
                interaction_matrix_df["t_ij"] = interaction_matrix_df["t_ij"]/60
            if time_unit == "hours":
                interaction_matrix_df["t_ij"] = interaction_matrix_df["t_ij"]/60/60

            interaction_matrix_df = interaction_matrix_df.drop(columns=["source_destination", range_type])

        else:

            distance_matrix_result = distance_matrix(
                sources = customer_origins_coords,
                destinations = supply_locations_coords,
                unit = "m"
                )
            
            distance_matrix_result_flat = [distance for sublist in distance_matrix_result for distance in sublist]

            interaction_matrix_df["t_ij"] = distance_matrix_result_flat

            if distance_unit == "kilometers":
                interaction_matrix_df["t_ij"] = interaction_matrix_df["t_ij"]/1000

        self.interaction_matrix_df = interaction_matrix_df

        return self
    
    def utility(self):
        
        interaction_matrix_df = self.interaction_matrix_df

        if interaction_matrix_df["t_ij"].isna().all():
            raise ValueError ("Transport cost variable is not defined")
        if interaction_matrix_df["A_j"].isna().all():
            raise ValueError ("Attraction variable is not defined")

        check_vars(
            df = interaction_matrix_df,
            cols = ["A_j", "t_ij"]
            )
        
        customer_origins = self.customer_origins
        customer_origins_metadata = customer_origins.get_metadata()
        tc_weighting = customer_origins_metadata["weighting"][0]
        if tc_weighting["func"] == "power":
            interaction_matrix_df["t_ij_weighted"] = interaction_matrix_df["t_ij"] ** tc_weighting["param"]
        elif tc_weighting["func"] == "exponential":
            interaction_matrix_df["t_ij_weighted"] = np.exp(tc_weighting["param"] * interaction_matrix_df['t_ij'])
        else:
            raise ValueError ("Transport costs weighting is not defined.")
                           
        supply_locations = self.supply_locations
        supply_locations_metadata = supply_locations.get_metadata()
        attraction_weighting = supply_locations_metadata["weighting"][0]
        if attraction_weighting["func"] == "power":
            interaction_matrix_df["A_j_weighted"] = interaction_matrix_df["A_j"] ** attraction_weighting["param"]
        elif tc_weighting["func"] == "exponential":
            interaction_matrix_df["A_j_weighted"] = np.exp(attraction_weighting["param"] * interaction_matrix_df['A_j'])
        else:
            raise ValueError ("Attraction weighting is not defined.")
        
        interaction_matrix_df["U_ij"] = interaction_matrix_df["A_j_weighted"]/interaction_matrix_df["t_ij_weighted"]
        
        interaction_matrix_df = interaction_matrix_df.drop(columns=['A_j_weighted', 't_ij_weighted'])

        self.interaction_matrix_df = interaction_matrix_df

        return self
    
    def probabilities (self):

        interaction_matrix_df = self.interaction_matrix_df

        if interaction_matrix_df["U_ij"].isna().all():
            self.utility()
            interaction_matrix_df = self.interaction_matrix_df

        utility_i = pd.DataFrame(interaction_matrix_df.groupby("i")["U_ij"].sum())
        utility_i = utility_i.rename(columns = {"U_ij": "U_i"})

        interaction_matrix_df = interaction_matrix_df.merge(
            utility_i,
            left_on="i",
            right_on="i",
            how="inner"
            )

        interaction_matrix_df["p_ij"] = (interaction_matrix_df["U_ij"]) / (interaction_matrix_df["U_i"])

        interaction_matrix_df = interaction_matrix_df.drop(columns=["U_i"])

        self.interaction_matrix_df = interaction_matrix_df

        return self
        
    def flows (self):

        interaction_matrix_df = self.interaction_matrix_df

        if interaction_matrix_df["C_i"].isna().all():
            raise ValueError ("Market size column in customer origins not defined. Use CustomerOrigins.define_marketsize()")

        check_vars(
            df = interaction_matrix_df,
            cols = ["C_i"]
            )

        if interaction_matrix_df["p_ij"].isna().all():
            self.probabilities()
            interaction_matrix_df = self.interaction_matrix_df

        interaction_matrix_df["E_ij"] = interaction_matrix_df["p_ij"] * interaction_matrix_df["C_i"]

        self.interaction_matrix_df = interaction_matrix_df

        return self

    def marketareas (self):

        interaction_matrix_df = self.interaction_matrix_df
        
        check_vars(
            df = interaction_matrix_df,
            cols = ["E_ij"]
            )
        
        market_areas_df = pd.DataFrame(interaction_matrix_df.groupby("j")["E_ij"].sum())
        market_areas_df = market_areas_df.reset_index(drop=False)
        market_areas_df = market_areas_df.rename(columns={"E_ij": "T_j"})

        huff_model = HuffModel(
            self,
            market_areas_df
            )
        
        return huff_model

    def mci_transformation(
        self,
        cols: list = ["A_j", "t_ij"]
        ):

        """ MCI model log-centering transformation """
        
        cols = cols + ["p_ij"]

        interaction_matrix_df = self.interaction_matrix_df

        interaction_matrix_df = mci_transformation(
            df = interaction_matrix_df,
            ref_col = "i",
            cols = cols
            )
        
        self.interaction_matrix_df = interaction_matrix_df

        return self

class HuffModel:

    def __init__(
        self,
        interaction_matrix, 
        market_areas_df
        ):

        self.interaction_matrix = interaction_matrix
        self.market_areas_df = market_areas_df

    def get_interaction_matrix_df(self):

        interaction_matrix = self.interaction_matrix
        interaction_matrix_df = interaction_matrix.get_interaction_matrix_df()

        return interaction_matrix_df
    
    def get_supply_locations(self):

        interaction_matrix = self.interaction_matrix
        supply_locations = interaction_matrix.get_supply_locations()

        return supply_locations

    def get_customer_origins(self):

        interaction_matrix = self.interaction_matrix
        customer_origins = interaction_matrix.get_customer_origins()

        return customer_origins

    def get_market_areas_df(self):
        return self.market_areas_df
    
    def summary(self):

        interaction_matrix = self.interaction_matrix

        customer_origins_metadata = interaction_matrix.get_customer_origins().get_metadata()
        supply_locations_metadata = interaction_matrix.get_supply_locations().get_metadata()

        print("Huff Model")
        print("----------------------------------")
        print("Supply locations   " + str(supply_locations_metadata["no_points"]))
        if supply_locations_metadata["attraction_col"][0] is None:
            print("Attraction column  not defined")
        else:
            print("Attraction column  " + supply_locations_metadata["attraction_col"][0])
        print("Customer origins   " + str(customer_origins_metadata["no_points"]))
        if customer_origins_metadata["marketsize_col"] is None:
            print("Market size column not defined")
        else:
            print("Market size column " + customer_origins_metadata["marketsize_col"])
        print("----------------------------------")
        print("Weights")
        if supply_locations_metadata["weighting"][0]["func"] is None and supply_locations_metadata["weighting"][0]["param"] is None:
            print("Gamma              not defined")
        else:
            print("Gamma              " + str(supply_locations_metadata["weighting"][0]["param"]) + " (" + supply_locations_metadata["weighting"][0]["func"] + ")")
        if customer_origins_metadata["weighting"][0]["func"] is None and customer_origins_metadata["weighting"][0]["param"] is None:
            print("Lambda             not defined")
        else:
            print("Lambda            " + str(customer_origins_metadata["weighting"][0]["param"]) + " (" + customer_origins_metadata["weighting"][0]["func"] + ")")     
        print("----------------------------------")
          
def load_geodata (
    file, 
    location_type: str, 
    unique_id: str,
    x_col: str = None, 
    y_col: str = None,
    data_type = "shp", 
    csv_sep = ";", 
    csv_decimal = ",", 
    csv_encoding="unicode_escape", 
    crs_input = "EPSG:4326"    
    ):

    if location_type is None or (location_type != "origins" and location_type != "destinations"):
        raise ValueError ("location_type must be either 'origins' or 'destinations'")
    
    if data_type not in ["shp", "csv", "xlsx"]:
        raise ValueError ("data_type must be 'shp', 'csv' or 'xlsx'")

    if data_type == "shp":
        geodata_gpd_original = gp.read_file(file)
        crs_input = geodata_gpd_original.crs

    if data_type == "csv" or data_type == "xlsx":
        if x_col is None:
            raise ValueError ("Missing value for X coordinate column")
        if y_col is None:
            raise ValueError ("Missing value for Y coordinate column")

    if data_type == "csv":
        geodata_tab = pd.read_csv(
            file, 
            sep = csv_sep, 
            decimal = csv_decimal, 
            encoding = csv_encoding
            )
    
    if data_type == "xlsx":
        geodata_tab = pd.read_excel(file)

    if data_type == "csv" or data_type == "xlsx":
        geodata_gpd_original = gp.GeoDataFrame(
            geodata_tab, 
            geometry = gp.points_from_xy(
                geodata_tab[x_col], 
                geodata_tab[y_col]
                ), 
            crs = crs_input
            )

    crs_output = "EPSG:4326"
    geodata_gpd = geodata_gpd_original.to_crs(crs_output)
    geodata_gpd = geodata_gpd[[unique_id, "geometry"]]

    metadata = {
        "location_type": location_type,
        "unique_id": unique_id,
        "attraction_col": [None],
        "marketsize_col": None,
        "weighting": {
            0: {
                "func": None, 
                "param": None
                }
            },
        "crs_input": crs_input,
        "crs_output": crs_output,
        "no_points": len(geodata_gpd)
        }    
    
    if location_type == "origins":
        geodata_object = CustomerOrigins(
            geodata_gpd, 
            geodata_gpd_original, 
            metadata
            )        
    elif location_type == "destinations":
        geodata_object = SupplyLocations(
            geodata_gpd, 
            geodata_gpd_original, 
            metadata
            )

    return geodata_object
    
def create_interaction_matrix(
    customer_origins,
    supply_locations    
    ):

    if not isinstance(customer_origins, CustomerOrigins):
        raise ValueError ("customer_origins must be of class CustomerOrigins")
    if not isinstance(supply_locations, SupplyLocations):
        raise ValueError ("supply_locations must be of class SupplyLocations")

    customer_origins_metadata = customer_origins.get_metadata()
    if customer_origins_metadata["marketsize_col"] is None:
        raise ValueError("Market size column in customer origins not defined. Use CustomerOrigins.define_marketsize()")
    
    supply_locations_metadata = supply_locations.get_metadata()
    if supply_locations_metadata["attraction_col"][0] is None:
        raise ValueError("Attraction column in supply locations not defined. Use SupplyLocations.define_attraction()")

    customer_origins_unique_id = customer_origins_metadata["unique_id"]
    customer_origins_marketsize = customer_origins_metadata["marketsize_col"]

    customer_origins_geodata_gpd = pd.DataFrame(customer_origins.get_geodata_gpd())
    customer_origins_geodata_gpd_original = pd.DataFrame(customer_origins.get_geodata_gpd_original())
    customer_origins_data = pd.merge(
        customer_origins_geodata_gpd,
        customer_origins_geodata_gpd_original[[customer_origins_unique_id, customer_origins_marketsize]],
        left_on = customer_origins_unique_id,
        right_on = customer_origins_unique_id 
        )
    customer_origins_data = customer_origins_data.rename(columns = {
        customer_origins_unique_id: "i",
        customer_origins_marketsize: "C_i",
        "geometry": "i_coords"
        }
        )

    supply_locations_unique_id = supply_locations_metadata["unique_id"]
    supply_locations_attraction = supply_locations_metadata["attraction_col"][0]

    supply_locations_geodata_gpd = pd.DataFrame(supply_locations.get_geodata_gpd())
    supply_locations_geodata_gpd_original = pd.DataFrame(supply_locations.get_geodata_gpd_original())
    supply_locations_data = pd.merge(
        supply_locations_geodata_gpd,
        supply_locations_geodata_gpd_original[[supply_locations_unique_id, supply_locations_attraction]],
        left_on = supply_locations_unique_id,
        right_on = supply_locations_unique_id 
        )
    supply_locations_data = supply_locations_data.rename(columns = {
        supply_locations_unique_id: "j",
        supply_locations_attraction: "A_j",
        "geometry": "j_coords"
        }
        )

    interaction_matrix_df = customer_origins_data.merge(
        supply_locations_data, 
        how = "cross"
        )
    interaction_matrix_df["ij"] = interaction_matrix_df["i"].astype(str)+"_"+interaction_matrix_df["j"].astype(str)
    interaction_matrix_df["t_ij"] = None
    interaction_matrix_df["U_ij"] = None
    interaction_matrix_df["p_ij"] = None
    interaction_matrix_df["E_ij"] = None

    interaction_matrix = InteractionMatrix(
        interaction_matrix_df,
        customer_origins,
        supply_locations
        )
         
    return interaction_matrix

def check_vars(
    df: pd.DataFrame,
    cols: list
    ):

    for col in cols:
        if col not in df.columns:
            raise KeyError(f"Column '{col}' not in dataframe.")
    
    for col in cols:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise ValueError(f"Column '{col}' is not numeric. All columns must be numeric.")
    
    for col in cols:
        if (df[col] <= 0).any():
            raise ValueError(f"Column '{col}' includes values <= 0. All values must be numeric and positive.")

def mci_transformation(
    df: pd.DataFrame,
    ref_col: str,
    cols: list
    ):
   
    check_vars(
        df = df,
        cols = cols + [ref_col]
        )

    def lct (x):

        x_geom = np.exp(np.log(x).mean())
        x_lct = np.log(x/x_geom)

        return x_lct
    
    for var in cols:

        var_t = df.groupby(ref_col)[var].apply(lct)
        var_t = var_t.reset_index()
        df[var+"_t"] = var_t[var]

    return df