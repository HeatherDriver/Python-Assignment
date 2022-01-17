# train.py
# -*- coding: utf-8 -*-

# PURPOSE:    This module serves 2 criteria:
# (1) Finds the relevant ideal function per training function inputted.
# Based on the square of the error between the train point, and the corresponding ideal point.

# (2) Creates the upper and lower boundaries per function.
# This is based on multiplying the largest deviation by the square root of 2 (other numbers can be
# inputted), to create the boundaries.
# These boundaries will serve to form basis for mapping further test points, if they fall within
# these limits.


# Library imports
import pandas as pd
from arithmetic import calc_diff
from arithmetic import calc_sum
from arithmetic import calc_square_root
from arithmetic import calc_prod
from arithmetic import square_number
from arithmetic import sum_array


class TrainFunctionReturner:
    """
    Calculates the sum of squares for each ideal function, versus the 4 train functions. Then re-selects the
    ideal function for which the sum of squares is lowest.
    Creates the mapped_fns dataframe which has the upper and lower function boundaries - these are constructed
    based on multiplying the largest deviation between two points by the square root of 2 - but other numbers
    can be inputted.
    Upper and lower boundaries will become the margins for which test points can be mapped further.
    Inputs:
        train_df, ideal_df (dataframes) - created after being loaded by sqlalchemy.
        sq_root_number (int) - defaulted to 2 but other integers can be accepted.
    Outputs:
    """
    # Initiates new constructor
    def __init__(self, train_df, ideal_df, sq_root_number=2):
        self.train_df = train_df
        self.ideal_df = ideal_df
        self.sq_root_number = sq_root_number

    def _calc_sum_of_squares(self, train_dataframe, ideal_dataframe):
        """
        Calculates the sum of squares for each function within train_df, versus each of the 40
        ideal functions. Appends column and sum for output.
        Input:
            train_dataframe (dataframe) - object constructor will pass train_df
            ideal_dataframe (dataframe) - object constructor will pass ideal_df
        Output:
            my_list (list) - list of train_df columns mapped to sum of squares for all
            functions in ideal_df.
        """
        my_list = []
        for column in train_dataframe.columns:
            column_name, _sum_sq_diff = [], []
            for col in ideal_dataframe.columns:
                # Calculates difference or error and squaring this
                diff = calc_diff(train_dataframe[column], ideal_dataframe[col])
                sq_diff = square_number(diff)
                sq_diff = sq_diff.fillna(0)
                # Sums squared error
                sum_sq_diff = sum_array(sq_diff)
                column_name.append(col)
                _sum_sq_diff.append(sum_sq_diff)
            my_list.append([column_name, _sum_sq_diff])
        return my_list

    def _get_top_ideal_func(self, _calc_sum_of_squares):
        """
        Retrieves the top ideal function for each of the 4 columns of train_df - the top ideal
        function has the lowest sum of squares for its error.
        Input:
            _calc_sum_of_squares (list) - list from which to select lowest error.
        Output:
            my_list (list) - list of train_df columns mapped to function with lowest sum of
            squares in ideal_df.
        """
        my_list = []
        for ls_data in _calc_sum_of_squares:
            # Zips the column name with the sum_sq_diff
            zipped = zip(ls_data[0], ls_data[1])
            zipped = list(zipped)
            # Sorts the list in ascending order
            sorted_zip = sorted(zipped, key=lambda x: x[1])
            # slice for [0] - i.e. the lowest sum_sq_diff
            top_fns = sorted_zip[0][0]
            my_list.append(top_fns)
        return my_list

    def ideal_function(self):
        """
        Calculates the square difference between each ideal function and each column in
        train_df. Takes the top (list index will be zero) function for each of train_df's
        4 columns and outputs the results within a dictionary.
        Input:
            train_df (dataframe) - the training dataframe
        Output:
            output_dict (dictionary) - maps train_df column to the ideal function name.
        """
        # Calculates the sum of squares per ideal function versus train_df
        calc_sum_of_squares = self._calc_sum_of_squares(self.train_df, self.ideal_df)
        get_top_ideal_func = self._get_top_ideal_func(calc_sum_of_squares)

        # Outputs the results as a dictionary
        output_dict = {column: list_entry for (column, list_entry) in zip(self.train_df.columns, get_top_ideal_func)}
        return output_dict

    def _validate_sq_root_number(self, number):
        """
        Asserts that the input for sq_root_number is an integer or float if supplied.
        Input:
            number - input to validate
        Output:
            None - raises Exception if assertion fails
        """
        try:
            assert type(number) in [int, float]
        except AssertionError as exc:
            assert False, 'Incorrect input for square root, only integers or floats accepted'

    def mapped_fns(self):
        """
        Calculates the largest deviation between the train x,y and ideal x,y values, then multiplies
        this by the square root of 2.
        Creates the upper and lower bounds for each ideal x, y value, so these can be plotted.
        Upper and lower bounds are created from adding/subtracting the largest deviation from
        each of the ideal function's y values.
        Input:
            No explicit input but uses the output of ideal_function.
        Output:
            df_list (dataframe) - dataframe of index, ideal value, upper & lower bound, maximum
            deviation and ideal func name.
        """

        df_list = []
        for key, value in self.ideal_function().items():
            ideal = pd.Series(self.ideal_df[value], name='y_ideal')
            # Validates that an integer has been passed to calculate the square root
            self._validate_sq_root_number(self.sq_root_number)
            # Finds the largest deviation between the train x,y and ideal x,y values.
            large_dev = abs((calc_diff(self.train_df[key], ideal))).max()
            # Then multiplies the largest deviation by the sqrt of 2 (or inputted number)
            large_dev = calc_prod(large_dev, calc_square_root(self.sq_root_number))

            # Adds and subtracts larg_dev from the ideal function to give
            # the upper & lower bounds per x, y value within the ideal fn.
            upper = pd.Series(calc_sum(ideal, large_dev), name='upper_bound')
            lower = pd.Series(calc_diff(ideal, large_dev), name='lower_bound')

            # Returns a Pandas dataframe with results
            _df = pd.concat([ideal, upper, lower], axis=1)
            _df['prod_max_dev_sq_root'] = large_dev
            _df['square_root'] = self.sq_root_number
            _df['name'] = value
            df_list.append(_df)
        return df_list
