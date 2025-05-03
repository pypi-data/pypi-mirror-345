

# EMBER Feature Extraction

![CI status](https://github.com/malware-concept-drift-detection/ember/actions/workflows/check.yml/badge.svg) 
![Version](https://img.shields.io/github/v/release/malware-concept-drift-detection/ember/ember?style=plastic)



This repository allows the user to easily create a dataset using EMBER features, starting from a collection of PE files.

Setup the directory of PE executables, configure the Docker Compose file and deploy the pipeline. A final `csv` file with all the features will be created.

If you want to work with EMBER2017 dataset (containing features from 1.1 million PE files scanned in or before 2017) or the EMBER2018 dataset (containing features from 1 million PE files scanned in or before 2018), please refer to the official repository.

Details of the selected features is available here: [https://arxiv.org/abs/1804.04637](https://arxiv.org/abs/1804.04637)


## Prerequisites

- Make sure you have a running and active version of [Docker](https://docs.docker.com/engine/install/).

## Usage:

1. Clone the repository and change directory:
    ```bash
    git clone git@github.com:w-disaster/ember.git && cd ember
    ```

2. Setup the directory containing PE files. The directory should have the following structure:

    ```plaintext
    your_base_dir/
    ├── malware_family_0/
    │   ├── id_malware_sample_0_0.exe
    │   ├── id_malware_sample_0_1.exe
    ├── malware_family_1/
    │   ├── id_malware_sample_1_0.exe
    └── ...
    ```

    Each PE filename will be used as the sample index in the final dataset.

    The directory structure doesn't change if you want to do malware detection: simply create two directories `benign` and `malicious` as the malware families.

3. Configure `docker-compose.yaml`:
    1. Set the number of processes `N_PROCESSES` for parallel processing;
    2. Change the volume source point of the base directory with PE files (`your_base_dir`). Default is `/home/luca/WD/NortonDataset670/MALWARE/`;
    3. Set the directory volume where the final dataset will be saved (default `./dataset/`)


4. *Deploy* the pipeline:

    ```base
    docker compose up
    ```

5. Check out the dataset with filename `malware_ember_features.csv` inside the configured directory. The dataset will have all the columns named.

    Besides the features it contains a column `sha256` and a `family` column. The first one is the PE file id which has specifically been used in our case, while the `family` is the malware family of the corresponding sample. 
    If you use another PE id or do malware detection, consider to change these column names afterwards.

