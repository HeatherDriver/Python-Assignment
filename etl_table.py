# etl_table.py
# -*- coding: utf-8 -*-

# PURPOSE:    This module serves to run file data munging from raw to SQL Lite-ready.
# Files are read into dictionaries, their file names are added, strings are converted to float,
# y columns are renamed according to the file name.


# Library imports
import csv
import re


class TableConverter:
    """
    Executes data validation and munging of input data, to create dictionary passed to etl SQLTableBuilder object.
    Input is the dict_file from input_args_files.get_file_names()
    Output is the converted_data list containing final dataset dictionary of {transformed column name : data value}.
    """

    # Initiates new constructor
    def __init__(self, dict_file):
        self.dict_file = dict_file

    def _csv_to_dict(self):
        """
        Creates csv_reader dictionary object from csv.
        Appends the file name ('train', 'test' or 'ideal') in dictionary - e.g. 'name' : 'ideal'.
        Input:
            No explicit func input.
            dict_file from input_args_files.get_file_names() is used in class constructor.
        Output:
            my_list (list) - list with csv_reader dictionary contained.
        """
        for file_name, file_path in self.dict_file.items():
            # Reading in the file
            my_list = []
            with open(file_path) as csv_file:
                csv_reader = csv.DictReader(csv_file)
                # Converts the csv to a dict & appends file name (train, ideal or test)
                for rows in map(dict, csv_reader):
                    rows.update({'name': file_name})
                    my_list.append(rows)
            return my_list

    def _col_name_check(self, _csv_to_dict):
        """
        Checks columns are (x, name, y), or if y that a func number is appended.
        Input:
            _csv_to_dict (list) - output of func _csv_to_dict, take index [0].
            I.e. _csv_to_dict = self._csv_to_dict()[0]
        Output:
            _csv_to_dict (list) - _csv_to_dict validated.
        """
        col_names = ['x', 'y', 'name']
        for key in _csv_to_dict.keys():
            # Validates column names, checks that 'y' columns have a digit
            if key not in col_names:
                try:
                    assert re.match('y\d+', key)
                except AssertionError:
                    raise AssertionError('Invalid column name')
        return self._csv_to_dict()

    def _cast_string_to_float(self, _col_name_check):
        """
        Casts dictionary values to float datatype, raises error for invalid values.
        Input:
            _col_name_check (list) - _csv_to_dict validated.
        Output:
            my_list (list) - _csv_to_dict with validated values and strings recast to float.
        """
        my_list = []
        for line in _col_name_check:
            _ = {}
            for key, val in line.items():
                # Keeps column as string if called 'name' (contains file name), else casts to float datatype
                if key == 'name':
                    _[key] = val
                else:
                    try:
                        _[key] = float(val)
                    except ValueError:
                        raise ValueError('Invalid data: {} not float or integer'.format(val))
            my_list.append(_)
        return my_list

    def _create_column_keys(self, _cast_string_to_float):
        """
        Creates mapping for each existing column name, to new column name with file name and 'func'
        appended.
        Input:
            _cast_string_to_float (list) - output of _cast_string_to_float.
        Output:
            _key_lookups (dict) - maps existing column name to new name.
        """
        _key_lookups = dict()
        for key in _cast_string_to_float[0].keys():
            # Maps existing column names to their transformed names
            if 'y' in key:
                _key_lookups[key] = '_'.join((key, _cast_string_to_float[0]['name'], 'func'))
            else:
                _key_lookups[key] = key
        return _key_lookups

    def table_to_dict(self):
        """
        Executes supporting functions.
        Renames columns to derived column names - e.g. y2 -> y2_training_func
        Input:
            None
        Output:
            converted_data (list) - list contains cleaned, validated data with renamed columns
        """
        # Converts csv to dictionary object
        csv_to_dict = self._csv_to_dict()
        # Checks column naming according to criteria
        col_name_check = self._col_name_check(csv_to_dict[0])
        # Casts data values to float
        cast_string_to_float = self._cast_string_to_float(col_name_check)
        # Creates renamed column mapping dictionary
        key_lookups = self._create_column_keys(cast_string_to_float)
        # Creates new dictionary object with correctly named columns and float data
        converted_data = []
        for line in cast_string_to_float:
            my_dict = dict()
            for key, value in key_lookups.items():
                my_dict.update({value: line[key]})
            converted_data.append(my_dict)
        return converted_data
