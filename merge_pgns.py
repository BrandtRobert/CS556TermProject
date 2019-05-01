import argparse
import pandas as pd
from functools import reduce
from typing import List
import sqlite3
from sqlite3 import Error
import sys


def connect_to_db(db_path: str = 'J1939.db'):
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except Error as e:
        print(e, file=sys.stderr)
        sys.exit(1)


def is_continuous(conn, spn: str):
    cursor = conn.cursor()
    cursor.execute("SELECT Resolution FROM SPNandPGN WHERE SPN=?", (spn,))
    row = cursor.fetchone()
    if "states" in row[0]:
        # If the value contains 'states' then it's likely discrete
        return False
    return True


def perform_interpolations(dataframe: pd.DataFrame):
    conn = connect_to_db()
    length = dataframe.shape[0]

    log_file = open('./results/logfile.txt', 'w')

    for PGNandSPN in dataframe.keys()[1:]:
        spn = PGNandSPN.split(':')[1]
        series = dataframe[PGNandSPN]
        if is_continuous(conn, spn):
            # Interpolate only fills backwards if given a limit value
            series.interpolate(method='linear', limit=length, limit_direction='both', inplace=True)
            print('{}, continuous'.format(PGNandSPN), file=log_file)
        else:
            # Forward pass through the data (the way we intend to fill)
            series.interpolate(method='ffill', inplace=True)
            # Backward pass through the data (in case we miss the first set of na values)
            series.interpolate(method='bfill', inplace=True)
            print('{}, discrete'.format(PGNandSPN), file=log_file)
        dataframe[PGNandSPN] = series

    log_file.close()

    return dataframe


def main():
    parser = argparse.ArgumentParser(description='A program to merge pgn / spn datasets. '
                                                 'Fills in missing values using linear interpolation')
    parser.add_argument('output_file', metavar='[Output File]', type=str, default='merged.csv',
                        help='The name of the merged PGN file')
    parser.add_argument('files', type=str, nargs='+', help='A set of PGN files to merge')
    parser.add_argument('--no-fill', action='store_false', dest='fill',
                        default=True, help="Don't fill in missing values")
    args = parser.parse_args()

    output_file: str = args.output_file
    files: str = args.files
    fill: bool = args.fill

    # Read in PGN datafiles
    print('Reading input datasets...')
    dataframes: List[pd.DataFrame] = []
    for file in files:
        df: pd.DataFrame = pd.read_csv(file)
        # Clean up data by stripping whitespace from headers and removing unwanted columns
        df = df.rename(columns=lambda x: x.strip())
        df = df.drop(['RowId', 'TimeInterval', 'Difference', 'Label'], axis=1)
        dataframes.append(df)

    # Merge datasets together using pandas
    print('Now merging datasets...')
    merged_df: pd.DataFrame = reduce(lambda left, right: pd.merge(left, right, how='outer'), dataframes)
    merged_df = merged_df.sort_values(by='Time')

    if fill:
        print('Filling missing values using linear interpolation...')
        # Fill values with linear interpolation
        # filled_df: pd.DataFrame = merged_df.interpolate(method='linear', limit_direction='both', limit=num_rows)
        filled_df: pd.DataFrame = perform_interpolations(merged_df)
    else:
        filled_df = merged_df

    print('Writing output to file {}'.format(output_file))
    filled_df.to_csv(output_file, index=False, na_rep='NA')


if __name__ == "__main__":
    main()

