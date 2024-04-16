import matching.games.hospital_resident
import geopandas as gpd


def get_busmap(network1, network2):
    network1_prefs = get_preferences(network1, network2)
    network2_prefs = get_preferences(network2, network1)
    capacities = {bus: 1 for bus in network2.buses.index}

    stable_marriage_instance = matching.games.HospitalResident.create_from_dictionaries(
        network1_prefs, network2_prefs, capacities)
    #   busmap has keys from n2 and values from n1
    busmap = stable_marriage_instance.solve()
    string_busmap = dict()

    for key in busmap.keys():
        value = busmap[key]
        string_busmap[str(key)] = str(value)


# construct preferences
def get_preferences(network1, network2):
    gdf1 = gpd.GeoDataFrame(network1.buses, geometry=gpd.points_from_xy(network1.buses.x, network1.buses.y), crs="EPSG:4326").to_crs("EPSG:3857")
    gdf2 = gpd.GeoDataFrame(network2.buses, geometry=gpd.points_from_xy(network2.buses.x, network2.buses.y), crs="EPSG:4326").to_crs("EPSG:3857")

    network1_preferences = dict()
    for bus1 in network1.buses.index:

        bus1_preferences = dict()
        for bus2 in network2.buses.index:
            # if network1.buses.loc[bus1,"country"] == network2.buses.loc[bus2,"country"]:
            dist = distance_between_buses(bus1, bus2, gdf1, gdf2)
            # if bus1 and bus2 are further away than threshold value, then they should
            # never be merged
            bus1_preferences[bus2] = dist
        bus1_preferences = sorted(bus1_preferences, key=lambda x: x[1])

        network1_preferences[bus1] = bus1_preferences

    return network1_preferences


def distance_between_buses(bus_from_network_1, bus_from_network_2, gdf1, gdf2):
    bus1_point = gdf1.loc[bus_from_network_1, "geometry"]
    bus2_point = gdf2.loc[bus_from_network_2, "geometry"]
    distance = bus1_point.distance(bus2_point)
    return distance
