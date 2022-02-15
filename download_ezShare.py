#-------------------------------------------------------------------------------
# Name:        ezShare file download tool
# Purpose:	   This software automatically downloads files from a WIFI SD card
#
# Author:      Jonathan D. Müller
#
# Created:     15/02/2022
# Copyright:   (c) Jonathan D. Müller 2022
# Licence:     GPLv3
#-------------------------------------------------------------------------------

import os
import glob
import requests

def list_folders(url):    
    # Download the website with the folder names
    page = requests.get(url).text
    # Create an empty folder list
    folder_list = [ ]
    # Go through and fill the folder list
    for item in page.split("\n"):
        # Find the relevant lines
        if "href=\"dir?dir=A:%5C" in item:
            # Remove obsolete characters
            current_line = item.strip()
            # Define the beginning and end of the folder name
            start = current_line.find("\"> ") + len("\"> ")
            end = current_line.find("</a>")
            # Strip off the unnecessary bits
            current_folder = current_line[start:end]
            # Add to folder_list
            if(current_folder != 'System Volume Information'):
                folder_list.append(current_folder)
    return(folder_list)

def list_files(url, folder):    
    # Download the website with the folder names
    page = requests.get(url + '%5C' + folder).text
    # Create an empty folder list
    file_list = [ ]
    # Go through and fill the folder list
    for item in page.split("\n"):
        # Find the relevant lines
        if "download?file=" in item:
            # Remove obsolete characters
            current_line = item.strip()
            # Define the beginning and end of the file name
            start = current_line.find("\"> ") + len("\"> ")
            end = current_line.find("</a>")
            # Strip off the unnecessary bits
            current_file = current_line[start:end]
            # Add to file_list
            file_list.append(current_file)
    return(file_list)

# Checks if the file already exists. Returns false if yes
def does_file_exist(out_folder, file_folder, file):
    # Check if output folder exists
    if(not os.path.exists(out_folder + file_folder)): # make directory if it doesn't exist
        os.makedirs(out_folder + file_folder)
    files_with_path = glob.glob(out_folder + '/' + file_folder + '/' + '*')
    # Remove the folder path to check
    files_no_path   = list(map(lambda x: x.replace(out_folder + '/' + file_folder + '\\',''), files_with_path))
    if(file in files_no_path):
        return(True)
    else:
        return(False)

def check_download(out_folder, folder, file, overwrite=False):
    # Create download url
    download_url = 'http://192.168.4.1/download?file=' + folder + '%5C' + file
    #print('Download', folder + '/' + file)
    #print(' ', folder, file, download_url)
    # If file doesn't exist locally, download it
    file_exists = does_file_exist(out_folder, folder, file)
    #print('  File exists: ', file_exists)
    #print('  Overwrite:   ', overwrite)
    if((~overwrite & file_exists)):
        print('Exists (Don\'t download)')
    else:
        print('Download')
        download_file(out_folder + '/' + folder + '/', file, download_url)
    pass

def download_file(out_folder, out_file, url):
    local_fn = out_folder + '/' + out_file
    r = requests.get(url)
    f = open(local_fn, 'wb')
    for chunk in r.iter_content(chunk_size=512 * 1024): 
        if chunk: # filter out keep-alive new chunks
            f.write(chunk)
    f.close()
    pass

def download_all(sd_url, out_folder, last_folder=False, overwrite=False):
    print('Download ALL files (Overwrite existing files)') if overwrite else print('Download only NEW files')
    # The last folder contains data of the current day that is still measurring
    # It's better not to download it
    if(last_folder):
        folder_list = list_folders(sd_url)
    else:
        folder_list = list_folders(sd_url)[:-1]
    # Now cycle through the folders, and check if the files exist
    for folder in folder_list:
        print('  ' + folder)
        file_list = list_files(sd_url, folder)
        for file in file_list:
            print('    ' + file + ': ', end='')
            check_download(out_folder, folder, file, overwrite=overwrite)
    print('All done...')
    
# Run the program
if __name__ == "__main__":
    # Initialisation/Variables
    sd_url = 'http://192.168.4.1/dir?dir=A:'
    output_folder = 'downloaded/'
    # Download all the files
    download_all(sd_url, output_folder)