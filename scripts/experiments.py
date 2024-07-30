from pathlib import Path
import pypsa
import pandas as pd
import geopandas as gpd
import networkx as nx
from pypsa.clustering.spatial import get_clustering_from_busmap
import numpy as np

gadm_shape = "data/pypsa-earth/resources/shapes/gadm_shapes.geojson"
country_shape = "data/pypsa-earth/resources/shapes/country_shapes.geojson"

comparison_methodology = {
    "method": "shape",
    "options": {
        "path": "data/pypsa-earth/resources/shapes/country_shapes.geojson"
    }
}  # method option among: ["country_shape", "gadm_shape", ...]
# TODO: expand to include network_1 and network_2; example: create voronoi polygons and compare them or alike,
# or "find_closest" to compare the closest nodes

# global crs parameters
GEO_CRS = "EPSG:4326"
METRIC_CRS = "EPSG:3857"

aggregation_strategies = {
    "generators": {  # use "min" for more conservative assumptions
        "p_nom": "sum",
        "p_nom_max": "sum",
        "p_nom_min": "sum",
        "p_min_pu": "mean",
        "marginal_cost": "mean",
        "committable": "any",
        "ramp_limit_up": "max",
        "ramp_limit_down": "max",
        "efficiency": "mean",
    }
}


def run_experiment_for_pair(path_network_1, path_network_2):
    eur_filename = 'eur_'+Path(path_network_1).stem
    earth_filename = 'earth_'+Path(path_network_2).stem

    print(path_network_1)
    print(path_network_2)
    # Load networks
    n1 = pypsa.Network(path_network_1)  # first network
    n2 = pypsa.Network(path_network_2)  # second network
    #Execute the mapping
    n1_mapped, n1_mapped_busmap = create_clustered_network(n1, comparison_methodology)
    n2_mapped, n2_mapped_busmap = create_clustered_network(n2, comparison_methodology)

    #General statistics by networks

    #n1 STATS TABLE
    s1 = n1_mapped.statistics()

    #n2 STATS TABLE
    s2 = n2_mapped.statistics()

    #Calculate percentage difference
    delta_mapped = s2 - s1

    #PERCENTAGE DIFF TABLE
    delta_mapped_pc = delta_mapped / s1 * 100

    #n1 PLOT
    n1.plot()
    #n2 PLOT
    n2.plot()

    
    #Compare lines as dataframe
    lines1 = add_line_names(n1_mapped.lines.copy()).set_index("name")
    lines2 = add_line_names(n2_mapped.lines.copy()).set_index("name")

    carrier = pd.concat([lines1.carrier, lines2.carrier[lines2.index.difference(lines1.index)]], ignore_index=False)

    delta_lines = pd.concat([carrier, lines1.s_nom.rename("lines 1"), lines2.s_nom.rename("lines 2")], axis=1).fillna(0)
    delta_lines["bus0"] = delta_lines.index.str.split(" - ").str[0] 
    delta_lines["bus1"] = delta_lines.index.str.split(" - ").str[1] 
    delta_lines["delta"] = delta_lines["lines 2"] - delta_lines["lines 1"]
    delta_lines["delta_pu"] = (delta_lines["delta"] / (delta_lines["lines 1"] + delta_lines["lines 2"]) * 2).fillna(0)
    delta_lines["delta_pc"] = delta_lines["delta_pu"] * 100

    header_cols = ["carrier", "bus0", "bus1", "lines 1", "lines 2", "delta", "delta_pu", "delta_pc"]
    #LINE COMPARISON DATAFRAME
    delta_lines = delta_lines[header_cols]

    #Compare graph properties
    graph_n1 = n1.graph()
    graph_n2 = n2.graph()

    nodes_n1 = graph_n1.number_of_nodes()
    nodes_n2 = graph_n2.number_of_nodes()
    diff_nodes = abs(nodes_n1 - nodes_n2)
    nodes_data = ["number of nodes", nodes_n1, nodes_n2, diff_nodes]

    edges_n1 = int(graph_n1.number_of_edges())
    edges_n2 = int(graph_n2.number_of_edges())
    diff_edges = abs(edges_n1 - edges_n2)
    edges_data = ["number of edges", edges_n1, edges_n2, diff_edges]

    density_n1 = nx.density(graph_n1)
    density_n2 = nx.density(graph_n2)

    diff_density = abs(density_n1 - density_n2)
    density_data = ["density", density_n1, density_n2, diff_density]

    graph_data = [nodes_data, edges_data, density_data]
    #dataframe to store graph properties of the networks
    graph_df = pd.DataFrame(data = graph_data, columns=["property", "network_1", "network_2", "difference"])

    #GRAPH PROPERTIES DATAFRAME
    print(graph_df)






