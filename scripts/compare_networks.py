import pypsa

import merge_networks
def compare_networks():
    n1_filepath = input("filepath of first network: ")
    n2_filepath = input("filepath of second network: ")
    n1 = pypsa.Network(n1_filepath)
    n2 = pypsa.Network(n2_filepath)

    n4 = merge_networks.merge(n1, n2)

    print(n4.components.buses)
