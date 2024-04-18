
### ERA5 global mean ###


import netCDF4 as nc
import numpy as np


def create_netCDF(output_path, source_path, xname, yname, input_vars):

    # This function works for ERA5 global

    # This function creates a new netCDF file based in input source and the given variables
    # Needs paths, lat/long variable names and 

    source_data = nc.Dataset(source_path)
    print('Source data')
    print(source_data)
    result = nc.Dataset(output_path, mode = "w", format = "NETCDF4") #Format is important


    # Copy dimensions from source to output file
    dims = np.array([])
    for dimname, dim in source_data.dimensions.items():
        result.createDimension(dimname, len(dim))
        dims = np.append(dims,dimname)
    print('dims:' ,dims)
    print(' ')

        # Create time variable
    result.createVariable('time', 'i4', ('time',))
    result.variables['time'][:] = source_data.variables['time'][:]

    #Copy dimension atributes and coordinates from target to output file
    for var in [xname, yname]:
        result.createVariable(var, 'f8', (source_data.variables[var].dimensions))
        result.variables[var][:] = source_data.variables[var][:]
        for attr in source_data.variables[var].ncattrs():
            setattr(result.variables[var], attr, getattr(source_data.variables[var], attr))

  
    #add variables to file and copy its attributes from the source file
    for var in input_vars:
        result.createVariable(var, 'f8', dims)
        for attr in source_data.variables[var].ncattrs():
            if np.logical_and(np.logical_and(attr != '_FillValue', attr != 'scale_factor'), attr != 'add_offset'): #scale factor and offset should not be copied because they lead to incorrect data when using Bessi, we also dont want the Fill Value
                setattr(result.variables[var], attr, getattr(source_data.variables[var], attr))
    print('Result data:')
    print(result)            
    result.close()
    print('netCDF-file created:',output_path)
       
  


#### Input information ###
def source_f(year):
    
    item_string = "{:04d}".format(year)
    source_path = f'/work2/input/climate_data/global_data/ERA5/ERA5_global_{year}.nc'
    return source_path

def output_f(year):
    item_string = "{:04d}".format(year)
    output_path = f'/work2/ola/input/ERA5_global_{year}.nc'
    return output_path

mean_climate = r'/work2/ola/input/hist_mean_ERA5.nc'
start_year = 1979
end_year = 1999
input_vars = ['t2m', 'tp','ssrd', 'strd', 'd2m']
precip = 'tp'  #name of precipitation variable
sw = 'ssrd' #name of shortwave variable
yname = 'lon' # 'xc'  
xname = 'lat' # 'yc'  

output_path = '/work2/ola/input/ERA5_global_mean_79-99.nc'
source_path = source_f(start_year)

create_netCDF(output_path, source_path, xname, yname, input_vars) #Function which creates empty file with var. and attr.


    
###  Calculate average year:

source_data = nc.Dataset(source_path, mode='r')
result = nc.Dataset(output_path, mode='a')

year_list = np.arange(start_year, end_year+1, 1)
print('year list: ', year_list)

dims = np.array([])
for dimname, dim in source_data.dimensions.items():
    dims = np.append(dims,dimname)
    
day_var = np.zeros([len(year_list),len(source_data.dimensions[dims[1]]), len(source_data.dimensions[dims[2]])], dtype=float)


for var in input_vars:
    for i in np.arange(0,365,1):
        for index, item in enumerate(year_list):
            source_path = source_f(item)
            data = nc.Dataset(source_path)
            day_var[index,:,:] = data[var][i,:,:]

        print('Calculating day', i+1, 'of 365 for variable', var)
        day_var_mean = np.mean(day_var, axis=0)
        result.variables[var][i,:,:] = day_var_mean

result.close()
print('Mean climate year:',output_path)
