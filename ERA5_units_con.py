### Converts file interpolated from ERA5 global mean to Bessi frendly units

import netCDF4 as nc
import numpy as np

vars = ['t2m','tp','d2m','ssrd', 'strd']

def convert_temp(old_values):
    #convert from Kelvin to degC
    new_values = old_values -273.15 
    return new_values

def convert_precp(old_values):
    #convert from m/s/day to mm/day 
    new_values = old_values *1000 *(60*60*24)
    return new_values

def convert_rad(old_values):
    #convert from J/d to W
    new_values = old_values / (60*60*24) #s/day
    return new_values



folder_path = '/work2/ola/input/ERA5/grl16/'
start_year = 1993
end_year = 2020

for i in np.arange(start_year, end_year+1, 1):
    year = "{:04d}".format(i)
    file_name = f'grl16_ERA5_{year}.nc'
    data_path = folder_path + file_name
    print('Converting units for file:',file_name)
    
    with nc.Dataset(data_path, mode='r+') as dataset:

        for var in vars:
            print('Var is', var)
            variable_data = dataset.variables[var][:]
            if var == 't2m':
                converted_data = convert_temp(variable_data)
                dataset.variables[var][:] = converted_data
                dataset.variables[var].units = 'degC'

            elif var == 'tp':
                converted_data = convert_precp(variable_data)
                dataset.variables[var][:] = converted_data
                dataset.variables[var].units = 'mm/day'

            elif var == 'd2m':
                converted_data = convert_temp(variable_data)
                dataset.variables[var][:] = converted_data
                dataset.variables[var].units = 'degC'
            
            elif var == 'ssrd':
                converted_data = convert_rad(variable_data)
                converted_data = np.where(converted_data < 0, 0, converted_data)
                dataset.variables[var][:] = converted_data
                dataset.variables[var].units = 'W/m2'
            

            else:
                converted_data = convert_rad(variable_data)
                dataset.variables[var][:] = converted_data
                dataset.variables[var].units = 'W/m2'

    ###

    
print("Unit conversion completed.")
