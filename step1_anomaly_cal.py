### Input routine: Step 1 - anomaly calculation ###

## This step can initate step 2 and 3 ##

import netCDF4 as nc
import numpy as np
import time
import subprocess
import os

start_time = time.time()

## Inputs:
esm_list = ['CanESM5', 'CESM2-WACCM','CMCC-CM2-SR5','IPSL-CM6A-LR', 'MPI-ESM1-2-HR']  #np.loadtxt('/work2/ola/input/python/esm_list.txt', dtype=str)    
ssp_list =  ['ssp126','ssp245','ssp370','ssp585']
mean_climate_dir = r'/work2/ola/input/ERA5/grl16_ERA5_mean79-99.nc'
start_year_hist = 1979
end_year_hist = 1999
start_year = 2015
end_year = 2100

calc_mean    = 1    #yes = 1
calc_anomaly = 1     #yes = 1
interpolate  = 1     #yes = 1
bias_corr    = 1     #yes = 1
max_p = 10    # Replace with the desired maximum number of processes // can prob do 10 proc.
nice_level = 10

#------------------------------------------------------------------------------------------------

exe_name = "python3"  # Replace with the actual executable name
processes = []
directory_path = '/work2/ola/input/python/'
os.chdir(directory_path) #Change the working directory
processes = []
print('------ Step 1 - Anomaly calculation -------')


# Anomaly calculation
for esm in esm_list:
    os.makedirs(f'/work2/ola/input/esm_anomaly_global/{esm}/', exist_ok=True)

    # Historic mean
    if calc_mean == 1:
        command = f"python3 mean_argparse.py --esm {esm} --start_hist {start_year_hist} --end_hist {end_year_hist}"       
        subprocess.call(command, shell=True)

    # Anomalies
    if calc_anomaly == 1:
        for ssp in ssp_list:
            for year in np.arange(start_year, end_year+1, 1):
                while len(processes) >= max_p:
                    time.sleep(2)
                    processes = [p for p in processes if p.poll() is None]
                
                command = f"python3 anomaly_argparse.py --esm {esm} --ssp {ssp} --year {year}"
                process = subprocess.Popen(
                    command,
                    shell=True,
                    preexec_fn=lambda: os.nice(nice_level)
                )
                processes.append(process)
                print('Processes running:', len(processes))
                
# Wait for all subprocesses to finish after launching all of them
for process in processes:
    process.wait()


# Start interpolation  (step 2)
if interpolate == 1:
    print('Initiating step 2')
    command1 = f"python3 step2_interpolation.py --esm_list {' '.join(esm_list)}  --ssp_list {' '.join(ssp_list)} --start_year {start_year} --end_year {end_year}"
    subprocess.call(command1, shell=True)

# Start bias correction (step 3)
if bias_corr == 1:
    print('Initiating step 3')
    command2 = f"python3 step3_bias_corr.py --esm_list {' '.join(esm_list)}  --ssp_list {' '.join(ssp_list)} --start_year {start_year} --end_year {end_year} --mcd {mean_climate_dir}"
    subprocess.call(command2, shell=True)
    

end_time = time.time()
tot_time = np.round((end_time - start_time)/60, 1)
print('Total time:', tot_time)
        
