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


def available_item_properties(network1: pypsa.Network, network2: pypsa.Network, item: str) -> list:
    """
    Identifies items present in both network1 and network2 for the specified item type.

    Args:
        network1 (pypsa.Network): The first network to compare.
        network2 (pypsa.Network): The second network to compare.
        item (str): The type of item to check for availability, either "network_nodes" or "network_edges".

    Returns:
        list: A list of items present in both network1 and network2.
    """

    if item not in ["network_nodes", "network_edges"]:  # Validate item type
        raise ValueError(
            "Invalid item type. Must be 'network_nodes' or 'network_edges'.")

    available_item = []  # Initialize a list to store common items

    # Iterate through items in network1 and check for presence in network2
    for idx in network1[item]:
        if idx in network2[item]:
            available_item.append(idx)

    return available_item


def missing_item_properties(network1: pypsa.Network, network2: pypsa.Network, item: str) -> list:
    """
    Identifies items present in network1 but missing in network2 for the specified item type.

    Args:
        network1 (pypsa.Network): The first network to compare.
        network2 (pypsa.Network): The second network to compare.
        item (str): The type of item to check for missing entries, either "network_nodes" or "network_edges".

    Returns:
        list: A list of items present in network1 but missing in network2.
    """

    if item not in ["network_nodes", "network_edges"]:  # Validate item type
        raise ValueError(
            "Invalid item type. Must be 'network_nodes' or 'network_edges'.")

    missing_item = []  # Initialize a list to store missing items

    # Iterate through items in network1 and identify those missing in network2
    for idx in network1[item]:
        if idx not in network2[item]:
            missing_item.append(idx)

    return missing_item


def compare_graph_properties(network1: pypsa.Network, network2: pypsa.Network) -> dict:
    """
    This function compares the properties of two PyPSA network objects.

    Args:
            network1 (pypsa.Network): The first network to compare.
            network2 (pypsa.Network): The second network to compare.

    Returns:
            dict: A dictionary containing the similarities and differences between the networks.
    """

    network1_properties = graph_properties(
        network1)  # Get properties of network 1
    network2_properties = graph_properties(
        network2)  # Get properties of network 2

    difference_dict = {}  # Dictionary to store property differences
    similar_dict = {}     # Dictionary to store property similarities

    results = {
        "similarities": similar_dict,
        "differences": difference_dict
    }

    # Find common properties (edges & nodes) present in both networks
    similar_dict["edges"] = available_item_properties(
        network1_properties, network2_properties, "network_edges")
    similar_dict["nodes"] = available_item_properties(
        network1_properties, network2_properties, "network_nodes")

    # Calculate the absolute difference in the number of edges and nodes
    difference_dict["edge_difference"] = abs(
        network1_properties["network_number_of_edges"] - network2_properties["network_number_of_edges"])
    difference_dict["node_difference"] = abs(
        network1_properties["network_number_of_nodes"] - network2_properties["network_number_of_nodes"])

    # Find missing edges (those in network 1 but not in network 2 and vice versa)
    edges_in_n1_not_in_n2 = missing_item_properties(
        network1_properties, network2_properties, "network_edges")
    edges_in_n2_not_in_n1 = missing_item_properties(
        network2_properties, network1_properties, "network_edges")

    # Find missing nodes (those in network 1 but not in network 2 and vice versa)
    nodes_in_n1_not_in_n2 = missing_item_properties(
        network1_properties, network2_properties, "network_nodes")
    nodes_in_n2_not_in_n1 = missing_item_properties(
        network2_properties, network1_properties, "network_nodes")

    difference_dict["edges_in_n1_not_in_n2"] = edges_in_n1_not_in_n2
    difference_dict["edges_in_n2_not_in_n1"] = edges_in_n2_not_in_n1
    difference_dict["nodes_in_n1_not_in_n2"] = nodes_in_n1_not_in_n2
    difference_dict["nodes_in_n2_not_in_n1"] = nodes_in_n2_not_in_n1

    degree = {}  # Dictionary to store degree information

    # Calculate average degree for each network
    average_network_degree = pd.DataFrame([network1_properties["network_average_degree_connectivity"],
                                           network2_properties["network_average_degree_connectivity"]], index=["network_1", "network_2"]).T
    degree["average_degree"] = average_network_degree.sort_index(inplace=True)

    # Combine degree information for both networks into a DataFrame
    network_degree = pd.DataFrame(
        [network1_properties["network_degree"], network2_properties["network_degree"]]).T
    network_degree.rename(
        columns={"0": "network_1", "1": "network_2"}, inplace=True)

    difference_dict["degree"] = {
        "network_degree": network_degree,
        "average_network_degree": average_network_degree
    }

    return results
