# arithmetic.py
# -*- coding: utf-8 -*-

# PURPOSE:    This module contains all arithmetic functions used in the program.

# Library imports
from math import sqrt
from numpy import array


def calc_diff(data_1, data_2):
    """
    Subtracts two numbers
    """
    return data_1 - data_2


def calc_sum(data_1, data_2):
    """
    Adds two numbers
    """
    return data_1 + data_2


def square_number(data_1):
    """
    Multiples a number by itself (i.e. squared)
    """
    return data_1 ** 2


def sum_array(data_1):
    """
    Sums a list or array
    """
    return sum(data_1)


def minus_array(data_1, data_2):
    """
    Subtracts elements in array_1 with corresponding elements in array_2
    """
    return array(data_1) - array(data_2)


def calc_square_root(data_1):
    """
    Calculates the square root
    """
    return sqrt(data_1)


def calc_prod(data_1, data_2):
    """
    Multiplies two numbers
    """
    return data_1 * data_2


def norm_root_mean_squared_error(y1, y2):
    """
    Calculates the normalised root mean squared error (RMSE) of the model.
    Normalised figure reflects the RMSE within the range of the y-axis.
    Input:
        y1 (array) - original y function values.
        y2 (array) - modelled y function values, predicted from model.
    Output:
        norm_rmse (float) - root mean squared error, normalised.
    """
    # rmse = mean_squared_error(y1, y2, squared=False)
    array_diff = minus_array(y1, y2)
    diff_squared = square_number(array_diff)
    mse = sum_array(diff_squared) / len(diff_squared)
    rmse = calc_square_root(mse)
    norm_rmse = rmse/(max(y1)-min(y1))
    return norm_rmse
