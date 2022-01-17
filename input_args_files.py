# input_args_files.py
# -*- coding: utf-8 -*-

# PURPOSE:    This module serves to fulfil 2 criteria:
# (1) Retrieves the input argument provided by the user when running main.py.
# The input argument needs to be the single folder location of the 'train', 'test' and 'ideal' functions
# files, so that the program can continue.

# (2) Module checks that all 3 files are there and correctly named
# after the folder location is inputted.


# Library imports
import argparse
import os
import fnmatch
from pathlib import Path


def get_input_args():
    """
    Retrieves and parses the command line argument provided by the user when running the program from the terminal. 
    Folder is --dir
    Input:
        None - uses argparse module to create and store command line arguments
    Output:
        args - string variable storing command line arguments
    """
    # Instantiates the ArgumentParser object
    parser = argparse.ArgumentParser(description='Provide directory with train, test and ideal functions')

    # Creates command line argument using add_argument() from ArgumentParser object
    # Argument: Datasets directory
    parser.add_argument('--dir', type=str, help='Path to folder with train, test and ideal functions')
    # Parses directory input
    args = parser.parse_args()
    # Retrieves directory
    args = args.dir
    return args

def valid_path_inputted(args):
    """
    Asserts that the path from get_input_args() is a valid one
    Input:
        args (str) - path returned by get_input_args()
    Output:
        None - raises exception if necessary
    """
    # Checks if a valid path has been provided
    path_valid = os.path.exists(args)
    try:
        assert path_valid is True
    except AssertionError:
        print("Please provide a valid path, '" + args + "' is not valid.")

def file_counter(args):
    """
    Checks that there are a valid number of files in inputted folder, and that these are named
    correctly
    Input:
        input_args (str) - path for train, test and ideal files
    Output:
        None - raises exceptions if necessary
    """
    # Creates directory object for iteration
    path_obj = Path(args).iterdir()
    # Instantiates file count dictionary
    file_counts = dict()
    # Searches for csv files named 'train', 'test' and 'ideal'
    for file in path_obj:
        # Strips out the file names from the rest of the folder string
        file_name = str(file).lower()
        base_name = os.path.basename(file_name)

        # Appends to file count dictionary if file name like 'train', 'test' and 'ideal'
        if base_name.endswith('.csv'):
            csv_file_name = base_name.split('.')[0]  # Do not take the file .csv extension
            if fnmatch.fnmatch(csv_file_name, '*train*'):
                file_counts['train'] = file_counts.get('train', 0) + 1
            elif fnmatch.fnmatch(csv_file_name, '*test*'):
                file_counts['test'] = file_counts.get('test', 0) + 1
            elif fnmatch.fnmatch(csv_file_name, '*ideal*'):
                file_counts['ideal'] = file_counts.get('ideal', 0) + 1

    # Checks total file count is 3
    total_files = sum(file_counts.values())
    try:
        assert total_files == 3, 'Incorrect total files: 1 file each for train, test and ideal required'
    except AssertionError as msg:
        print(msg)
    finally:
        # Checks 1 file for each of 'train', 'test' and 'ideal'
        wrong_count = {key: value for (key, value) in file_counts.items() if value != 1}
        if wrong_count:
            print('Incorrect files: files missing or too many files in folder')

def get_file_names(folder):
    """
    Searches the folder for the 3 files (train, test and ideal). If the files have irregular names, will
    search within string to find name.  Checks all 3 files present.
    Input:
        folder (str) - folder containing train, test and ideal
    Output:
        files_folders (dict) - maps train, test and ideal to file path within folder
    """
    files_folders = {}
    for file in Path(folder).iterdir():
        # Strips out the file names from the rest of the folder string
        file_name = str(file).lower()
        base_name = os.path.basename(file_name)
        # Searches for csv files
        if base_name.endswith('.csv'):
            file_name = base_name.split('.')[0]  # Do not take the file .csv extension
            # Searches further for files called train, test and ideal
            if fnmatch.fnmatch(file_name, '*train*'):
                file_name = 'train'
            elif fnmatch.fnmatch(file_name, '*test*'):
                file_name = 'test'
            elif fnmatch.fnmatch(file_name, '*ideal*'):
                file_name = 'ideal'
            _ = {file_name: str(file)}
            files_folders[file_name] = _
    return files_folders
