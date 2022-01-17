# summary.py
# -*- coding: utf-8 -*-

# PURPOSE:    This module serves 2 criteria:
# (1) Generates a summary dataframe reporting results of changing the upper and lower
# boundaries for a number inputted.
# (2) Creates a graph per Ideal function, displaying the summary results.


# Library imports
import pandas as pd
from os import getcwd

from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.transform import dodge
from bokeh.io import output_file
from bokeh.io import save
from bokeh.palettes import Spectral11

# Imports own modules
from test import TestFunctionReturner
from graphing import create_graph_folder

# Creates additional folder to save graphs
create_graph_folder('additional_graphs')


class _SummaryReportFetch(TestFunctionReturner):
    """
    Creates helper class object, to be repeatedly called for each new square root given by the range object
    from SummaryReporter.
    Input is the new square root passed by SummaryReporter.
    No explicit Output, except the changed square root attribute.
    """

    # Initiates new constructor
    def __init__(self, train_df, ideal_df, test_df, sq_root_number):
        # Calls parent's (TestFunctionReturner) constructor
        super().__init__(train_df, ideal_df, test_df, sq_root_number)

    def new_sq_root_number(self, new_sqrt):
        # Sets the square root to the new input
        self.sq_root_number = new_sqrt


class SummaryReporter:
    """
    Repeatedly calls summary results df with different square roots, then concatenates these for input
    to Bokeh.
    Calls Bokeh library with summarised data for graph generation.
    """
    # Initiates new constructor
    def __init__(self, start, stop, step, train, ideal, test):
        self.start = start
        self.stop = stop
        self.step = step
        self.train = train
        self.ideal = ideal
        self.test = test

    def summary(self):
        """
        Repeatedly calls the summary results df with different square roots, concatenates and returns
        summary of results.
        Inputs:
            None - implicit new square root number serves as input to inherited summary_results_df.
        Outputs:
            DataFrame of square root, percentage mapped in area and percentage mapped in total.
        """
        my_list = []
        # Creates range object iterator
        for i in range(self.start, self.stop + 1, self.step):
            # Creates supporting class object
            class_obj = _SummaryReportFetch(self.train, self.ideal, self.test, 1)
            class_obj.new_sq_root_number(i)

            # Retrieves summary report for that square root
            _df = class_obj.summary_results_df()

            # Appends all summary reports together
            my_list.append(_df)
        return pd.concat(my_list)

    def summary_graphs(self):
        """
        Outputs Bokeh graph representations of each summary from above.
        Inputs:
            None - implicit continuation of the summary function above.
        Outputs:
            Graph of square root and percentage mapped in area and percentage mapped in total.
        """
        # Creates the summary dataframe
        _df = self.summary()
        for idx in _df.index.unique():
            # Retrieves required columns for graphing
            df = _df.loc[_df.index == idx][['square_root', 'perc_mapped_in_area', 'perc_mapped_total']]
            sq_rt = [str(sq_rt) for sq_rt in df['square_root'].values]

            # Creates title for graph
            _title = idx.replace('_', ' ')

            # Inputs the graph data to a ColumnDataSource dictionary object
            data = {'sq_rt': sq_rt,
                    'perc_mapped_in_area': df['perc_mapped_in_area'].values,
                    'perc_mapped_total': df['perc_mapped_total'].values
                    }
            source = ColumnDataSource(data=data)

            # Instantiates figure for graphing
            p = figure(x_range=sq_rt, y_range=(0, 1.1), width=1000, height=750,
                       title=_title + ": percentage test points mapped by differing square roots",
                       toolbar_location=None, x_axis_label='square root', y_axis_label='percentage mapped')
            # Plots bars
            p.vbar(x=dodge('sq_rt', -0.25, range=p.x_range), top='perc_mapped_in_area', width=0.2, source=source,
                   color=Spectral11[1], legend_label="perc_mapped_in_area")
            p.vbar(x=dodge('sq_rt', 0.25, range=p.x_range), top='perc_mapped_total', width=0.2, source=source,
                   color=Spectral11[3], legend_label="perc_mapped_total")

            # Graph formatting
            p.title.text_font_size = "14px"
            p.x_range.range_padding = 0.01
            p.xgrid.grid_line_color = None
            p.add_layout(p.legend[0], 'right')

            # Graph filename
            _filename = idx + '_summary.html'
            graphs_directory = getcwd() + '/additional_graphs/'
            output_file(graphs_directory + _filename)
            save(p)
