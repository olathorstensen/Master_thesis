import netCDF4 as nc
import numpy as np
import argparse

parser = argparse.ArgumentParser(description='Anomaly calcualtion script.')
parser.add_argument('--esm', type=str, required=True, help='ESM')
parser.add_argument('--start_hist', type=int, required=True, help='Start year historic data')
parser.add_argument('--end_hist', type=int, required=True, help='End year hist data.')


args = parser.parse_args()

esm = args.esm
start_hist = args.start_hist
end_hist = args.end_hist




dims = ['time','latitude','longitude'] #Has to be in correct order
input_vars = ['air_temperature_2m', 'precipitation_flux' ,'relative_humidity_2m', 'swrd', 'lwrd'] #Air temp must be before humidity for unit converion.
yname = 'longitude' # 'xc'  
xname = 'latitude' # 'yc'


#Functions:
def source_path_f(esm, ssp, year): #format: str, str, int
    year_string = "{:04d}".format(year)
    if ssp == 'historical':
        source_path = f'/work2/input/climate_data/global_data/CMIP6/{esm}/atmosphere/{esm}_{ssp}_{year_string}.nc'
    else:
        source_path = f'/work2/ola/input/esm_anomaly_global/{esm}/{esm}_{ssp}_{year_string}.nc'
    return source_path


def output_path_f(esm, ssp, year):
    if ssp == 'historical':
        source_path = f'/work2/ola/input/esm_anomaly_global/{esm}/{esm}_{ssp}_mean.nc'
    else:
        year_string = "{:04d}".format(year)
        source_path = f'/work2/ola/input/esm_anomaly_global/{esm}/{esm}_{ssp}_{year_string}.nc'
    return source_path

def convert_temp(old_values):
    #convert from Kelvin to degC
    new_values = old_values -273.15 
    return new_values

def convert_precip(old_values):
    #convert from kg-m2 -s to mm/day 
    new_values = old_values * (60*60*24)
    return new_values

def convert_humid(rh, temp):
    # Input: temp in degC, rh in %. Output: dew point [C]
    a = 17.625
    b = 243.04
    new_values = b*(np.log(rh/100) + (a*temp/(b+temp))) / (a-np.log(rh/100)-((a*temp)/(b+temp)))
    return new_values

def create_netCDF(output_path, source_path, xname, yname, input_vars):
    # This function works for ERA5 global
    # This function creates a new netCDF file based in input source and the given variables
    # Needs paths, lat/long variable names and 

    source_data = nc.Dataset(source_path)
    result = nc.Dataset(output_path, mode = "w", format = "NETCDF4") #Format is important

    # Copy dimensions from source to output file
    #dims = np.array([])
    for dim in dims:
        result.createDimension(dim, len(source_data.dimensions[dim]))

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
    result.close()
    #print('netCDF-file created:',output_path)





## Create mean year for historic period
source_path = source_path_f(esm, 'historical', start_hist)
output_path = output_path_f(esm, 'historical', start_hist) #Start_year replace with 'mean' when 'historical' is an input
    

create_netCDF(output_path, source_path, xname, yname, input_vars)

source_data = nc.Dataset(source_path, mode='r')
result = nc.Dataset(output_path, mode='a')

year_list = np.arange(start_hist, end_hist+1, 1)
print('Creating historic mean for years: ', year_list)

day_var = np.zeros([len(year_list),len(source_data.dimensions[dims[1]]), len(source_data.dimensions[dims[2]])], dtype=float)

for var in input_vars:
    for i in np.arange(0,365,1):
        for index, item in enumerate(year_list):
            source_path = source_path_f(esm, 'historical', item)
            data = nc.Dataset(source_path)
            day_var[index,:,:] = data[var][i,:,:]

        print('Calculating mean for day', i+1, 'of 365, variable is', var)
        day_var_mean = np.mean(day_var, axis=0)

        if var == 'air_temperature_2m':
            day_var_mean = convert_temp(day_var_mean)
            if i ==0:
                result.variables[var].units = 'degC'

        elif var == 'precipitation_flux':
            day_var_mean = convert_precip(day_var_mean)
            if i ==0:
                result.variables[var].units = 'mm/day'

        elif var == 'relative_humidity_2m':
            result_data = nc.Dataset(output_path, mode='r')
            temp_var = result_data['air_temperature_2m'][i,:,:]
            day_var_mean = convert_humid(day_var_mean, temp_var)
            if i == 0:
                result.variables[var].units = 'degC'

        result.variables[var][i,:,:] = day_var_mean


result.close()
