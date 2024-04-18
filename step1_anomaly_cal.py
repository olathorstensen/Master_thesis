### Input routine: Step 1 - anomaly calculation ###

import netCDF4 as nc
import numpy as np
import time
import subprocess
import os

start_time = time.time()

## Inputs:
esm_list = ['ACCESS-CM2'] #, 'MIROC6','FGOALS-g3'] #]CESM2    #np.loadtxt('/work2/ola/input/python/esm_list.txt', dtype=str)    
ssp_list =  ['ssp126','ssp245'] #,'ssp245', #,'ssp245','ssp370','ssp585'] ['ssp370','ssp585']
start_year_hist = 1979
end_year_hist = 1999
start_year = 2015
end_year = 2100

calc_mean    = 0    #yes = 1
calc_anomaly = 1     #yes = 1
interpolate  = 1     #yes = 1
bias_corr    = 1     #yes = 1
max_p = 10    # Replace with the desired maximum number of processes // can prob do 10 proc.
nice_level = 10

#--------------------------------------------------------------------------------------
exe_name = "python3"  # Replace with the actual executable name
processes = []
directory_path = '/work2/ola/input/python/'
os.chdir(directory_path) #Change the working directory


    
processes = []
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


# Starts interpolation
if interpolate == 1:
    print('Initiating step 2')
    command1 = f"python3 step2_interpolation_pwait.py --esm_list {' '.join(esm_list)}  --ssp_list {' '.join(ssp_list)} --start_year {start_year} --end_year {end_year}"
    subprocess.call(command1, shell=True)

# Starts bias correction
if bias_corr == 1:
    print('Initiating step 3')
    command2 = f"python3 step3_bias_corr.py --esm_list {' '.join(esm_list)}  --ssp_list {' '.join(ssp_list)} --start_year {start_year} --end_year {end_year}"
    subprocess.call(command2, shell=True)
    

end_time = time.time()
tot_time = np.round((end_time - start_time)/60, 1)
print('Total time:', tot_time)
        
