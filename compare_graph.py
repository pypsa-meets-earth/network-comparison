import pypsa
import networkx as nx
import matplotlib.pyplot as plt


def graph_properties(network: pypsa.Network) -> dict:
    """
    Extracts the properties of the network graph.

    Parameters: 
    network: pypsa.Network
    Returns:
    dict: network_properties
    """

    # extract graph properties
    graph = network.graph()
    network_degree = dict(graph.degree())
    network_average_degree_connectivity = nx.average_degree_connectivity(graph)
    network_edges = list(graph.edges())
    network_nodes = list(graph.nodes())
    network_number_of_edges = graph.number_of_edges()
    network_number_of_nodes = graph.number_of_nodes()

    network_properties = {
        "network_edges": network_edges,
        "network_degree": network_degree,
        "network_average_degree_connectivity": network_average_degree_connectivity,
        "network_nodes": network_nodes,
        "network_number_of_edges": network_number_of_edges,
        "network_number_of_nodes": network_number_of_nodes,
    }

    return network_properties


def plot_network_graph(network: pypsa.Network, seed: int = 1969):
    """
    Plots the network graph.

    Parameters: 
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


if __name__ == "__main__":

    # network_path = "elec_s_37.nc"

    # # load network
    # network = pypsa.Network(network_path)
    # network_properties = graph_properties(network)
    # print(f"edges: {network_properties['network_edges']}")
    # print(f"nodes: {network_properties['network_nodes']}")
    # print(
    #     f"degree of connectedness: {network_properties['network_average_degree_connectivity']}")
    # print(f"degree of network: {network_properties['network_degree']}")

    # # plot network graph
    # plot_network_graph(network)
    pass
