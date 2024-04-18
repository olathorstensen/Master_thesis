import netCDF4 as nc
import numpy as np
import scipy.interpolate as sp
import xarray as xr
import argparse

parser = argparse.ArgumentParser(description='Interpolation script.')
parser.add_argument('--input', type=str, required=True, help='Input file path.')
parser.add_argument('--output', type=str, required=True, help='Output file path.')

args = parser.parse_args()



#where to save result
output_path = args.output

#load target grid on which to interpolate
target_grid_path = '/work2/trieckh/ice_data/Greenland/GRL-16KM/GRL-16KM_TOPO-M17.nc'
target_grid = nc.Dataset(target_grid_path, mode = 'r')

#load source data to be interpolated
source_data_path = args.input
source_data = nc.Dataset(source_data_path)

#specify list of which variables to interpolate
input_vars = ['air_temperature_2m', 'precipitation_flux' ,'relative_humidity_2m', 'swrd', 'lwrd']

time_dim = True #True if variables that should be interpolated have a time dimension

#choose which timestep to interpolate
choose_step = -1 #-1 to interpolate all steps

#coordinate names
target_xname = 'lon2D'
target_yname = 'lat2D'

source_xname = 'longitude'
source_yname = 'latitude'

#output format
output_format = "NETCDF3_CLASSIC"

#create new file for the interpolated data
result = nc.Dataset(output_path, mode = "w", format = output_format)

#check if time dimension is needed, if so, create time dimension and variable
if np.logical_and(time_dim, choose_step == -1):
    result.createDimension('time', None)
    result.createVariable('time', 'i4', ('time'))
    time_steps = len(source_data.variables['time'])
    dims = np.array(['time',list(target_grid.variables[target_xname].dimensions)[0], list(target_grid.variables[target_xname].dimensions)[1]]) # create list of Dimensions the interpolated variable should have. The dimensions have to be defined in the same order as for the target coordinate variables.
else:
    time_steps = 1
    dims = list(target_grid.variables[target_xname].dimensions)[:]

#copy the dimensions of the target grid into the new file
for dim in list(target_grid.dimensions.keys()):
    result.createDimension(dim, len(target_grid.dimensions[dim]))

#copy the variables of the target grid into the new file
for var in [target_xname, target_yname]:
    result.createVariable(var, 'f8', (target_grid.variables[var].dimensions))
    result.variables[var][:] = target_grid.variables[var][:]
    for attr in target_grid.variables[var].ncattrs():
        setattr(result.variables[var], attr, getattr(target_grid.variables[var], attr))

#add variable that should be interpolated to the output file and copy its attributes from the source file
for var in input_vars:
    result.createVariable(var, 'f8', dims)
    for attr in source_data.variables[var].ncattrs():
        if np.logical_and(np.logical_and(attr != '_FillValue', attr != 'scale_factor'), attr != 'add_offset'): #scale factor and offset should not be copied because they lead to incorrect data when using Bessi, we also dont want the Fill Value
            setattr(result.variables[var], attr, getattr(source_data.variables[var], attr))

#create 2D array with koordinates of source data and crop off data that lies outside of the region of the target grid
target_x_style_change = 0 # marks if the definition of the x coordinates has been changed
target_x = target_grid.variables[target_xname][:]
if np.max(target_x) > 180:
    target_x[target_x > 180] = target_x[target_x > 180] - 360
    target_x_style_change = 1
#min and max values for x and y
xmin = np.min(target_x) -2 #keep in mind that the data for greenland overlaps with the Meridian
xmax = np.max(target_x) +2
ymin = np.min(target_grid.variables[target_yname][:]) -2 #+/- 2 in order to not cut the data off too close
ymax = np.max(target_grid.variables[target_yname][:]) +2

x = source_data.variables[source_xname][:]
if np.max(x) > 180:
    x[x > 180] = x[x > 180] - 360
y = source_data.variables[source_yname][:]

