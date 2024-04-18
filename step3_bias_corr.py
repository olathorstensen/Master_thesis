### Step 3 - Bias correction
import netCDF4 as nc
import numpy as np
import os
import subprocess
import time
import argparse

#Inputs
parser = argparse.ArgumentParser(description='Anomaly calcualtion script.')
parser.add_argument('--esm_list', nargs='+', required=True, help='ESMs')
parser.add_argument('--ssp_list', nargs='+', required=True, help='Emmision scenarios')
parser.add_argument('--start_year', type=int, required=True, help='Start year.')
parser.add_argument('--end_year', type=int, required=True, help='End year.')
parser.add_argument('--mcd', type=str, required=True, help='Mean climate directory path.')

args = parser.parse_args()

esm_list = args.esm_list
ssp_list = args.ssp_list
start_year = args.start_year
end_year = args.end_year
mean_climate_path = args.mcd

print(' ')
print('------- Step 3 - bias correction -------')


max_p = 10 # Replace with the desired maximum number of processes
nice_level = 10

# Bias correction
exe_name = "python3"  # Replace with the actual executable name
processes = []
os.chdir('/work2/ola/input/python/')
    
for esm in esm_list:
    os.makedirs(f'/work2/ola/input/esm_grl16/{esm}/', exist_ok=True)
    for ssp in ssp_list:
        for year in np.arange(start_year, end_year +1, 1):
            print(f'Correcting: {esm} {ssp} {year}')
                
            while len(processes) >= max_p:
                time.sleep(2)                
                processes = [p for p in processes if p.poll() is None]
                                
            year_string = "{:04d}".format(year)
            input_file_path = f'/work2/ola/input/esm_anomaly_interp/{esm}/{esm}_{ssp}_{year_string}.nc'
            output_file_path = f'/work2/ola/input/esm_grl16/{esm}/{esm}_{ssp}_{year_string}.nc'
                

            command = f"python3 bias_cor_argparse.py --input {input_file_path} --output {output_file_path} --mean_climate {mean_climate_path}"

            process = subprocess.Popen(
                command,
                shell=True,
                preexec_fn=lambda: os.nice(nice_level)
            )
            processes.append(process)
            print('Processes running:',len(processes))
                
                
    for process in processes:
        process.wait()
            
 
