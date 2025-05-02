import os
import argparse
import shutil
import random
import logging

#chaff-splitdb2 --input-dir data --split-fraction 0.8 -seed 42


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def split_files(input_dir, output_dir, train_folder, test_folder, split_fraction, seed):
    """
    Splits .db2 files into train and test subdirectories.

    Args:
        input_dir (str): Directory containing .db2 files.
        output_dir (str): Directory where train/ and test/ subdirectories will be created.
        train_folder (str): Name of the train subdirectory.
        test_folder (str): Name of the test subdirectory.
        split_fraction (float): Fraction of data to use for training (e.g., 0.8 means 80% train, 20% test).
        seed (int): Seed for reproducibility (only used locally).
    """
    # Ensure input directory exists
    if not os.path.isdir(input_dir):
        logging.error(f"Input directory '{input_dir}' does not exist.")
        raise FileNotFoundError(f"Input directory '{input_dir}' does not exist.")

    # Create output directories
    train_dir = os.path.join(output_dir, train_folder)
    test_dir = os.path.join(output_dir, test_folder)
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)

    # Find all .db2 files in the input directory
    db2_files = [f for f in os.listdir(input_dir) if f.endswith(".db2")]

    if not db2_files:
        logging.warning("No .db2 files found in the input directory.")
        return

    # Validate split fraction
    if not (0.0 < split_fraction < 1.0):
        logging.error("Split fraction must be between 0 and 1 (exclusive).")
        raise ValueError("Invalid split fraction. Use a value between 0 and 1.")

    # Use a local random instance to avoid affecting global randomness
    rng = random.Random(seed)
    rng.shuffle(db2_files)  # Shuffle file list locally

    split_index = int(len(db2_files) * split_fraction)
    train_files = db2_files[:split_index]
    test_files = db2_files[split_index:]

    # Move files to respective directories
    for file in train_files:
        shutil.move(os.path.join(input_dir, file), os.path.join(train_dir, file))
        logging.info(f"Moved {file} → {train_dir}")

    for file in test_files:
        shutil.move(os.path.join(input_dir, file), os.path.join(test_dir, file))
        logging.info(f"Moved {file} → {test_dir}")

    logging.info(f"Data split complete: {len(train_files)} train files, {len(test_files)} test files.")


def main():
    parser = argparse.ArgumentParser(description="Split .db2 files into train and test directories.")
    parser.add_argument(
        '--input-dir', type=str, required=True,
        help="Path to the directory containing .db2 files."
    )
    parser.add_argument(
        '--output-dir', type=str, default=".",
        help="Path where train/ and test/ subdirectories will be created (default: current directory)."
    )
    parser.add_argument(
        '--train-folder', type=str, default="train",
        help="Name of the training subdirectory (default: 'train')."
    )
    parser.add_argument(
        '--test-folder', type=str, default="test",
        help="Name of the testing subdirectory (default: 'test')."
    )
    parser.add_argument(
        '--split-fraction', type=float, required=True,
        help="Fraction of data to use for training (must be between 0 and 1)."
    )
    parser.add_argument(
        '--seed', type=int, default=42,
        help="Random seed for reproducibility (default: 42, affects only this function)."
    )

    args = parser.parse_args()
    split_files(args.input_dir, args.output_dir, args.train_folder, args.test_folder, args.split_fraction, args.seed)


if __name__ == "__main__":
    main()