#Masks to identify which data points lie within the area of the target grid
selected_indices_x = np.logical_and(x >= xmin, x <= xmax) 
selected_indices_y = np.logical_and(y >= ymin, y <= ymax)

source_coordinates = np.zeros((np.sum(selected_indices_x) * np.sum(selected_indices_y), 2))

X,Y = np.meshgrid(x[selected_indices_x], y[selected_indices_y])

if target_x_style_change:
    X[X < 0] = X[X < 0] + 360 # makes sure the source x coordinates and the target x coordinates are defined in the same way ((0,360) or (-180,180))

source_coordinates[:,0] = np.ndarray.flatten(X)
source_coordinates[:,1] = np.ndarray.flatten(Y)

#create 2D array with coordinates of the target grid
nx = np.shape(result.variables[target_xname][:])[0]
ny = np.shape(result.variables[target_xname][:])[1]

target_coordinates = np.zeros((nx * ny, 2))
target_coordinates[:,0] = np.ndarray.flatten(result.variables[target_xname][:])
target_coordinates[:,1] = np.ndarray.flatten(result.variables[target_yname][:])

#function to create a data array of the right shape and interpolate the data
def interp(var, time_step, source_data_values):
    #create 1D array with values of the source data
    '''
    if time_dim:
        if choose_step == -1:
            source_data_values = np.ndarray.flatten(source_data.variables[var][:][time_step,selected_indices_y,:][:,selected_indices_x])
        else:
            source_data_values = np.ndarray.flatten(source_data.variables[var][:][choose_step,selected_indices_y,:][:,selected_indices_x])
    else:
        source_data_values = np.ndarray.flatten(source_data.variables[var][:][selected_indices_y,:][:,selected_indices_x])
    '''
#interpolate with scipy.interpolate.griddata
    data_interp = sp.griddata(source_coordinates, source_data_values, target_coordinates, method = 'linear', fill_value = 10e+30) #fill_value is set very large so missing points can be easily identified

#reshape the interpolated data into a 2D array
    data_interp_2D = np.reshape(data_interp, (nx, ny))
    
#check for missing values and approximate them by taking the mean of the nearest neighbours that are not missing

    missing = np.argwhere(data_interp_2D == 10e+30)
    for i in np.arange(0, np.shape(missing)[0], 1):
        missing_neighbours = data_interp_2D[missing[i,0]-1:missing[i,0]+2:1, missing[i,1]-1:missing[i,1]+2:1]
        data_interp_2D[missing[i,0],missing[i,1]] = np.mean(missing_neighbours[missing_neighbours != 10e+30])
       
#save the interpolated data in the output file
    if np.logical_and(time_dim, choose_step == -1):
        result.variables[var][time_step,:,:] = data_interp_2D
    else:
        result.variables[var][:] = data_interp_2D


#interpolate the data for each time step for each specified variable

if time_dim:
    if choose_step == -1:
        for var in input_vars:
            for time_step in np.arange(0, time_steps, 1):
                #print(var,' timestep: ', time_step)
                source_data_values = np.ndarray.flatten(source_data.variables[var][:][time_step,selected_indices_y,:][:,selected_indices_x])
                interp(var, time_step, source_data_values)
    else:
        for var in input_vars:
            #print(var,' timestep: ', choose_step)
            source_data_values = np.ndarray.flatten(source_data.variables[var][:][choose_step,selected_indices_y,:][:,selected_indices_x])
            interp(var, 0, source_data_values)
else:
    for var in input_vars:
        #print(var)
        source_data_values = np.ndarray.flatten(source_data.variables[var][:][selected_indices_y,:][:,selected_indices_x])
        interp(var, 0, source_data_values)
'''
for var in input_vars:
    for time_step in np.arange(0, time_steps, 1):
        print(var,' timestep: ', time_step)
        interp(var, time_step)
'''            

print('Interpolation complete')
print(output_path)
print('nx = ', nx)
print('ny = ', ny)


