## Step 2 - Interpolation

import os
import subprocess
import time
import numpy as np
import argparse
"""

print(' ')
print('Step 2 - Interpolation script')

parser = argparse.ArgumentParser(description='Anomaly calcualtion script.')
parser.add_argument('--esm_list', nargs='+', required=True, help='ESMs')
parser.add_argument('--ssp_list', nargs='+', required=True, help='Emmision scenarios')
parser.add_argument('--start_year', type=int, required=True, help='Start year.')
parser.add_argument('--end_year', type=int, required=True, help='End year.')

args = parser.parse_args()

esm_list = args.esm_list
ssp_list = args.ssp_list
start_year = args.start_year
end_year = args.end_year

print(esm_list)
print(ssp_list)
print(start_year)
print(end_year)
"""

ssp_list = ['global']  #['ssp370', 'ssp585']
esm_list = ['ERA5']     #['ACCESS-CM2']   #np.loadtxt()
start_year = 2001
end_year = 2020


    
def main(esm_list, ssp_list, start_year, end_year):
    exe_name = "python3"  # Replace with the actual executable name
    max_p = 10 # Replace with the desired maximum number of processes
    nice_level = 10
    processes = []

    start_time = time.time()
    
    for esm in esm_list:
        os.makedirs(f'/work2/ola/input/{esm}/grl16/', exist_ok=True)
        for ssp in ssp_list:
            for year in np.arange(start_year, end_year +1, 1):
                print(f'Calculating: {esm} {ssp} {year}')
                
                while len(processes) >= max_p:
                    time.sleep(10)
                    processes = [p for p in processes if p.poll() is None]
                                
                year_string = "{:04d}".format(year)
                input_file_path = f'/work2/input/climate_data/global_data/ERA5/{esm}_{ssp}_{year_string}.nc'
                output_file_path = f'/work2/ola/input/ERA5/grl16/grl16_{esm}_{year_string}.nc'
                

                command = f"python3 interpolate16km_argparse.py --input {input_file_path} --output {output_file_path}"

                process = subprocess.Popen(
                    command,
                    shell=True,
                    preexec_fn=lambda: os.nice(nice_level)
                )
                processes.append(process)
                print('Processes running:',len(processes))
                
                
    for process in processes:
        process.wait()

    end_time = time.time()
    tot_time = np.round((end_time - start_time)/60, 1)
    
    print(f'Total runtime: {tot_time} minutes')

if __name__ == "__main__":
    main(esm_list, ssp_list, start_year, end_year)

