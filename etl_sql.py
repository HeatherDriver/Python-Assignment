# etl_sql.py
# -*- coding: utf-8 -*-

# Library imports
from sqlalchemy import Integer
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Float
from collections import OrderedDict


class SQLTableBuilder:
    """
    Serves to further create SQL Lite-ready data through creating a table index, schema and
    dictionary of data to load.
    Input is the list with dict_file from etl_sql.table_to_dict()
    Outputs are (1) Dictionary with table metadata to pass to sqlalchemy's engine.
                (2) Dictionary of table data to load by sqlalchemy.
    """
    # Initiates new constructor
    def __init__(self, dict_file):
        self.dict_file = dict_file

    def _add_index(self):
        """
        Adds an index column to data - hence satisfies unique row requirement to load data
        in sqlalchemy.
        Input:
            No explicit input, uses dict_file passed to object.
        Output:
            converted_idx_list (list) - list containing index dictionary. Will be further added to by _sorted
            function.
        """
        my_idx_list = []
        # Creates dict with index and unique monotonic number
        for i in range(len(self.dict_file)):
            my_idx_list.append({'index': i})

        # Adds index value to data dict
        converted_idx_list = []
        for dict_line, list_line in zip(self.dict_file, my_idx_list):
            dict_line.update(list_line)
            converted_idx_list.append(dict_line)
        return converted_idx_list

    def _sorted(self, _converted_idx_list):
        """
        Further takes converted_idx_list from _add_index function and adds a leading zero to y values in the
        range 1-9. Representing these values as y01 instead of y1 for example, allows columns to be
        correctly sorted. Sorts through use of the OrderedDict.
        Input:
            _converted_idx_list (list) - output of _add_index function.
        Output:
            converted_data (list) - list with sorted dictionary.
        """
        converted_data = []
        for dict_item in _converted_idx_list:
            _dict = {}
            for key, value in dict_item.items():
                # Searches for correct y columns meeting criteria
                if 'y' in key and 'delta' not in key:
                    num = key[1:].split('_')[0]
                    re1, re2 = key[1:].split('_')[1], key[1:].split('_')[2]
                    num = str(num)
                    if len(num) == 1:
                        num = '0' + num
                    y_num = 'y' + num
                    k = '_'.join((y_num, re1, re2))
                else:
                    k = key
                _dict[k] = value
                # Creates the correctly ordered dictionary
                ordered_dict = OrderedDict(sorted(_dict.items()))
            converted_data.append(ordered_dict)
        return converted_data

    def schema_create(self):
        """
        Creates two Dictionaries, 1 with table metadata for engine in sqlalchemy, &
        another with data to load to the above table. Does so by calling the 2 supporting functions
        (_add_index and _sorted).
        Input:
            No explicit input, uses output of index_create
        Output:
            (1) Dictionary with table metadata to pass to sqlalchemy's engine.
            (2) Dictionary of transformed table data to load.
        """
        # Adds the index column
        add_index = self._add_index()
        # Sorts the columns correctly
        sorted_indexed_data = self._sorted(add_index)
        # Accesses the data
        _dict = dict(sorted_indexed_data[0])

        # The 'name' (train, test or ideal) will be used for the table metadata
        key = _dict['name']
        file_name = key.title()

        # Creates the table metadata as a dictionary
        class_dict = dict()
        class_dict["clsname"] = ''.join(('My', file_name, 'Table'))
        class_dict['__tablename__'] = file_name
        class_dict['__table_args__'] = {'extend_existing': True}

        data_to_load = []
        for line in sorted_indexed_data:
            data_d = {}
            # Converts the datatype to align with table's datatype in sqlalchemy
            for key, value in line.items():
                if key == 'index':
                    _ = {key: Column(Integer, primary_key=True, unique=True)}
                elif key == 'num_of_ideal_func':
                    _ = {key: Column(String)}
                elif key == 'name':
                    continue
                else:
                    _ = {key: Column(Float)}
                class_dict.update(_)
                data_d.update({key: value})
            data_to_load.append(data_d)

        return class_dict, data_to_load