# Utility function for dataframe to geodataframe conversion
def buses_to_geodf(df_buses, INPUT_CRS=GEO_CRS, OUTPUT_CRS=METRIC_CRS):
    """Function to transform a buses dataframe into a geodataframe with the correct crs."""
    return gpd.GeoDataFrame(
        df_buses,
        geometry=gpd.points_from_xy(df_buses.x, df_buses.y),
        crs=INPUT_CRS,
    ).to_crs(OUTPUT_CRS)

#Create mapping of the networks for comparison purposes¶
#Utility functions for mapping
def shape_mapping(n, options):
    """Create mapping by shape"""
    gdf = gpd.read_file(options["path"])

    # create GADM_ID and country if missing (country_shapes.geojson)
    if "GADM_ID" not in gdf.columns:
        gdf["GADM_ID"] = gdf["name"]
    if "country" not in gdf.columns:
        gdf["country"] = gdf["name"]
    
    gdf.set_index("GADM_ID", inplace=True)
    df_mapped = n.buses.groupby("country").apply(
        lambda x: gpd.sjoin_nearest(buses_to_geodf(x), gdf[gdf.country==x.name].to_crs(METRIC_CRS), how="inner")
    ).droplevel(0, axis=0)
    return (df_mapped["index_right"] + " " + df_mapped.carrier).rename("mapping")


def create_bus_mapping(n, method):
    """Function to create the bus mapping of network n according to a given methodology"""
    match method["method"]:
        case "shape":
            return shape_mapping(n, method["options"])
        case _:
            raise NotImplementedError(f"Method {method['method']} not implemented")



def get_aggregation_strategies(aggregation_strategies):
    """
    Default aggregation strategies that cannot be defined in .yaml format must
    be specified within the function, otherwise (when defaults are passed in
    the function's definition) they get lost when custom values are specified
    in the config.
    """
    import numpy as np

    # to handle the new version of PyPSA.
    try:
        from pypsa.clustering.spatial import _make_consense
    except Exception:
        # TODO: remove after new release and update minimum pypsa version
        from pypsa.clustering.spatial import _make_consense

    bus_strategies = dict(country=_make_consense("Bus", "country"))
    bus_strategies.update(aggregation_strategies.get("buses", {}))

    generator_strategies = {"build_year": lambda x: 0, "lifetime": lambda x: np.inf}
    generator_strategies.update(aggregation_strategies.get("generators", {}))

    return bus_strategies, generator_strategies

# Bus aggregation strategies

def create_clustering(n, busmap, aggregation_strategies=aggregation_strategies):
    # get aggregation strategies
    bus_strategies, generator_strategies = get_aggregation_strategies(aggregation_strategies)

    # get clustering
    clustering = get_clustering_from_busmap(
        n,
        busmap,
        bus_strategies=bus_strategies,
        aggregate_generators_weighted=True,
        aggregate_generators_carriers=None,
        aggregate_one_ports=["Load", "StorageUnit"],
        line_length_factor=1.0,
        generator_strategies=generator_strategies,
        scale_link_capital_costs=False,
    )
    return clustering.network, busmap

def create_clustered_network(n, method):
    return create_clustering(n, create_bus_mapping(n, method))



# utility function
def add_line_names(lines):
    """Prepare line names for comparison"""
    lines["carrier"] = lines.bus0.str.split().str[1]
    lines["name"] = lines.bus0.str.split().str[0] + " - " + lines.bus1.str.split().str[0]

    return lines







