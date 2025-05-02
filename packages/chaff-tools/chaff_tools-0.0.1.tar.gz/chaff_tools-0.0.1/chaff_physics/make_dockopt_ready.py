import os
import argparse
import gzip
import shutil
import tarfile
import logging
from chaff_tools.yaml_wrangler import *

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def gzip_db2_files(file_paths, output_dir):
    """Compress .db2 files into .db2.gz files and save them to the specified directory."""
    gzipped_files = []
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file_path in file_paths:
        if not os.path.isfile(file_path) or not file_path.endswith('.db2'):
            logging.warning(f"Skipping invalid file: {file_path}")
            continue
        
        output_file = os.path.join(output_dir, os.path.basename(file_path) + '.gz')

        try:
            with open(file_path, 'rb') as f_in, gzip.open(output_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
            gzipped_files.append(output_file)
            logging.info(f"Compressed {file_path} → {output_file}")
        except Exception as e:
            logging.error(f"Error compressing {file_path}: {e}")

    return gzipped_files


def create_tgz_from_files(file_paths, tgz_file):
    """Create a .tgz archive from a list of files."""
    try:
        with tarfile.open(tgz_file, 'w:gz') as tar:
            for file_path in file_paths:
                if os.path.exists(file_path):
                    tar.add(file_path, arcname=os.path.basename(file_path))
                    logging.info(f"Added {file_path} to {tgz_file}")
                else:
                    logging.warning(f"Skipping missing file: {file_path}")
        logging.info(f"Successfully created tarball: {tgz_file}")
    except Exception as e:
        logging.error(f"Failed to create tarball {tgz_file}: {e}")
        raise


def cleanup_directory(directory):
    """Deletes a directory and its contents."""
    try:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            logging.info(f"Cleaned up temporary directory: {directory}")
        else:
            logging.warning(f"Cleanup skipped, directory not found: {directory}")
    except Exception as e:
        logging.error(f"Error cleaning up directory {directory}: {e}")


def process_contaminant_set(yaml_file, output_path, cleanup=True):
    """Process the contaminant set, compress .db2 files, and create a .tgz archive."""
    os.makedirs(output_path, exist_ok=True)

    # Load selected actives and contaminants from YAML
    try:
        selected_actives, selected_contaminants, _, _ = load_from_yaml(yaml_file)
    except Exception as e:
        logging.error(f"Error loading YAML file: {e}")
        raise

    # Combine selected actives and contaminants
    contaminant_set = selected_actives + selected_contaminants

    # Ensure all files exist
    valid_files = [f for f in contaminant_set if os.path.isfile(f)]
    if not valid_files:
        logging.error("No valid .db2 files found in contaminant set.")
        raise FileNotFoundError("No valid .db2 files found in contaminant set.")

    # Create a directory for compressed files (renamed to working_db_files)
    working_dir = os.path.join(output_path, 'working_db_files')
    gzipped_files = gzip_db2_files(valid_files, working_dir)

    if not gzipped_files:
        logging.error("No .db2.gz files were created.")
        raise RuntimeError("Failed to compress any .db2 files.")

    # Generate a unique tarball name based on YAML filename
    yaml_name = os.path.splitext(os.path.basename(yaml_file))[0]
    yaml_ascii_friendly = yaml_name.replace('.', 'pt')
    tgz_filename = f"{yaml_ascii_friendly}.tgz"
    tgz_file_path = os.path.join(output_path, tgz_filename)

    # Create .tgz archive
    create_tgz_from_files(gzipped_files, tgz_file_path)

    logging.info(f"Contaminant set successfully processed and saved as {tgz_filename}")

    # Optional cleanup (defaults to True)
    if cleanup:
        cleanup_directory(working_dir)


def main():
    parser = argparse.ArgumentParser(description="Prepare a .tgz file for DockOpt from a chaff-tools YAML file.")
    parser.add_argument(
        '--yaml-file', type=str, required=True,
        help="Path to the YAML file containing the contaminant set."
    )
    parser.add_argument(
        '--output', type=str, required=True,
        help="Path to the output directory where the .tgz file will be saved."
    )
    parser.add_argument(
        '--no-cleanup', action='store_true',
        help="Disable cleanup of the working_db_files directory after processing."
    )

    args = parser.parse_args()
    
    process_contaminant_set(args.yaml_file, args.output, cleanup=not args.no_cleanup)


if __name__ == "__main__":
    main()
