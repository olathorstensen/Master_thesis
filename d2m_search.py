import netCDF4 as nc
import numpy as np


esm_list = np.loadtxt('/work2/ola/input/python/esm_list.txt', dtype=str)
ssp_list = ['historical', '126', '245', '370', '585']
print(esm_list)

for esm in esm_list:
    print(esm)

    for ssp in ssp_list:
        if ssp == "historical":
            source_path = f'/work2/input/climate_data/global_data/CMIP6/{esm}/atmosphere/{esm}_{ssp}_1980.nc'
            df = nc.Dataset(source_path)  
            print(df.variables.keys())
            print(' ')

        else:
            source_path = f'/work2/input/climate_data/global_data/CMIP6/{esm}/atmosphere/{esm}_ssp{ssp}_2060.nc'
            df = nc.Dataset(source_path)  
            print(' ')

