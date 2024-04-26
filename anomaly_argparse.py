import netCDF4 as nc
import numpy as np
import argparse

parser = argparse.ArgumentParser(description='Anomaly calcualtion script.')
parser.add_argument('--esm', type=str, required=True, help='ESM')
parser.add_argument('--ssp', type=str, required=True, help='Emmision scenario')
parser.add_argument('--year', type=int, required=True, help='Current year.')


args = parser.parse_args()

esm = args.esm
ssp = args.ssp
year = args.year


dims = ['time','latitude','longitude'] #Has to be in correct order

# Functions
def source_path_f(esm, ssp, year): #format: str, str, int
    year_string = "{:04d}".format(year)
    source_path = f'/work2/input/climate_data/global_data/CMIP6/{esm}/atmosphere/{esm}_{ssp}_{year_string}.nc'
    return source_path

def output_path_f(esm, ssp, year):
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
    # Eq and const. values: Alduchov and Eskridge (1995)
    a = 17.625 # Water surface. If ice surface: 22.587
    b = 243.04 # Water surface. If ice surface: 273.86 
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

    

    ## Anomaly calculation
hist_data_path = f'/work2/ola/input/esm_anomaly_global/{esm}/{esm}_historical_mean.nc'
hist_data = nc.Dataset(hist_data_path, mode='r')


#Read simuluated data
input_vars = ['air_temperature_2m', 'precipitation_flux','relative_humidity_2m', 'swrd', 'lwrd']
yname = 'longitude' # 'xc'  
xname = 'latitude' # 'yc'
source_path = source_path_f(esm, ssp, year)
output_path = output_path_f(esm, ssp, year)

create_netCDF(output_path, source_path, xname, yname, input_vars) # Create variables with ERA5 name and units

sim_data = nc.Dataset(source_path)
result = nc.Dataset(output_path, mode = "a")


for var in input_vars:
    for i in np.arange(0, 365, 1):
        if var == 'air_temperature_2m':
            day_var = sim_data[var][i,:,:]
            day_var = convert_temp(day_var)
            anomaly = day_var - hist_data[var][i,:,:]
            result.variables[var][i,:,:] = anomaly
            if i == 0:
                result.variables[var].units = 'degC'


        elif var == 'precipitation_flux':
            day_var = sim_data[var][i,:,:]
            day_var = convert_precip(day_var)
            anomaly = day_var / hist_data[var][i,:,:]
            result.variables[var][i,:,:] = anomaly
            if i == 0:
                result.variables[var].units = 'mm/day'

        elif var == 'relative_humidity_2m':
                result_data = nc.Dataset(output_path, mode='r')
                temp_var = sim_data['air_temperature_2m'][i,:,:] - 273.15 #kelvin
                day_var = sim_data[var][i,:,:]
                day_var = convert_humid(day_var, temp_var)
                result.variables[var][i,:,:] = day_var - hist_data[var][i,:,:]
                if i == 0:
                    result.variables[var].units = 'degC'
                    
        else:
            day_var = sim_data[var][i,:,:]
            anomaly = day_var - hist_data[var][i,:,:]
            result.variables[var][i,:,:] = anomaly

hist_data.close()    
sim_data.close()            
result.close()
print('Anomalies calculated for:',esm, ssp, year)

