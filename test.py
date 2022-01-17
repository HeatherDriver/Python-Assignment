# test.py
# -*- coding: utf-8 -*-

# PURPOSE:    This module creates the main test dataframe ('mapped_fns_df'). This is constructed
# by determining the deviation per test point and identifying whether it lies within the upper or
# lower boundaries of the training data.

# This is then used within other applications:
# (1) Dictionary to pass the data and mapping to sqlalchemy.
# (2) Unmapped functions (both overall and for each of the 4 ideal functions, and within range).
# (3) Summary results - reports the proportion of points mapped at each square root


# Library imports
import pandas as pd

# Imports own module
from train import TrainFunctionReturner
from arithmetic import calc_diff


class TestFunctionReturner(TrainFunctionReturner):
    """
    Creates the main mapped functions dataframe ('mapped_fns_df') and extensions:
        (1) mapped_fns_dict       - dictionary of mapped functions dataframe for use by sqlalchemy.
        (2) unmapped_fns          - dataframe of unmapped points for each of the four ideal functions.
        (3) unmapped_fns_set      - all unmapped points overall -> passed to further analysis (unmapped module).
        (4) unmapped_fns_in_range - dataframe of unmapped points existing within function's  upper and lower range.
        (5) summary_results_df    - dataframe summarising statistics for mapped and unmapped points.
    """
    # Initiates new constructor
    def __init__(self, train_df, ideal_df, test_df, sq_root_number):
        # Calls parent's (TrainFunctionReturner) constructor
        super().__init__(train_df, ideal_df, sq_root_number)
        # Assigns the test_df attribute
        self.test_df = test_df

    def _mapped_fns(self):
        """
        Helper function that checks values in test_df to find if the deviation does not exceed the
        largest deviation between train and ideal (previously multiplied by square-root of 2 or
        the number inputted).
        Input:
            No explicit input, uses the implicitly created test_df input and inherited train_df.
        Output:
            output_list (list) - mapped x, y values of test_df with the delta (difference)
            and name of the ideal function.
        """
        mapped_fn_df = super().mapped_fns()
        _output_list = []

        # Checks the deviation of points within test_df to see if they lie between the lower and
        # upper bounds of the four ideal functions
        for line in self.test_df.itertuples():
            for ideal_fn in mapped_fn_df:
                my_list = []
                # Loops the points within test_df against ideal_df's functions, based on x
                # co-ordinates (index) matching
                for row in ideal_fn.itertuples():
                    if line.Index == row.Index:
                        # Calculates the difference or error and converts to absolute value
                        diff = calc_diff(line.y_test_func, row.y_ideal)
                        abs_diff = abs(diff)
                        # Checks the value against the max deviation multiplied by square root
                        if abs_diff <= row.prod_max_dev_sq_root:
                            my_list.append([line.Index, line.y_test_func, abs_diff, row.square_root, row.name])
                _output_list.append(my_list)
        output_list = [tuple(values) for line in _output_list for values in line]
        return output_list

    def mapped_fns_df(self):
        """
        Creates dataframe of mapped functions for test data.
        Input:
            No explicit input, calls _mapped_fns function and creates further dataframe.
        Output:
            mapped_output_df (dataframe) - mapped x, y values of test_df with the delta (difference)
            and name of the ideal function.
        """
        output_list = self._mapped_fns()
        # Returns a Pandas dataframe with results
        mapped_output_df = pd.DataFrame(output_list, columns=['x', 'y_test_func', 'delta_y_test_func',
                                                              'square_root', 'num_of_ideal_func'])
        mapped_output_df.set_index('x', inplace=True)
        mapped_output_df.sort_index(inplace=True)
        return mapped_output_df

    def mapped_fns_dict(self):
        """
        Creates dictionary of test data mapped to ideal function to be used as input to sqlalchemy.
        Input:
            No explicit input, uses output of mapped_fns_df to create dictionary.
        Output:
            _mapped_fns_dict (dictionary) - dict of mapped_fns_df in correct format for
            etl_sql.SQLTableBuilder class.
        """
        mapped_fns_dict = self.mapped_fns_df().to_dict('records')

        _list = []
        for x_val in self.mapped_fns_df().index:
            _dict = dict()
            _dict['x'] = x_val
            _dict['name'] = 'mapped'
            _list.append(_dict)

        for dict_entries, x_val in zip(mapped_fns_dict, _list):
            dict_entries.update(x_val)
        return mapped_fns_dict

    def _set_difference(self, df, mapped_points):
        """
        Helper function using set difference methodology to find unmapped points
        between function index and mapped points.
        """
        idx = set(df.index.values)
        dif = idx.difference(mapped_points)
        return dif

    def unmapped_fns(self):
        """
        Creates dataframe of unmapped test function points, compared to each ideal function.
        A point mapped by ideal_func x and not mapped by ideal_func y will appear as an unmapped point
        for ideal_func y, for example.
        Input:
            No explicit input, continuation of mapped_fns_df against test_df
        Output:
            unmapped_output_df (dataframe) - unmapped functions for each ideal function
        """
        mapped_fns_df = self.mapped_fns_df()
        output_list = []
        # Selects the relevant dataframe and retrieves index
        for ideal_func in mapped_fns_df['num_of_ideal_func'].unique():
            _df = mapped_fns_df.loc[mapped_fns_df['num_of_ideal_func'] == ideal_func, 'y_test_func']
            out = set(_df.index.values)
            # Uses set difference to identify unmapped co-ordinates
            dif = self._set_difference(self.test_df, out)
            # Appends the unmapped points to a list
            for item in dif:
                y_ = self.test_df.loc[self.test_df.index == item, 'y_test_func'].values.tolist()
                for data in y_:
                    _output = (item, data, ideal_func)
                    output_list.append(_output)

        # Returns a Pandas dataframe with results
        unmapped_output_df = pd.DataFrame(output_list, columns=['x', 'y_test_func', 'num_of_ideal_func'])
        unmapped_output_df.set_index(['num_of_ideal_func', 'x'], inplace=True, verify_integrity=False)
        unmapped_output_df.sort_index(inplace=True)
        return unmapped_output_df

    def unmapped_fns_set(self):
        """
        Creates dataframe of all unmapped test functions. Points not mapped by any function (zero of the 4),
        are returned
        Input:
            No explicit input, uses output of mapped_fns_df and test_df.
        Output:
            unmapped_output_df (dataframe) - x, y values for unmapped test values.
        """
        # Uses set difference to identify unmapped co-ordinates
        out = set(self.mapped_fns_df().index.values)
        dif = self._set_difference(self.test_df, out)

        # Appends the unmapped points to a list
        output_list = []
        for item in dif:
            y_ = self.test_df.loc[self.test_df.index == item, 'y_test_func'].values.tolist()
            for data in y_:
                _output = (item, data)
                output_list.append(_output)

        # Returns a Pandas dataframe with results
        unmapped_output_df = pd.DataFrame(output_list, columns=['x', 'y_test_func'])
        unmapped_output_df.set_index('x', inplace=True)
        unmapped_output_df.sort_index(inplace=True)
        return unmapped_output_df

    def unmapped_fns_in_range(self):
        """
        Checks the range of function values lying within each mapped ideal function and then re-checks for
        unmapped data points within this range.
        Input:
            No explicit input, uses output of mapped_fns_df and unmapped_fns.
        Output:
            unmapped_fns_in_range_df (dataframe) - mapped and unmapped points in range identified by 1
            and 0, respectively.
        """
        my_list = []
        unmapped_fns = self.unmapped_fns()
        mapped_fns_df = self.mapped_fns_df()
        # Selects the mapped functions and adds 'mapped' = 1
        sub_df = mapped_fns_df.drop(['delta_y_test_func', 'square_root'], axis=1)
        sub_df['mapped'] = 1
        # Finds the min and max for y values within the mapped function, to identify additional
        # unmapped points within the range
        for ideal_func in mapped_fns_df['num_of_ideal_func'].unique():
            _sub_df = sub_df[sub_df['num_of_ideal_func'] == ideal_func]
            y_min = _sub_df['y_test_func'].min()
            y_max = _sub_df['y_test_func'].max()
            for x, y in zip(unmapped_fns['y_test_func'].index,
                            unmapped_fns['y_test_func'].values):
                if x[0] == ideal_func:
                    if y >= y_min and y <= y_max:
                        my_list.append([x[1], y, ideal_func])

        # Inserts the unmapped functions in range into a dataframe with 'mapped' = 0
        _df = pd.DataFrame(my_list, columns=['x', 'y_test_func', 'num_of_ideal_func'])
        _df = _df.set_index('x', drop=True, verify_integrity=False)
        _df['mapped'] = 0

        unmapped_fns_in_range_df = pd.concat([_df, sub_df], axis=0)
        unmapped_fns_in_range_df['square_root'] = self.sq_root_number
        return unmapped_fns_in_range_df

    def summary_results_df(self):
        """
        Combines results of mapped and unmapped counts into a single dataframe.
        Input:
            No explicit input, uses mapped_fns_df, unmapped_fns_in_range, and test_df
        Output:
            summary_results_df (dataframe) - results including percentage mapped (area and total)
        """
        square_root = self.mapped_fns_df().iloc[0]['square_root']
        unmapped_fns_in_range = self.unmapped_fns_in_range()

        # Creates groupby objects for summary data
        mapped = unmapped_fns_in_range.groupby(['num_of_ideal_func'])['mapped'].sum()
        count_mapped = unmapped_fns_in_range.groupby(['num_of_ideal_func'])['mapped'].count()

        # Calculates proportion of points mapped
        perc_mapped_area = mapped/count_mapped
        perc_mapped_total = mapped/self.test_df.shape[0]

        # Concatenates the results to single dataframe
        summary_results_df = pd.concat([mapped, count_mapped, perc_mapped_area, perc_mapped_total], axis=1)
        summary_results_df.columns = ['mapped', 'points_in_map_area', 'perc_mapped_in_area', 'perc_mapped_total']
        summary_results_df['square_root'] = square_root
        return summary_results_df
