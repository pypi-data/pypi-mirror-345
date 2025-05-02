import os
import zipfile
import shutil
import gzip
import logging
import pandas as pd
import argparse
from tldr_tools.tldr_download import download_decoys
from tldr_tools.tldr_endpoint import APIManager
from chaff_tools.contaminate import contaminate
from chaff_tools.make_dockopt_ready import process_contaminant_set

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def extract_and_flatten(zip_path, target_dir):
    # Create the target directory if it doesn't exist
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    # Open the ZIP file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Loop through all files in the ZIP
        for file in zip_ref.namelist():
            # Extract each file to the target directory
            extracted_path = zip_ref.extract(file, target_dir)
            # Flatten the directory structure (if any)
            if os.path.isdir(extracted_path):
                continue
            else:
                base_name = os.path.basename(file)
                flattened_path = os.path.join(target_dir, base_name)
                # Move the file to the flat directory
                shutil.move(extracted_path, flattened_path)
    
    # Remove all empty folders
    for root, dirs, files in os.walk(target_dir, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if not os.listdir(dir_path):  # Check if the directory is empty
                os.rmdir(dir_path)  # Remove the empty directory
    
    print(f"Files extracted, flattened, and empty folders removed in: {target_dir}")

def extract_db2_gz(file_path):
    # Ensure the file is a .db2.gz file
    if not file_path.endswith('.db2.gz'):
        print("The provided file is not a .db2.gz file.")
        return

    # Create the extracted folder inside the same directory as the file
    extracted_folder = os.path.join(os.path.dirname(file_path), 'extracted')
    os.makedirs(extracted_folder, exist_ok=True)

    # Output path by removing the .gz extension
    output_path = os.path.join(extracted_folder, os.path.basename(file_path)[:-3])

    # Extract the .gz file
    with gzip.open(file_path, 'rb') as f_in:
        with open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    print(f"Extracted: {file_path} -> {output_path}")

def extract_db2_gz_from_folder(input_folder):
    # Iterate over the files in the given folder
    for file in os.listdir(input_folder):
        if file.endswith('.db2.gz'):
            extract_db2_gz(os.path.join(input_folder, file))


def tldr_batch_download(csv_file, api_manager, output_path=".", overwrite=False):
  df = pd.read_csv(csv_file)

  # Iterate over each row in the DataFrame and download decoys
  for _, row in df.iterrows():
      job_number = str(row['job_no'])  # Ensure the job number is a string
      receptor_folder = row['memo']  # Assuming 'receptor' column has the folder name
      rec_output_path = os.path.join(output_path, receptor_folder, "tldr_download")
      extract_dir = os.path.join(output_path, receptor_folder, "decoys")

      if overwrite or not os.path.exists(rec_output_path):
        print(f"Downloading decoys for job {job_number} in {receptor_folder}")

        # Download the decoys for this job
        download_decoys(api_manager, job_number, rec_output_path, retries=5)

        # Check if decoys_*.zip exist in $receptor_folder and extract to output_folder
        # TODO: Might need to not hard code this, since this might conflict with future modules
        decoys_zip = f"decoys_{job_number}.zip"
        decoys_zip_path= os.path.join(rec_output_path, decoys_zip)
        if os.path.exists(decoys_zip_path):
            extract_and_flatten(decoys_zip_path, extract_dir)
            extract_db2_gz_from_folder(extract_dir)
        else:
            print(f"No {decoys_zip} found for job {job_number} in {rec_output_path}")
      else:
        print(f"Skipping job {job_number} in {receptor_folder} as output already exists")

import os
import logging

def batch_contaminate_and_dockopt_ready(path_to_receptors, path_to_contaminants, rel_path_actives="ligands/extracted", rel_path_contaminants="extracted", output_dir="", seed=None):
    # Ensure output_dir exists if it's provided
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Loop over each receptor in the path_to_receptors
    for root, dirs, files in os.walk(path_to_receptors):
        for receptor in dirs:
            receptor_dir = os.path.join(root, receptor)
            actives_dir = os.path.join(receptor_dir, rel_path_actives)
            contaminants_dir = os.path.join(path_to_contaminants, rel_path_contaminants)

            # Use the receptor directory as the default output if output_dir is not specified
            if not output_dir:
                output_dir = os.path.join(root, receptor)

            # Create output_dir if it doesn't exist
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Loop through different fractions of contaminants
            for frac_contaminants in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
                logging.info(f"Processing receptor: {receptor} with {frac_contaminants * 100}% contaminants")

                # Contaminate with the specified fraction
                contaminate(actives_dir, contaminants_dir, frac_contaminants, output_dir=output_dir, seed=seed)
                
                actives_base = os.path.basename(actives_dir)
                contaminants_base = os.path.basename(contaminants_dir)
                frac_ascii_friendly = str(frac_contaminants).replace('.', 'pt')
                frac_name = f"{frac_ascii_friendly}_{actives_base}_{contaminants_base}"

                # Output YAML and TGZ file names
                output_yaml = os.path.join(output_dir, f"{frac_name}.yaml")
                output_tgz = os.path.join(output_dir, f"{frac_name}.tgz")

                # Process and create the contaminant set
                try:
                    process_contaminant_set(output_yaml, output_tgz)
                    logging.info(f"Successfully processed {frac_name}\n--------------------------")
                except Exception as e:
                    logging.error(f"Error processing {frac_name}: {e}\n--------------------------")




def main():
    #CLI Parser for handling different extraction and download tasks
    parser = argparse.ArgumentParser(description="Utility for extracting and processing molecular data.")

    subparsers = parser.add_subparsers(dest="command")

    # # Extract ZIP files
    # zip_parser = subparsers.add_parser("extract-zip", help="Extract a ZIP file and flatten contents")
    # zip_parser.add_argument("--zip_path", required=True, help="Path to the ZIP file")
    # zip_parser.add_argument("--target_dir", required=True, help="Directory to extract contents into")

    # # Extract a single .db2.gz file
    # db2_parser = subparsers.add_parser("extract-db2", help="Extract a .db2.gz file")
    # db2_parser.add_argument("--file_path", required=True, help="Path to the .db2.gz file")

    # # Extract all .db2.gz files from a folder
    # db2_folder_parser = subparsers.add_parser("extract-db2-folder", help="Extract all .db2.gz files from a folder")
    # db2_folder_parser.add_argument("--input_folder", required=True, help="Folder containing .db2.gz files")

    # TLDR Batch Download
    tldr_parser = subparsers.add_parser("tldr_download", help="Download and process TLDR batch jobs from a CSV")
    tldr_parser.add_argument("--csv_file", required=True, help="Path to the CSV file")
    tldr_parser.add_argument("--output_path", default=".", help="Output directory (default: current directory)")
    tldr_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")

    # Batch Contaminate then DockOpt Ready
    # def batch_contaminate_and_dockopt_ready(path_to_receptors, path_to_contaminants, rel_path_actives="ligands/extracted", rel_path_contaminants="decoys/extracted", output_dir="", random_seed=None):
    contam_dockopt = subparsers.add_parser("make_ready", help="Batch process receptors for DockOpt")
    contam_dockopt.add_argument("--receptor-path", required=True, help="Path to the all the receptor folders (e.g. /path/to/receptors/)")
    contam_dockopt.add_argument("--contaminant-path", required=True, help="Path to the contaminant folders (e.g. /path/to/contaminants/)")
    contam_dockopt.add_argument("--rel-active-path", default="ligands/extracted", help="Relative path to the actives (default: 'ligands/extracted')")
    contam_dockopt.add_argument("--rel-contam-path", default="extracted", help="Relative path to the contaminants (default: 'decoys/extracted')")
    contam_dockopt.add_argument("--output-dir", default="", help="Directory where the results will be saved. Default is the receptor directory.")
    contam_dockopt.add_argument("--seed", type=int, help="Seed for random number generation (optional).")
    
    args = parser.parse_args()

    if args.command == "extract-zip":
        extract_and_flatten(args.zip_path, args.target_dir)
    elif args.command == "extract-db2":
        extract_db2_gz(args.file_path)
    elif args.command == "extract-db2-folder":
        extract_db2_gz_from_folder(args.input_folder)
    elif args.command == "batch-tldr-download":
        api_manager = APIManager()
        tldr_batch_download(args.csv_file, api_manager, args.output_path, args.overwrite)
    elif args.command == "batch-ready":
        batch_contaminate_and_dockopt_ready(
            path_to_receptors=args.receptor_path,
            path_to_contaminants=args.contaminant_path,
            rel_path_actives=args.rel_active_path,
            rel_path_contaminants=args.rel_contam_path,
            output_dir=args.output_dir,
            seed=args.seed
    )
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
