import pypsa
import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm


def graph_properties(network: pypsa.Network) -> dict:
    """
    Extracts various properties of the provided PyPSA network object.

    Args:
        network (pypsa.Network): The PyPSA network object to analyze.

    Returns:
        dict: A dictionary containing the extracted network properties.
    """

    # Get the underlying NetworkX graph object from the PyPSA network
    graph = network.graph()

    # Extract degree information for each node (node and its connected edges)
    network_degree = dict(graph.degree())

    # Calculate the average degree of connectivity in the network
    network_average_degree_connectivity = nx.average_degree_connectivity(graph)

    # Extract a list of edges and nodes from the NetworkX graph
    network_edges = list(graph.edges())
    network_nodes = list(graph.nodes())

    # Get the total number of edges and nodes in the network
    network_number_of_edges = graph.number_of_edges()
    network_number_of_nodes = graph.number_of_nodes()

    # Create a dictionary to store the extracted network properties
    network_properties = {
        "network_edges": network_edges,
        "network_degree": network_degree,
        "network_average_degree_connectivity": network_average_degree_connectivity,
        "network_nodes": network_nodes,
        "network_number_of_edges": network_number_of_edges,
        "network_number_of_nodes": network_number_of_nodes,
    }

    return network_properties


def plot_network_graph(network: pypsa.Network, seed: int = 1969, fl_id: str = "") -> None:
    """
    Plots the network graph.

    Args:
        network: pypsa.Network
    Returns:
        None
    """
    graph = network.graph()
    options = {"node_color": "black", "node_size": 50,
               "linewidths": 0, "width": 0.1}
    pos = nx.spring_layout(graph, seed=seed)  # Seed for reproducible layout
    nx.draw(graph, pos, **options)
    plt.savefig("network_graph" + fl_id + ".png", dpi=300)

def generate_pallette(orig_cm_map=plt.cm.Reds, custom_name="myreds",
    a0=0.25, a1=0.8, n=10) -> mcolors.LinearSegmentedColormap:
    """
    """ 
    mycolors = orig_cm_map(np.linspace(a0, a1, n))  
    mycmap = mcolors.LinearSegmentedColormap.from_list("mycmap", mycolors)
    return mycmap

def add_color_col(df: pd.DataFrame, col: str, 
    col_map: mcolors.LinearSegmentedColormap) -> pd.DataFrame:
    """
    """
    s_norm = mcolors.Normalize(
        vmin=df[col].dropna().min(),
        vmax=df[col].dropna().max(),
        clip=False
    )
    s_mapper = cm.ScalarMappable(norm=s_norm, cmap=col_map)
    df[col].fillna(value=0, inplace=True)
    df[col + "_color"] = df[col].apply(
        lambda x: "gray" if x == 0 else s_mapper.to_rgba(x)
    )
    return df

def plot_network_graph_el(network: pypsa.Network,
    seed: int = 1969, fl_id: str = "", color_gen=False) -> None:
    """
    Plots the network graph.

    Args:
        network: pypsa.Network
    Returns:
        None
    """
    graph = network.graph()

    # custom pallettes are used to avoid bland colors 
    mycmap_red = generate_pallette(
        orig_cm_map=plt.cm.Reds,
        custom_name="mycmap_red",
        a0=0.45, a1=0.95, n=10
    )
    mycmap_green = generate_pallette(
        orig_cm_map=plt.cm.Greens,
        custom_name="mycmap_green",
        a0=0.5, a1=0.9, n=10
    )

    s_df = network.lines[["s_nom", "length", "num_parallel"]]
    s_df["s_lines"] = network.lines.eval("s_nom * length * num_parallel")    
    s_df = add_color_col(df=s_df, col="s_lines", col_map=mycmap_green)      

    if color_gen:
        p_gen = network.generators[["bus", "p_nom"]].groupby(["bus"]).sum() 
    else:
        p_load = network.loads_t.p_set.sum(axis=0)
        p_load.name = "node_load"
        load_df = network.buses.join(p_load, how="left")
        load_df = add_color_col(df=load_df, col="node_load", col_map=mycmap_red)
        node_color = load_df.node_load_color.values

    options = {
        "node_color": node_color,
        "node_size": 20,
        "linewidths": 0.1,
        "edge_color": s_df.s_lines_color.values,      
        "width": 2
    }
    pos = nx.spring_layout(graph, seed=seed)
    nx.draw(graph, pos, **options)
    plt.savefig("network_graph_el" + fl_id + ".png", dpi=300)    
