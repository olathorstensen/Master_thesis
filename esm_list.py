import os

### Function to make list of directories in ESM folder

def list_files_in_directory(directory):
    file_list = []
    # Iterate over files and directories in the specified directory
    for item in os.listdir(directory):

        if os.path.isdir(os.path.join(directory, item)):
            # If it's a directory, you can choose to do something else
            file_list.append(item)
    return file_list

# Specify the directory path
directory_path = '/work2/input/climate_data/global_data/CMIP6/'

# Call the function to get the list of files
files_in_directory = list_files_in_directory(directory_path)

output_file_path = '/work2/ola/input/python/esm_list.txt'

with open(output_file_path, 'w') as output_file:
    for file_name in files_in_directory:
        output_file.write(file_name + '\n')

print("File names exported to:", output_file_path)

