import pypsa
import math
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import pandas as pd
import warnings
import geopandas as gpd
from shapely.errors import ShapelyDeprecationWarning
from pypsa.clustering.spatial import (
    aggregategenerators,
    aggregateoneport,
    busmap_by_stubs,
    get_clustering_from_busmap,
)
from matching.games import HospitalResident
from geopy.distance import geodesic
from shapely import Point
import operator
import spatial
#warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)
#plt.rc("figure", figsize=(10, 8))



#construct preferences
def get_preferences(network1, network2, reverse=False):
        network1_preferences=dict()
        for bus1 in network1.buses.index:
                
                bus1_preferences = dict()
                for bus2 in network2.buses.index:
                        if reverse==True:
                                dist = distance_between_buses(bus2,bus1)
                        else:
                                dist = distance_between_buses(bus1,bus2)
                        #if bus1 and bus2 are further away than threshold value, then they should
                        #never be merged
                        bus1_preferences[bus2] = dist      
                bus1_preferences = sorted(bus1_preferences, key=lambda x:x[1])
                network1_preferences[bus1] = bus1_preferences

        return network1_preferences


def distance_between_buses(bus_from_network_1,bus_from_network_2):
        bus1_point = gdf1.loc[bus_from_network_1,"geometry"]
        bus2_point = gdf2.loc[bus_from_network_2,"geometry"]
        distance = bus1_point.distance(bus2_point)
        return distance




def update_component_name(network, component_name, new_value, old_value):
        #update name in static dataframe for this component
        network.df(component_name).rename(index={old_value : new_value},inplace=True)

        list_name = component_name.lower()
        #update name in static dataframes of other components
        for component in network.iterate_components():
                if list_name in list(component.df.keys()):
                        component.df.get(list_name).replace({old_value : new_value},inplace=True)
                        
        #update name in time-varying dataframes of this component (if any exist)
        if network.pnl(component_name):
                for k,v in network.pnl(component_name).items():
                            network.pnl(component_name).get(k).rename(columns={old_value : new_value},inplace=True)

        #special case where a bus name is changed - requires special treatment
        if component_name == "Bus":
                for component in network.iterate_components():
                        if "bus" in list(component.df.keys()):
                                component.df.get("bus").replace({old_value : new_value},inplace=True)
                        if "bus0" in list(component.df.keys()):
                                component.df.get("bus0").replace({old_value : new_value},inplace=True)
                        if "bus1" in list(component.df):
                                component.df.get("bus1").replace({old_value : new_value},inplace=True)






def merge(network, other):
        to_skip = ["Network"]
        if other.srid != network.srid:
            logger.warning(
                f"Warning: spatial Reference System Indentifier {other.srid} for new network not equal to value {network.srid} of existing network. Original value will be used."
            )
        snapshots_aligned = network.snapshots.equals(other.snapshots)
        weightings_aligned = network.snapshot_weightings.equals(other.snapshot_weightings)
        assert (snapshots_aligned and weightings_aligned), "Error, snapshots or snapshot weightings do not agree, cannot add network with time-varying attributes."

        new_network = network
        for component in other.iterate_components(other.components.keys() - to_skip):
            # we do not add components whose ID is present in this network
            index_list = list(
                set(component.df.index) - set(network.df(component.name).index)
            )
            if set(index_list) != set(component.df.index) and component.name not in [
                "LineType",
                "TransformerType",
            ]:
                logger.warning(
                    f"Warning: components of type {component.name} in new network have duplicate IDs in existing network. These components will not be added"
                )
            # import static data for component
            df_to_add = component.df[component.df.index.isin(index_list)]
            new_network.import_components_from_dataframe(df_to_add, component.name)
            # import time series data for component
            for attr, df in component.pnl.items():
                    df_to_add = df.loc[:, df.columns.isin(index_list)]
                    new_network.import_series_from_dataframe(df, component.name, attr)

            return new_network


#rename any component in network1 such that there is a component (of the same type) in network2 with the same name
def rename_duplicated_items(network1, network2):
        for component in network1.iterate_components():
                n1_component_index = component.df.index
                n2_component_index = n2.df(component.name).index
                for comp1 in n1_component_index:
                        for comp2 in n2_component_index:
                                if comp1==comp2:
                                        update_component_name(n1, component.name, comp1+"_n1", comp1)
                                        continue
                
n1 = pypsa.Network("/Users/jessicaryan/Documents/GitHub/network-comparison/pypsa-networks/pypsa-eur-networks/elec_s_37.nc")
n2 = pypsa.Network("/Users/jessicaryan/Documents/GitHub/network-comparison/pypsa-networks/pypsa-earth-networks/elec_s_110_ec.nc")
print("rename duplicated items")
rename_duplicated_items(n1, n2)


gdf1 = gpd.GeoDataFrame(n1.buses, geometry=gpd.points_from_xy(n1.buses.x, n1.buses.y), crs="EPSG:4326").to_crs("EPSG:3857")
gdf2 = gpd.GeoDataFrame(n2.buses, geometry=gpd.points_from_xy(n2.buses.x, n2.buses.y), crs="EPSG:4326").to_crs("EPSG:3857")

print("n1 has order "+str(n1.buses.size))
print("n2 has order "+str(n2.buses.size))



                        
n1_preferences = get_preferences(n1,n2)
n2_preferences = get_preferences(n2,n1,reverse=True)
capacities = {bus: 1 for bus in n2.buses.index}

#could update prefs to remove partners further than thres distance           
stable_marriage_instance = HospitalResident.create_from_dictionaries(n1_preferences, n2_preferences,capacities)
#busmap has keys from n2 and values from n1
print("get the busmap")
busmap = stable_marriage_instance.solve()

string_busmap = dict()
for key in busmap.keys():
        value = busmap[key]
        string_busmap[str(key)] = str(value)

print("merging the original networks")

n3 = merge(n2,n1)
for bus in n3.buses.index:
        b = str(bus)
        if b not in string_busmap.keys():
                if bus not in n1.buses.index and bus not in n2.buses.index:
                string_busmap[b] = b
       
     

print("now create the clustering")
clustering = spatial.get_clustering_from_busmap(n3,string_busmap,with_time=False)

n4 = clustering.network
n4.buses.loc[:, ["x", "y"]] = n2.buses.loc[n3.buses.index, ["x", "y"]]


