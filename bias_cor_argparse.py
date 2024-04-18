### Step 3.1 - Bias correction_argparse

import netCDF4 as nc
import numpy as np
import os
import argparse

parser = argparse.ArgumentParser(description='Interpolation script.')
parser.add_argument('--input', type=str, required=True, help='Input file path.')
parser.add_argument('--output', type=str, required=True, help='Output file path.')
parser.add_argument('--mean_climate', type=str, required=True, help='Refrence climate path.')

args = parser.parse_args()

source_path = args.input
output_path = args.output
mean_climate_path = args.mean_climate



def create_netCDF(output_path, source_path, xname, yname, input_vars):

# This function creates a new netCDF file based in input source and the given variables
# Needs paths, lat/long variable names and 

    source_data = nc.Dataset(source_path)

    # Create new netCDF file
    result = nc.Dataset(output_path, mode="w", format="NETCDF3_CLASSIC")

    # Copy dimensions from source to output file
    for dimname, dim in source_data.dimensions.items():
        result.createDimension(dimname, len(dim))

    # Create time variable
    result.createVariable('time', 'i4', ('time',))
    result.variables['time'][:] = source_data.variables['time'][:]

    # Copy coordinate variables
    for varname in [xname, yname]:
        var = source_data.variables[varname]
        result.createVariable(varname, var.dtype, var.dimensions)
        result.variables[varname][:] = var[:]

        # Copy variable attributes
        for attrname in var.ncattrs():
            result.variables[varname].setncattr(attrname, var.getncattr(attrname))

    # Copy input variables
    for varname in input_vars:
        var = source_data.variables[varname]
        result.createVariable(varname, var.dtype, var.dimensions)

        # Copy variable attributes (excluding _FillValue, scale_factor, and add_offset)
        for attrname in var.ncattrs():
            if attrname not in ['_FillValue', 'scale_factor', 'add_offset']:
                result.variables[varname].setncattr(attrname, var.getncattr(attrname))

        # Copy variable data
        result.variables[varname][:] = var[:]
       
       
  
    # Close the netCDF files
    source_data.close()
    result.close()

    #print('netCDF-file created')



yname = 'lon2D' # 'xc'  
xname = 'lat2D' # 'yc'  

input_vars = ['air_temperature_2m', 'precipitation_flux' ,'relative_humidity_2m', 'swrd', 'lwrd']
output_vars = ['t2m', 'tp', 'd2m', 'ssrd', 'strd']

create_netCDF(output_path, mean_climate_path, xname, yname, output_vars) #Function which creates empty file with var. and attr.

hist_data = nc.Dataset(mean_climate_path)
sim_data = nc.Dataset(source_path, mode = 'r+')
result = nc.Dataset(output_path, mode = "a")


for index, item in enumerate(input_vars):
    for i in np.arange(0, 365, 1):
        if item == 'precipitation_flux':
            anomaly = sim_data[item][i,:,:]
            mean = hist_data[output_vars[index]][i,:,:]
            result.variables[output_vars[index]][i,:,:] = mean * anomaly
        else:
            anomaly = sim_data[item][i,:,:]
            mean = hist_data[output_vars[index]][i,:,:]
            result.variables[output_vars[index]][i,:,:] = mean + anomaly

result.close()
sim_data.close()

print('File done:', output_path)
