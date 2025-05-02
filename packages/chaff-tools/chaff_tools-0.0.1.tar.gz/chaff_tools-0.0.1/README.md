## What is it?

TBD

## Installation

Installation made easy. chaff-tools is pip installable. Please make sure you have Python 3.6 installed.

```shell-session
$ pip install chaff-tools
```

## Usage
Miscallenous tools are used 

```shell-session
# Extract a ZIP file and flatten contents
$ chaff-physics extract-zip
```

```shell-session
# Extract a .db2.gz file
$ chaff-physics extract-db2
```

```shell-session
# Extract all .db2.gz files from a folder
$ chaff-physics extract-db2-folder
```

```shell-session
# Download and process TLDR batch jobs from a CSV
$ extract-db2-folder
```

```shell-session
# Extract all .db2.gz files from a folder
$ extract-db2-folder
```

## Random split

The cp-random-split tool allows you to perform a realistic, clustering-based train/test split on a dataset of molecular SMILES, as described in the Martin et al. paper. This helps preserve chemical diversity between sets, unlike purely random splits.


### Command

```bash
cp-random-split \
  --input-file compounds.csv \
  --smiles-col 0 \
  --frac-train 0.8 \
  --exact \
  --method Auto \
  --output results/some_split
```

| Flag                 | Description                                                                 |
|----------------------|-----------------------------------------------------------------------------|
| `-i`, `--input-file` | Path to the input CSV/TSV file containing SMILES.                           |
| `-s`, `--smiles-col` | Index of the column containing SMILES (default: `0`).                       |
| `-f`, `--frac-train`  | Fraction of the dataset to use for training (e.g. `0.8`).                   |
| `--exact`            | If set, may split a cluster to achieve the exact fraction.                  |
| `-m`, `--method`     | Clustering method: `Auto`, `TB` (Butina), or `Hierarchy` (default: `Auto`). |
| `-o`, `--output`     | Base path for output files; `_train.csv` and `_test.csv` will be created.    |


## Co-existence with tldr-tools

tldr-tools can be synergistically used with chaff-tools to run larger-scale pipelines.


tldr-batch          


```shell-session
$ chaff-contaminate --actives_dir path/to/actives --contaminants_dir path/to/contaminants --frac_contaminate 0.2 --output path/to/output.yaml --seed 42
```

Arguments:

    --actives_dir: Directory containing .db2 files for actives.
    --contaminants_dir: Directory containing .db2 files for contaminants.
    --frac_contaminate: Fraction of actives that should be contaminated (value between 0 and 1).
    --output: Path where the YAML file with results will be saved.
    --seed: (Optional) Random seed for reproducibility.

For example, if running decoy generation is desired:

```shell-session
tldr-submit --module decoys --activesism input_files/actives.ism --decoygenin input_files/decoy_generation.in --memo "Decoy generation for ADA, replicate 1"
```

Or, you can build a ligand using DOCK3.8:

```shell-session
tldr-submit --module build --input chaff_tools/aggregator_advisor_hf_test.txt --memo "aa_hf_test"
```

Documenting runs with the optional memo parameter is encouraged.

Pass in a job number to check on a status of a run:
```shell-session
tldr-status --job-number 14886
```

Once a run is successful, you can download the output to a local directory:

```shell-session
tldr-download --job-number 14886 --output some_folder
```

## Does tldr-tools work in Colab and Jupyter Notebook?

Yep, you use chaff-tools as follow:

```shell-session
TBD
```
