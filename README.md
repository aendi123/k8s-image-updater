# k8s-image-updater

## Overview
`k8s-image-updater` is a tool designed to automate the process of updating container image tags in Kubernetes resource YAML files. It supports various Kubernetes resources, including Deployments, DaemonSets, and StatefulSets. The tool automatically fetches the latest image tags and optionally updates the YAML files accordingly. Users can configure regex patterns to exclude specific files and folders, and define tag patterns to match their requirements.

## Dependencies
- `regctl` must be installed, and you must be logged in to the registries from which you want to fetch new tags.
- Python and `conda` must be installed on your system.

## Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/aendi123/k8s-image-updater.git
    cd k8s-image-updater
    ```

2. Create the conda environment:
    ```sh
    conda env create -f environment.yaml
    conda activate k8s-image-updater
    ```

## Usage
```sh
> python3 k8s_image_updater/imageupdater.py -h
usage: imageupdater.py [-h] [-c CONFIGCSV] [-e EXCLUDE] [-w] [path]

positional arguments:
  path                          path to search for YAML files

options:
  -h, --help                    show this help message and exit
  -c, --configcsv CONFIGCSV     provide CSV file with image names and their regex the tag has to match
  -e, --exclude EXCLUDE         provide regex pattern to exclude while searching for YAML files
  -w, --write-newest            enable writing the newest tag into the YAML files
```

## Configuration
### CONFIGCSV
The format of this CSV must be:
```csv
registry/imagename;regex
```
Example:
```csv
docker.io/haproxy;^\d+\.\d+\.\d+-alpine$
```
### EXCLUDE
Example:
```sh
-e '.*archive.*'
```