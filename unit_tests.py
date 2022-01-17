# Library imports
import unittest
import numpy as np
import pandas as pd

# Imports own modules
import etl_table
import arithmetic
import train
import test
import unmapped


class ETLTableColNameCheck(unittest.TestCase):
    def setUp(self):
        self.mock_dict = {'ya': 1000}
        self.mock_list_w_dict = [{'x': '8.19', 'y': 'h'}]

    def test_col_name_check(self):
        """
        Tests _col_name_check fails if an invalid y-column inputted
        """
        self.assertRaises(AssertionError, etl_table.TableConverter({'test': './test'})._col_name_check,
                          self.mock_dict)

    def test_cast_string_to_float(self):
        """
        Tests _cast_string_to_float fails if a non-float or non-integer inputted
        """
        self.assertRaises(ValueError, etl_table.TableConverter({'test': './test'})._cast_string_to_float,
                          self.mock_list_w_dict)


class TestTrainFunction(unittest.TestCase):
    def setUp(self):
        self.mock_df_1 = pd.DataFrame.from_dict({'col_1': [3, -2], 'col_2': [8, -1]})
        self.mock_df_2 = pd.DataFrame.from_dict({'col_1': [-1, 4], 'col_2': [-2, 1]})
        self.mock_train_obj = train.TrainFunctionReturner(self.mock_df_1, self.mock_df_2)

    def test_calc_sum_of_squares(self):
        """
        Tests that _calc_sum_of_squares function is returning expected output
        """
        self.assertEqual(self.mock_train_obj._calc_sum_of_squares(self.mock_df_1, self.mock_df_2)[0][1],
                         [52, 34])

    def test_get_top_ideal_func(self):
        """
        Tests that _get_top_ideal_func function returns the column for the smallest number.
        """
        self.assertEqual(self.mock_train_obj.
                         _get_top_ideal_func([[['col_1', 'col_2'], [1, 3]],
                                              [['col_3', 'col_4'], [7, 2]]]), ['col_1', 'col_4'])

    def test_validate_sq_root_number(self):
        """
        Tests that an error is raised if a non-number passed as a parameter.
        """
        self.assertRaises(AssertionError, self.mock_train_obj._validate_sq_root_number, 'x')


class TestTestFunction(unittest.TestCase):
    def setUp(self):
        self.mock_dict = {'col_1': [3, 2, 1, 0], 'col_2': [5, 7, 9, 11]}
        self.mock_df = pd.DataFrame.from_dict(self.mock_dict)
        self.mock_array = np.array([0.0, 4, 2, 8])
        self.mock_train_obj = test.TestFunctionReturner(self.mock_df, self.mock_df, self.mock_df, 1)

    def test_set_difference(self):
        """
        Tests that _set_difference function is returning expected output
        """
        self.assertEqual(self.mock_train_obj._set_difference(self.mock_df, self.mock_array), {1, 3})


class TestUnmappedFunction(unittest.TestCase):
    def setUp(self):
        self.mock_df = pd.DataFrame.from_dict({'col_1': [3, 0], 'col_2': [0, 4]})
        self.mock_unmapped_obj = unmapped.UnmappedClusters(self.mock_df, self.mock_df, self.mock_df)

    def test_euclidean_dist(self):
        """
        Tests that _euclidean_dist is returning expected output.
        Logic based on triangle with sides (3, 4) -> length of hypotenuse is 5.
        """
        self.assertEqual(self.mock_unmapped_obj._euclidean_dist(self.mock_df['col_1'].values,
                                                                self.mock_df['col_2'].values), 5)


class TestArithmetic(unittest.TestCase):
    def setUp(self):
        self.mock_array = np.array([1, 2, -8])
        self.mock_y1 = np.array([3, -0.5, 2, 7])
        self.mock_y2 = np.array([2.5, 0.0, 2, 8])

    def test_calc_diff(self):
        """
        Tests difference calculation working as expected
        """
        self.assertEqual(arithmetic.calc_diff(5, 5), 0)

    def test_calc_sum(self):
        """
        Tests sum calculation working as expected
        """
        self.assertEqual(arithmetic.calc_sum(5, 5), 10)

    def test_square_number(self):
        """
        Tests square number calculation working as expected
        """
        self.assertEqual(arithmetic.square_number(5), 25)

    def test_sum_array(self):
        """
        Tests sum array calculation working as expected
        """
        self.assertEqual(arithmetic.sum_array(self.mock_array), -5)

    def test_minus_array(self):
        """
        Tests minus array calculation working as expected
        """
        self.assertEqual(arithmetic.minus_array(self.mock_y1[0], self.mock_y2[0]), 0.5)

    def test_calc_square_root(self):
        """
        Tests square root calculation working as expected
        """
        self.assertEqual(arithmetic.calc_square_root(16), 4)

    def test_calc_prod(self):
        """
        Tests multiplication calculation working as expected
        """
        self.assertEqual(arithmetic.calc_prod(7, 3), 21)

    def test_norm_root_mean_squared_error(self):
        decimal_place = 3
        # error message in case if test case got failed
        message = "y1 and y2 are not almost equal."
        self.assertAlmostEqual(arithmetic.
                               norm_root_mean_squared_error(self.mock_y1, self.mock_y2),
                               0.0816, decimal_place, message)


if __name__ == '__main__':
    unittest.main()
