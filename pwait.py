import os
import subprocess
import time
import numpy as np

ssp_list = ['ssp126','ssp245', 'ssp370', 'ssp585']
esm_list = ['ACCESS-CM2']   #np.loadtxt()
start_year = 2015
end_year = 2016

def pwait(process_name, max_processes):
    while count_processes(process_name) >= max_processes:
        time.sleep(60)

def count_processes(process_name):
    try:
        process_count = subprocess.check_output(["pgrep", "-c", process_name], text=True)
        return int(process_count.strip())
    except subprocess.CalledProcessError:
        return 0

def main():
    exe_name = "interpolate16km_argpars.py"  # Replace with the actual executable name
    max_cpus = 4  # Replace with the desired maximum number of processes
    
    for esm in esm_list:
        for ssp in ssp_list:
            for year in np.arange(start_year, end_year +1, 1):
                
                pwait(exe_name, max_cpus)
            
                year_string = "{:04d}".format(year)
                input_file_path = f'/work2/ola/input/esm_global_data/{esm}/{esm}_{ssp}_{year_string}.nc'
                output_file_path = f'/work2/ola/input/esm_interpolated_data/{esm}/{esm}_{ssp}_{year_string}.nc'
            
                command = f"python3 interpolate16km_argpars.py --input {input_file_path} --output {output_file_path}"
                
                subprocess.run(command, shell=True)

if __name__ == "__main__":
    main()
