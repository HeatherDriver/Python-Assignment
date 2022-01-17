# main.py
# -*- coding: utf-8 -*-

# Library imports
import pandas as pd
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import logging
import time

# Imports own modules
import input_args_files
import etl_table
import etl_sql
from test import TestFunctionReturner
from graphing import IdealPlotter
from graphing import create_graph_folder
from summary import SummaryReporter
from unmapped import UnmappedClusters

# Instantiates sqlalchemy Base and engine
Base = declarative_base()
engine = create_engine("sqlite://", echo=True)
Base.metadata.create_all(engine)

# Creates dataframe for data loaded by sqlalchemy within the main namespace
def df_create(table_name):
    """
    Creates a dataframe from sqlite db, with 'x' as the index.
    Input:
        table_name (str) - name of table
    Output:
        dataframe sorted on index.
    """
    stmt = "SELECT * FROM " + table_name
    with engine.connect() as conn:
        e_stmt = conn.execute(stmt)
    df = pd.DataFrame(e_stmt.fetchall())
    df.columns = e_stmt.keys()
    df.set_index('x', inplace=True)
    df.sort_index(inplace=True)
    df = df.drop(['index'], axis=1)
    return df


def main():
    # Initiate logfile
    logging.basicConfig(filename="logfile.log", level=logging.INFO)
    start = time.time()
    logging.info('---Started---')

    # Gets the input arguments
    _input = input_args_files.get_input_args()

    # Checks that a valid input has been received
    input_args_files.valid_path_inputted(_input)

    # Checks all the files are in inputted folder
    input_args_files.file_counter(_input)

    # Creates dictionary mapping file path to test, train and ideal
    files_folder = input_args_files.get_file_names(_input)

    # Checks that above dictionary was created
    _ = isinstance(files_folder, dict)

    # Stores the file names and paths in variables
    test, train, ideal = files_folder['test'], files_folder['train'], files_folder['ideal']

    # Creates the dataset dictionaries for each of test, train and ideal
    test_d, train_d, ideal_d = etl_table.TableConverter(test).table_to_dict(), etl_table.TableConverter(train).table_to_dict(), \
                               etl_table.TableConverter(ideal).table_to_dict()

    # Instantiates the SQL lite table objects
    test_ins = etl_sql.SQLTableBuilder(test_d)
    train_ins = etl_sql.SQLTableBuilder(train_d)
    ideal_ins = etl_sql.SQLTableBuilder(ideal_d)

    # Retrieves the SQL lite metadata
    my_test_class = type(test_ins.schema_create()[0]['clsname'], (Base,), test_ins.schema_create()[0])
    my_train_class = type(train_ins.schema_create()[0]['clsname'], (Base,), train_ins.schema_create()[0])
    my_ideal_class = type(ideal_ins.schema_create()[0]['clsname'], (Base,), ideal_ins.schema_create()[0])

    # Creates schemas
    Base.metadata.create_all(engine)
    data_test = test_ins.schema_create()[1]
    data_train = train_ins.schema_create()[1]
    data_ideal = ideal_ins.schema_create()[1]

    # Adds the data to each table created
    with Session(engine) as sess:
        sess.add_all(my_test_class(**rec) for rec in data_test)
        sess.add_all(my_train_class(**rec) for rec in data_train)
        sess.add_all(my_ideal_class(**rec) for rec in data_ideal)
        sess.commit()

    # Creates dataframes for further analysis
    test = df_create('Test')
    train = df_create('Train')
    ideal = df_create('Ideal')

    # Generates ideal functions based on initial mapping of train to ideal, followed by test to ideal.
    test_fns = TestFunctionReturner(train_df=train, ideal_df=ideal, test_df=test, sq_root_number=2)

    # Creates dictionary of mapped test data for loading in sqlalchemy.
    mapped_d = test_fns.mapped_fns_dict()

    # Instantiates SQL lite table object
    mapped_ins = etl_sql.SQLTableBuilder(mapped_d)

    # Retrieves the SQL lite metadata
    my_mapped_class = type(mapped_ins.schema_create()[0]['clsname'], (Base,), mapped_ins.schema_create()[0])

    # Creates schemas
    Base.metadata.create_all(engine)
    data_mapped = mapped_ins.schema_create()[1]

    # Adds the data to each table created
    with Session(engine) as sess:
        sess.add_all(my_mapped_class(**rec) for rec in data_mapped)
        sess.commit()

    # Creates main folder to save graphs
    create_graph_folder()

    # Saves only mapped points in range of ideal function
    IdealPlotter(train_df=train, ideal_df=ideal, sq_root_number=2, test_df=test).mapped_plotted_fns()

    # Specifying .mapped_plotted_fns(True) saves unmapped points in range of ideal function
    IdealPlotter(train_df=train, ideal_df=ideal, sq_root_number=2, test_df=test).mapped_plotted_fns(True)

    # Generates summary graphs at inputted square roots (2 - 10, with increments of 1)
    SummaryReporter(2, 10, 1, train, ideal, test).summary_graphs()

    # Generates data for unmapped functions at square root of 6 analysis
    unmapped_analysis = UnmappedClusters(train_df=train, ideal_df=ideal, test_df=test)

    # Prints Euclidean distances for clusters of unmapped points at upper and lower boundary set
    # at square root of 6
    unmapped_analysis.print_euclidean_dist()

    # Displays original unmapped clusters
    unmapped_analysis.original_cluster_display()

    # Shows polynomial line fitted to clusters
    unmapped_analysis.polynomial_display()

    # Concludes writing to logfile
    time_to_run = time.time() - start
    logging.info(("Time to run:", time_to_run))
    logging.info('---Finished---')


# Call to main function to run the program
if __name__ == "__main__":
    main()
