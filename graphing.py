# graphing.py
# -*- coding: utf-8 -*-

# PURPOSE:    This module serves 2 criteria:
# (1) Creates graph folder.
# This is either the main graph or additional_graphs folder.
# (2) Prepares and presents the data from the test function in Bokeh graphs.


# Library imports
from bokeh.plotting import figure
from bokeh.plotting import output_file
from bokeh.plotting import save
from bokeh.palettes import Spectral11
import os

# Imports own modules
from test import TestFunctionReturner


# ---------------------Functions---------------------


def create_graph_folder(graph_folder_name='main_graphs'):
    """
    Creates relevant folder to save Bokeh graph outputs.
    Input:
        graph_folder_name (str): defaulted to 'main_graphs', else will create additional_graphs
        folder
    Output:
        Created folder, no explicit return value.
    """
    if graph_folder_name != 'main_graphs':
        graph_folder_name = 'additional_graphs'
    current_directory = os.getcwd()
    final_directory = os.path.join(current_directory, graph_folder_name)
    if not os.path.exists(final_directory):
        os.makedirs(final_directory)


# -----------------------Classes----------------------


class IdealPlotter(TestFunctionReturner):
    """
    Prepares and presents the data from the test function in one Bokeh graph per function
    Input is the parameters inherited from TestFunctionReturner - no explicit additional parameters
    Output is one Bokeh graph per function
    """

    # Initiates new constructor
    def __init__(self, train_df, ideal_df, test_df, sq_root_number):
        # Calls parent's (TrainFunctionReturner) constructor
        super().__init__(train_df, ideal_df, test_df, sq_root_number)

    def get_plot_data(self):
        """
        Retrieves and prepares the data for mapped_plotted_fns.
        Input:
            No explicit input, uses inherited dataframe.
        Output:
            df_list (list): transformed dataframes concatenated into a list.
        """
        df_list = []
        # Inheritance of unmapped_fns_in_range and mapped_fns
        unmapped_fns_in_range = super().unmapped_fns_in_range()
        mapped_fns = super().mapped_fns()
        # Retrieving list of functions
        fn_list = list(unmapped_fns_in_range['num_of_ideal_func'].unique())
        num_lines = len(fn_list)

        for fn_num in range(num_lines):
            # Iterates through  mapped_fns (list with dataframes)
            _mapped_fns = mapped_fns[fn_num]
            name = _mapped_fns['name'].unique()[0]
            # Retrieves the data for the mapped and unmapped data in range so both can be plotted
            _unmatched_fn_df = unmapped_fns_in_range[unmapped_fns_in_range['num_of_ideal_func'] == name]
            _unmatched_fn_df = _unmatched_fn_df.reset_index()
            _unmatched_fn_df = _unmatched_fn_df.drop(['square_root'], axis=1)
            _mapped_fns = _mapped_fns.reset_index()
            # Merges mapped and unmapped data into one dataframe
            all_results = _mapped_fns.merge(_unmatched_fn_df, left_on='x', right_on='x', how="left",
                                            suffixes=('_l', '_r'))
            all_results = all_results.set_index('x')
            all_results = all_results.drop(['num_of_ideal_func', 'prod_max_dev_sq_root'], axis=1)
            df_list.append(all_results)
        return df_list

    def mapped_plotted_fns(self, unmapped_in_range=False):
        """
        Creates separate Bokeh graphs for each of the 4 matched test functions.
        Input:
            unmapped_in_range (boolean) - default is False, if True will show relevant points lying
            within range that are still unmapped by the function.
        Output:
            1 saved Bokeh graph representing each function.
        """
        # Creates the data for plotting by running above function
        get_plot_data = self.get_plot_data()
        num_lines = len(get_plot_data)
        palette = Spectral11[0:5]

        for fn_num in range(num_lines):
            # Creates a graph for each function
            # Retrieves upper and lower bound line data
            borders_to_plot = get_plot_data[fn_num][['upper_bound', 'lower_bound']]
            # Retrieves function data to plot
            fn_to_plot = get_plot_data[fn_num]['y_ideal']
            # Retrieves the function name
            name = get_plot_data[fn_num]['name'].unique()[0]
            # Retrieves the square root applied
            square_root = str(get_plot_data[fn_num]['square_root'].unique()[0])
            # Creates title for graph
            _title = ' plotted with upper and lower bounds, mapped functions: factor square root '
            # Bokeh figure instantiation
            p = figure(width=1000,
                       height=750,
                       x_axis_label='x',
                       y_axis_label='y')
            # Creating multiline graph for upper and lower bounds -> 2 lines
            p.multi_line(xs=[borders_to_plot.index.values] * 2,
                         ys=[borders_to_plot[col_name] for col_name in borders_to_plot.columns],
                         line_color=palette[fn_num],
                         line_width=4,
                         legend_label=name.replace('_', ' ') + ' upper & lower bounds')
            # Creating single line for function -> 3 lines in total
            p.line(x=fn_to_plot.index,
                   y=fn_to_plot.values,
                   line_color=palette[fn_num + 1],
                   line_width=2,
                   legend_label=name.replace('_', ' '))

            # Default is to only plot mapped data points
            mapped_plot_data = get_plot_data[fn_num][get_plot_data[fn_num]['mapped'] == 1]
            # Plots mapped data points as circles
            p.circle(x=mapped_plot_data.index,
                     y=mapped_plot_data['y_test_func'].values,
                     size=3,
                     color="#000000",
                     legend_label='mapped funcs',
                     alpha=0.8)
            # Creates graph title and sets graph formatting
            title_label = name.replace('_', ' ') + _title + square_root
            p.title.text_font_size = "14px"

            # Creates filename
            _filename = name + '.html'
            graphs_directory = os.getcwd() + '/main_graphs/'
            # Default is to only plot mapped data points - if unmapped_in_range used then will plot
            # unmapped points as squares
            if unmapped_in_range:
                unmapped_plot_data = get_plot_data[fn_num][get_plot_data[fn_num]['mapped'] == 0]
                p.square(x=unmapped_plot_data.index,
                         y=unmapped_plot_data['y_test_func'].values,
                         size=5,
                         color='#1C5771',
                         legend_label='unmapped funcs',
                         alpha=0.8)
                _title = _title.replace(':', ' and unmapped functions:')
                title_label = name.replace('_', ' ') + _title + square_root
                _filename = name + '_unmapped' + '.html'

            p.title = title_label
            p.title_location = 'above'
            p.add_layout(p.legend[0], 'right')
            output_file(graphs_directory + _filename)
            save(p)
