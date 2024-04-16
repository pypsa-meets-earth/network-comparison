from venv import logger
import pypsa
import match_buses


def merge(network1, network2) -> pypsa.Network:
    rename_duplicated_items(network1, network2)
    busmap = match_buses.get_busmap(network1, network2)

    network3 = add_components(network1, network2)
    for bus in network3.components.buses.index:
        b = str(bus)
        if b not in busmap.keys():
            busmap[b] = b
    network3.buses = network3.buses.drop("country",axis=1)
    network3.buses = network3.buses.drop("carrier",axis=1)
    clustering = pypsa.clustering.spatial.get_clustering_from_busmap(network3, busmap, with_time=False)

    return clustering.network


def add_components(network_1, network_2) -> pypsa.Network:
    to_skip = ["Network"]
    if network_2.srid != network_1.srid:
        logger.warning(
            f"Warning: spatial Reference System Indentifier {network_2.srid} for new network not equal to value {network_1.srid} of existing network. Original value will be used."
        )
    snapshots_aligned = network_1.snapshots.equals(network_2.snapshots)
    weightings_aligned = network_1.snapshot_weightings.equals(network_2.snapshot_weightings)
    assert (
                snapshots_aligned and weightings_aligned), "Error, snapshots or snapshot weightings do not agree, cannot add network with time-varying attributes."

    new_network = network_1

    for component in network_2.iterate_components(network_2.components.keys() - to_skip):
        # we do not add components whose ID is present in this network
        index_list = list(
            set(component.df.index) - set(network_1.df(component.name).index)
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
            new_network.import_series_from_dataframe(df_to_add, component.name, attr)

        return new_network


def update_component_name(network, component_name, new_value, old_value):
    # update name in static dataframe for this component
    network.df(component_name).rename(index={old_value: new_value}, inplace=True)

    list_name = component_name.lower()
    # update name in static dataframes of other components
    for component in network.iterate_components():
        if list_name in list(component.df.keys()):
            component.df.get(list_name).replace({old_value: new_value}, inplace=True)

    # update name in time-varying dataframes of this component (if any exist)
    if network.pnl(component_name):
        for k, v in network.pnl(component_name).items():
            network.pnl(component_name).get(k).rename(columns={old_value: new_value}, inplace=True)

    # special case where a bus name is changed - requires special treatment
    if component_name == "Bus":
        for component in network.iterate_components():
            if "bus" in list(component.df.keys()):
                component.df.get("bus").replace({old_value: new_value}, inplace=True)
            if "bus0" in list(component.df.keys()):
                component.df.get("bus0").replace({old_value: new_value}, inplace=True)
            if "bus1" in list(component.df):
                component.df.get("bus1").replace({old_value: new_value}, inplace=True)


# rename any component in network1 such that there is a component (of the same type) in network2 with the same name
def rename_duplicated_items(network1, network2):
    for component in network1.iterate_components():
        n1_component_index = component.df.index
        n2_component_index = network2.df(component.name).index
        for comp1 in n1_component_index:
            for comp2 in n2_component_index:
                if comp1 == comp2:
                    update_component_name(network1, component.name, comp1 + "_n1", comp1)
                    continue
