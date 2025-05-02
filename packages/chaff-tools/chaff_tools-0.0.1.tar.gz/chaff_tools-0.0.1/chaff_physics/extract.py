import os
import tarfile
import gzip
import shutil
import argparse
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def extract_tar(file_path, output_dir):
    """Extract a tar archive with auto-detection of compression and clean up after extraction."""
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Extract tar archive with auto-detection of compression type
        with tarfile.open(file_path, "r:*") as tar:
            tar.extractall(path=output_dir)

        logging.info(f"Extracted {file_path} to {output_dir}")
        
    except Exception as e:
        logging.error(f"Error extracting {file_path}: {e}")

def extract_nested_archives(root_archives, working_dir):
    """Extract multiple root .tar.gz files and all nested .tar.gz files."""
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)

    for archive in root_archives:
        logging.info(f"Processing archive: {archive}")
        try:
            extract_tar(archive, working_dir)
        except Exception as e:
            logging.error(f"Error extracting nested archive {archive}: {e}")
            continue

    # Extract all nested .tar.gz files
    for root, _, files in os.walk(working_dir):
        for file in files:
            if file.endswith(".tar.gz"):
                nested_tar_path = os.path.join(root, file)
                logging.info(f"Extracting nested archive: {nested_tar_path}")
                try:
                    extract_tar(nested_tar_path, root)
                except Exception as e:
                    logging.error(f"Error extracting nested archive {nested_tar_path}: {e}")
                    continue

def extract_db2_gz_files(working_dir, dest_folder):
    """Extract all .db2.gz files in the working directory and move extracted files to dest_folder."""
    
    os.makedirs(dest_folder, exist_ok=True)

    try:
        for root, _, files in os.walk(working_dir):
            for file in files:
                if file.endswith(".db2.gz"):
                    file_path = os.path.join(root, file)
                    extracted_path = os.path.join(dest_folder, file[:-3])  # Remove '.gz' extension

                    logging.info(f"Extracting .db2.gz file: {file_path}")
                    try:
                        with gzip.open(file_path, "rb") as f_in, open(extracted_path, "wb") as f_out:
                            shutil.copyfileobj(f_in, f_out)
                        logging.info(f"Extracted: {file_path} -> {extracted_path}")
                    except Exception as e:
                        logging.error(f"Error extracting {file_path}: {e}")

    except Exception as e:
        logging.error(f"Error processing .db2.gz files: {e}")

def cleanup_working_dir(working_dir):
    """Deletes the working directory after processing."""
    try:
        if os.path.exists(working_dir):
            shutil.rmtree(working_dir)
            logging.info(f"Deleted working directory: {working_dir}")
        else:
            logging.warning(f"Working directory not found: {working_dir}")
    except Exception as e:
        logging.error(f"Error deleting {working_dir}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Extract nested tar.gz downloaded from TLDR.")
    parser.add_argument("--files", nargs="+", required=True, help="Paths to the root .tar.gz files (space-separated for multiple files)")
    parser.add_argument("--working-dir", default="extract_working_dir", help="Temporary extraction folder")
    parser.add_argument("--dest-folder", default="db2_files", help="Destination folder for .db2 files")
    parser.add_argument("--no-cleanup", action="store_true", help="Disable cleanup of the working directory after extraction.")
    args = parser.parse_args()

    logging.info("Starting extraction process...")

    try:
        extract_nested_archives(args.files, args.working_dir)
        extract_db2_gz_files(args.working_dir, args.dest_folder)
    finally:
        if not args.no_cleanup:
            cleanup_working_dir(args.working_dir)
        else:
            logging.info("Skipping cleanup as per flag request.")
        
    logging.info("Extraction and organization complete.")

if __name__ == "__main__":
    main()
