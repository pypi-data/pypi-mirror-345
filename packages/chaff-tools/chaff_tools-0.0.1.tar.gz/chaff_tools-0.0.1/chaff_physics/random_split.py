import argparse
import pandas as pd
import logging
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem
from rdkit.Chem import PandasTools
import numpy as np
import sys

from .fingerprint import (
    compute_fingerprint,
    cluster_fingerprints,
    realistic_split,
    split_df_into_train_and_test_sets
)

def random_split_cli():
    """
    Command-line interface for realistic random split of a CSV or TSV with SMILES.
    """
    parser = argparse.ArgumentParser(
        prog='cp-random-split',
        description='Perform clustering-based train/test split on a SMILES dataset'
    )
    parser.add_argument(
        '--input-file', '-i', required=True,
        help='Path to input CSV/TSV file containing SMILES column'
    )
    parser.add_argument(
        '--smiles-col', '-s', type=int, default=0,
        help='Index of the SMILES column (default: 0)'
    )
    parser.add_argument(
        '--frac-train', '-f', type=float, required=True,
        help='Fraction of data to use for training (e.g. 0.8)'
    )
    parser.add_argument(
        '--exact', action='store_true',
        help='Adjust to exact fraction by possibly splitting a cluster'
    )
    parser.add_argument(
        '--method', '-m', choices=['auto', 'tb', 'hierarchy'], default='auto',
        help='Clustering method (auto/tb/hierarchy)'
    )
    parser.add_argument(
        '--output', '-o', required=True,
        help='Base name for output files (train.csv and test.csv will be created)'
    )
    args = parser.parse_args()

    # Load data
    if args.input_file.endswith('.csv'):
        df = pd.read_csv(args.input_file)
    else:
        df = pd.read_csv(args.input_file, sep='\t')

    # Perform split
    clustered = realistic_split(
        df, args.smiles_col, args.frac_train,
        split_for_exact_frac=args.exact,
        cluster_method=args.method
    )
    train_df, test_df = split_df_into_train_and_test_sets(clustered)

    # Save outputs
    train_path = args.output + '_train.csv'
    test_path = args.output + '_test.csv'
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)

    logging.info(f"Train/test split complete.\n Train: {train_path}\n Test: {test_path}")

if __name__ == '__main__':
    random_split_cli()
