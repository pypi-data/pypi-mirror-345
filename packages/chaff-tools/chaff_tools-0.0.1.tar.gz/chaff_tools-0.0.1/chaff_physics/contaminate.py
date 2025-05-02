import argparse
import os
import numpy as np
import random
import logging
import pandas as pd
from chaff_tools.yaml_wrangler import *

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_prng(seed):
    """Initialize a random number generator using np.random.default_rng() for better reproducibility."""
    logging.info(f"Initializing PRNG with seed {seed}")
    return np.random.default_rng(seed)


def load_files(directory, sample_size=None):
    """Load and sample .db2 files from a given directory, returning absolute paths."""
    if not os.path.isdir(directory):
        logging.error(f"{directory} is not a valid directory.")
        raise NotADirectoryError(f"{directory} is not a valid directory.")
    
    all_files = [f for f in os.listdir(directory) if f.endswith('.db2')]
    
    if not all_files:
        logging.warning(f"No .db2 files found in directory: {directory}")
        raise FileNotFoundError(f"No .db2 files found in directory: {directory}")
    
    if sample_size:
        if sample_size <= 0:
            logging.error("Sample size must be a positive integer.")
            raise ValueError("Sample size must be a positive integer.")
        logging.info(f"Sampling {sample_size} files from the directory.")
        return [os.path.join(directory, f) for f in random.sample(all_files, min(sample_size, len(all_files)))]
    
    logging.info(f"Loading all files from directory: {directory}")
    return [os.path.join(directory, f) for f in all_files]


def select_samples(actives, contaminants, frac_contaminate, rng):
    """Select actives and contaminants based on frac_contaminate using an independent random number generator."""
    if not (0 <= frac_contaminate <= 1):
        logging.error(f"frac_contaminate must be between 0 and 1, got {frac_contaminate}")
        raise ValueError(f"frac_contaminate must be between 0 and 1, got {frac_contaminate}")
    
    num_actives = len(actives)
    num_contaminants = int(frac_contaminate * num_actives)
    num_contaminants = min(num_contaminants, len(contaminants))  # Ensure we don’t select more contaminants than available
    
    logging.info(f"Selecting {num_actives - num_contaminants} actives and {num_contaminants} contaminants.")
    
    selected_actives = rng.choice(actives, num_actives - num_contaminants, replace=False)
    selected_contaminants = rng.choice(contaminants, num_contaminants, replace=False)
    
    nonselected_actives = [a for a in actives if a not in selected_actives]
    nonselected_contaminants = [c for c in contaminants if c not in selected_contaminants]
    
    return (selected_actives.tolist(), selected_contaminants.tolist(),
            nonselected_actives, nonselected_contaminants)


def contaminate(actives_dir, contaminants_dir, frac_contaminate, output_file, seed=None, sample_size=None):
    logging.info("Starting contamination process.")

    if seed is None:
        seed = random.randint(0, 2**32 - 1)
        logging.info("No seed provided. Using a random seed.")
    
    rng = initialize_prng(seed)
    actives = load_files(actives_dir, sample_size)
    contaminants = load_files(contaminants_dir, sample_size)
    
    (selected_actives, selected_contaminants,
     nonselected_actives, nonselected_contaminants) = select_samples(
        actives, contaminants, frac_contaminate, rng)

    # Ensure output directory exists
    out_dir = os.path.dirname(output_file) or '.'
    os.makedirs(out_dir, exist_ok=True)

    save_to_yaml(
        selected_actives, selected_contaminants,
        nonselected_actives, nonselected_contaminants,
        seed, output_file
    )
    logging.info(f"Results saved to {output_file}")
    logging.info("Contamination process completed.")


def main():
    parser = argparse.ArgumentParser(
        description="Contaminate an active set with contaminants (e.g. ChAFF compounds)."
    )
    parser.add_argument(
        '--actives_dir', type=str, required=True,
        help="Directory containing the .db2 files for actives."
    )
    parser.add_argument(
        '--contaminants_dir', type=str, required=True,
        help="Directory containing the .db2 files for contaminants."
    )
    parser.add_argument(
        '--frac_contaminate', type=float, required=True,
        help="Fraction of contaminant samples to select, between 0 and 1."
    )
    parser.add_argument(
        '--seed', type=int, default=None,
        help="Seed for the random number generator to ensure reproducibility."
    )
    parser.add_argument(
        '--output_file', type=str, required=True,
        help="Output YAML file path to save the results."
    )
    
    args = parser.parse_args()
    contaminate(
        args.actives_dir,
        args.contaminants_dir,
        args.frac_contaminate,
        args.output_file,
        seed=args.seed
    )

if __name__ == "__main__":
    main()
