from google_drive_downloader import GoogleDriveDownloader as gdd
from pathlib import Path
import pypsa
import pandas as pd
import geopandas as gpd
import networkx as nx
from pypsa.clustering.spatial import get_clustering_from_busmap
import numpy as np
import experiments

path_network_1 = "/Users/jessicaryan/Documents/GitHub/network-comparison/scripts/data/pypsa-eur/networks/elec.nc"
path_network_2 = "/Users/jessicaryan/Documents/GitHub/network-comparison/scripts/data/pypsa-earth/networks/elec_s_110.nc"

n1 = pypsa.Network(path_network_1)
n2 = pypsa.Network(path_network_2)

# use_drive enables to download default data from gdrive
# When use_drive is true and the path of the file is not found,
# but it matches a value from dictionary file_ids,
# then the file is downloaded from gdrive
use_gdrive = True  



gadm_shape = "/Users/jessicaryan/Documents/GitHub/network-comparison/scripts/data/pypsa-earth/resources/shapes/gadm_shapes.geojson"
country_shape = "/Users/jessicaryan/Documents/GitHub/network-comparison/scripts/data/pypsa-earth/resources/shapes/country_shapes.geojson"

comparison_methodology = {
    "method": "shape",
    "options": {
        "path": "data/pypsa-earth/resources/shapes/country_shapes.geojson"
    }
}  # method option among: ["country_shape", "gadm_shape", ...]
# TODO: expand to include network_1 and network_2; example: create voronoi polygons and compare them or alike,
# or "find_closest" to compare the closest nodes

# file_ids of default gdrive data
file_ids = {
    # PyPSA-Eur
    "data/pypsa-eur/networks/elec_s_1024.nc": "1GQxNVwpU62YVlWiupFUVMG0Ipu_3UUUd",  # 200Mb!!!
    "data/pypsa-eur/networks/elec_s_512.nc": "1HiOyMzZGA75LfNhFnGU_ntnmjO9CPfEo",
    "data/pypsa-eur/networks/elec_s_256.nc": "1JphEeBz3vdVKY0uKnnHSf-f4k9223emg",
    "data/pypsa-eur/networks/elec.nc": "16DHvFbNah9LblbXOjIbZ6H0cHmCaYH_U",  # % 500Mb!!
    "data/pypsa-eur/networks/base.nc": "1JphEeBz3vdVKY0uKnnHSf-f4k9223emg",
    # PyPSA-Earth
    "data/pypsa-earth/networks/elec_s_110.nc": "12muoaSDkROjTD5cAw143jh3FBPXufNf5",
    "data/pypsa-earth/networks/elec.nc": "1huKiKNutNQgAc8JCIbEuEslENep5YIhG",  # 2Gb!!! jess  
    "data/pypsa-earth/networks/elec_s_150_ec.nc": "13ZMxBz1agQxnvFTYWPLXngmn2j5eIQBe",#jess
    "data/pypsa-earth/networks/elec_s_150.nc": "1e24swFXa0FihVV6W3cM1smVlkny5KtNB",#jess
    "data/pypsa-earth/networks/elec_s.nc": "19fH830mfegOwlpwkZE3m9skfW4Pgt1rA",#jess
    "data/pypsa-earth/networks/base.nc": "19MLCB6Qt5MI_vRyHIUwpv_M8jjNrp-Yi",#jess
    "data/pypsa-earth/networks/elec_s_150_ec_lcopt_3H.nc": "1SUUqcmd9ZvjI08bbIy5iB5HOjyn_0pvP",#jess
    "data/pypsa-earth/resources/shapes/gadm_shapes.geojson": "1DsAn53rTK7Wz6rnga2ogXEnGpXiH5yN4",
    "data/pypsa-earth/resources/shapes/country_shapes.geojson": "1-KxaGSdSXyOlqSfkYNvvJMjZavXQ4Sih",
}

pypsa_eur_network_files = ["data/pypsa-eur/networks/elec_s_1024.nc",
                           "data/pypsa-eur/networks/elec_s_512.nc",
                           "data/pypsa-eur/networks/elec_s_256.nc",
                           "data/pypsa-eur/networks/elec.nc",
                           "data/pypsa-eur/networks/base.nc"]

pypsa_earth_network_files = ["data/pypsa-earth/networks/elec_s_110.nc",
                             "data/pypsa-earth/networks/elec.nc",
                             "data/pypsa-earth/networks/elec_s_150_ec.nc",
                             "data/pypsa-earth/networks/elec_s_150.nc",
                             "data/pypsa-earth/networks/elec_s.nc",
                             "data/pypsa-earth/networks/base.nc",
                             "data/pypsa-earth/networks/elec_s_150_ec_lcopt_3H.nc",
                             "data/pypsa-earth/resources/shapes/gadm_shapes.geojson",
                             "data/pypsa-earth/resources/shapes/country_shapes.geojson"
                             ]
#files_to_download = [gadm_shape, country_shape] + pypsa_earth_network_files + pypsa_eur_network_files


path_network_1 = "./data/pypsa-eur/networks/elec_s_1024.nc"
path_network_2 = "./data/pypsa-earth/networks/elec_s_110.nc"
files_to_download = [path_network_1, path_network_2, gadm_shape, country_shape]


# utility function for gdrive
def download_grive(file_id, dest_path, showsize=False):
    gdd.download_file_from_google_drive(
        file_id=file_id,
        dest_path=dest_path,
        showsize=showsize,
        unzip=False,
    )
    print("dest_path")
    print(dest_path)

for fpath in files_to_download:
    pl_path = Path(fpath)
    
    print(pl_path)

    # skip if file exists
    if pl_path.is_file():
        print(f"File '{fpath}' found")
        continue

    if use_gdrive:
        if fpath in file_ids:
            pl_path.parent.mkdir(parents=True, exist_ok=True)
            download_grive(file_ids[fpath], fpath)
        else:
            print(f"File '{fpath}' not found and not in file_ids")
            raise FileNotFoundError(fpath)
    else:
        print(f"File '{fpath}' not found")
        raise FileNotFoundError(fpath)


#n1 = pypsa.Network(path_network_1)
#n2 = pypsa.Network(path_network_2)
#experiments.run_experiment_for_pair(eur_file, earth_file)
#for pypsa_eur_filepath in pypsa_eur_network_files:
    


