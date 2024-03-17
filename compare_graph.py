import pypsa
import networkx as nx
import matplotlib.pyplot as plt


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


def plot_network_graph(network: pypsa.Network, seed: int = 1969) -> None:
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
    plt.savefig("network_graph.png", dpi=300)
