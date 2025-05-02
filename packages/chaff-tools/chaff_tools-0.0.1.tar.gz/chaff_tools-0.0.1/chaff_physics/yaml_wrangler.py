import yaml
import os
import logging

def save_to_yaml(selected_actives, selected_contaminants, nonselected_actives, nonselected_contaminants, random_seed, output_file):
    """Save the results to a YAML file with full absolute paths and random seed information."""
    logging.info(f"Saving results to {output_file}")
    data = {
        'selected_actives': selected_actives,
        'selected_contaminants': selected_contaminants,
        'nonselected_actives': nonselected_actives,
        'nonselected_contaminants': nonselected_contaminants,
        'random_seed': random_seed,  # Include the seed for reproducibility
    }
    
    try:
        with open(output_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
        logging.info(f"Results successfully saved to {output_file}")
    except Exception as e:
        logging.error(f"Error while saving YAML: {e}")
        raise

def load_from_yaml(yaml_file):
    """Load the data from a YAML file and return it as Python lists."""
    if not os.path.exists(yaml_file):
        logging.error(f"YAML file not found: {yaml_file}")
        raise FileNotFoundError(f"YAML file not found: {yaml_file}")
    
    try:
        with open(yaml_file, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        
        required_keys = [
            'selected_actives',
            'selected_contaminants',
            'nonselected_actives',
            'nonselected_contaminants'
        ]
        
        for key in required_keys:
            if key not in data:
                logging.error(f"Missing expected key: {key}")
                raise ValueError(f"Missing expected key: {key}")
            if not isinstance(data[key], list):
                logging.error(f"Expected list for {key}, got {type(data[key])}")
                raise ValueError(f"Expected list for {key}, got {type(data[key])}")
        
        selected_actives = data.get('selected_actives', [])
        selected_contaminants = data.get('selected_contaminants', [])
        nonselected_actives = data.get('nonselected_actives', [])
        nonselected_contaminants = data.get('nonselected_contaminants', [])
        
        logging.info("YAML file loaded successfully.")
        return selected_actives, selected_contaminants, nonselected_actives, nonselected_contaminants
    
    except yaml.YAMLError as e:
        logging.error(f"Error reading YAML file: {e}")
        raise
    except Exception as e:
        logging.error(f"An error occurred while loading the YAML: {e}")
        raise

    
# Function to read and extract compound_name and SMILES from a .db2 file
def extract_db2_data(db2_path):
    with open(db2_path, 'r') as f:
        lines = f.readlines()
        
    # Extract compound_name (first line) and SMILES (third line)
    compound_name = lines[0].split()[1]  # second item on the first line
    smiles = lines[2].strip()  # third line, strip extra spaces/newlines
    
    return compound_name, smiles

# Function to read the YAML file
def read_yaml(yaml_path):
    with open(yaml_path, 'r') as f:
        return yaml.load(f, Loader=yaml.FullLoader)

# Function to process and save data to Parquet files
def db2_to_pq(yaml_path):
    # Read the YAML file
    data = read_yaml(yaml_path)
    
    # Initialize lists for selected actives and contaminants
    selected_actives = []
    selected_contaminants = []
    
    # Process each file in the YAML nonselected_contaminants and nonselected_actives lists
    for db2_path in data.get('nonselected_contaminants', []):
        compound_name, smiles = extract_db2_data(db2_path)
        selected_contaminants.append((compound_name, smiles))
    
    for db2_path in data.get('nonselected_actives', []):
        compound_name, smiles = extract_db2_data(db2_path)
        selected_actives.append((compound_name, smiles))
    
    # Create Pandas DataFrames for each category
    df_contaminants = pd.DataFrame(selected_contaminants, columns=['compound_name', 'smiles'])
    df_actives = pd.DataFrame(selected_actives, columns=['compound_name', 'smiles'])
    
    # Save as Parquet files
    table_contaminants = pa.Table.from_pandas(df_contaminants)
    pq.write_table(table_contaminants, 'selected_contaminants.parquet')
    
    table_actives = pa.Table.from_pandas(df_actives)
    pq.write_table(table_actives, 'selected_actives.parquet')
    
    print("Parquet files created: 'selected_contaminants.parquet' and 'selected_actives.parquet'")