Ookla Open Data and Statistics Canada Internet Analysis
==============================

Comparative analysis of the 
[Statistics Canada National Broadband Internet Service Availability Map](https://www.ic.gc.ca/app/sitt/bbmap/hm.html?lang=eng) 
and the speed test data made available through 
[Ookla’s Open Data Initiative ](https://www.ookla.com/ookla-for-good/open-data).

Project Organization
------------

The project is orgainized into the following directories: `data`, `notebooks`, `scripts`, `src`, and `streamlit`.
`data` contains the downloaded and generated data and files; `notebooks` is for doing investigative 
data analysis and prototyping functions in Jupyter notebooks; `scripts` is a location for python files which 
are run to generate/transform data or do other setup work, etc.; `src` is a directory of common 
python modules for the project; `streamlit` holds python files for a streamlit app. 


Getting Started Instructions 
==============================

Instructions for setting up a python environment and downloading the AWS CLI are listed below.


## Setting Up Environment

### Python Environment

This project uses the python programming language. To install the required python packages 
both a pip `requirements.txt` and a conda `environment.yml` are included in this repository.
It is recommended to use conda to install and create a python environment, as there 
can be issues with ARM based CPUs (e.g. the MacBook Air M1 chips) or on Windows. 

To install anaconda in your remote ubuntu virtual machine (ie. ISAIC or RAC) please follow [these instructions](https://linuxhint.com/install-anaconda-ubuntu-22-04/). When you get to the step to download the Anaconda installer script, use the following command to get the correct script:
```
curl --output anaconda.sh https://repo.anaconda.com/archive/Anaconda3-2022.05-Linux-x86_64.sh
```
Option 2: Instructions for installing conda are available on the [conda docs page](https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html)


After intalling either Anaconda or Miniconda, run the following:
```bash
conda env create -f environment.yml
conda activate ookla-statcan
```

### Install AWS CLI

Install the AWS CLI as shown below. 
```
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
aws --version  # Check install
```
These commands are from [here](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html). 


## Downloading Base Data
These are steps for downloading data to do full analysis of the statcan-ookla datasets. 

### Run Handy Script
With AWS and Anaconda/Miniconda installed, a script called 'data_init.sh' can be run to download 
the data and perform computations to postprocess the data. This can be run 
as follows. Ensure you are in the `ookla-statcan-analysis` directory then:
```
conda activate ookla-statcan
bash data_init.sh
```

The docker container can also be used to download and process the data. To do so 
first start the docker container using `docker compose up -d` then 
find the docker CONTAINER ID using `docker ps`, then use the following command,
replacing the angle brackets and CONTAINER ID with the ID of the running container:
```
docker exec -it <CONTAINER ID> bash data_init.sh
```

### Data Download/Processing

If the script doesn't work, the steps are outlined below one by one.

The AWS command line interface
is needed to easily download the Ookla open data using:
```bash
aws s3 sync --no-sign-request --region=us-west-2 s3://ookla-open-data/shapefiles ./data/ookla-raw
```

After downloading the data, some somewhat long processing needs to be done. First, the global ookla tile information 
needs to be filtered down to just Canada (otherwise the data is far too large to manipulate). This is done with 
the `process_raw_ookla_faster.py` script. 

Subsequently, geometric "overlays" for the ookla tiles and the Statistics Canada boundary files need to be 
calculated to determine which area(s) the tiles should represent when merging with census data or comparing to 
other StatCan references. This can be done with the `create_overlays.py` script. These will take several hours to 
complete. 

Both can be run in sequence from this directory as:
```bash
python scripts/data/process_raw_ookla_faster.py
python scripts/data/create_overalys.py
```

The defined modules/functions in the `src/datasets/loading` directory are designed to download necessary StatCan files as needed.


## Results & App Data

The results from the current analysis perform a complex and long running 
set of calculations based on the geometries and data from both the Ookla and Statistics Canada
data sets. To generate the main resulting geometries and derived internet speed
estimates a sequence of files needs to be run as follows:

1. `data_init.sh` -> `data/ookla-raw/{ookla-global-data-files}`
2. `scripts/data/process_raw_ookla_faster.py` -> `data/ookla-canada-tiles/{Canada-Quarterly-Ookla-Tiles-Subset}`
3. `notebooks/ArbitraryGeomPHHCalc.ipynb` -> `data/processed/geometries/hexagons_w_dissolved_smaller_popctrs.geojson`
4. `notebooks/LastYearOrBestValue.ipynb` -> `data/processed/statistical_geometries/LastFourQuartersOrBestEstimate_On_DissolvedSmallerCitiesHexes.gpkg`

(Needs to be tested, but should work start to finish from scratch; supposed to download StatCan files on its own as needed.)

It is also possible to download the results for the streamlit app using the following:
`curl -O https://swift-yyc.cloud.cybera.ca:8080/v1/AUTH_233e84cd313945c992b4b585f7b9125d/ookla-statcan-analysis/LastFourQuartersOrBestEstimate_On_DissolvedSmallerCitiesHexes.gpkg`
and moving it into the folder `data/processed/statistical_geometries/`.

## Streamlit App
To run the Streamlit App, make sure the last file in the data pipeline 
is downloaded and in the correct folder (`data/processed/statistical_geometries/LastFourQuartersOrBestEstimate_On_DissolvedSmallerCitiesHexes.gpkg`)
and that the python environment has all the necessary packages installed (listed in the requirements.txt or the environment.yml);
and top level directory of this repo needs to be in the PYTHONPATH (`export PYTHONPATH="${PYTHONPATH}:$(pwd)"`). 
Then run `streamlit run streamlit/app.py`, which will start the app, defaulting to port 8501. It is 
not a long-running background service (like Jupyter), so if the terminal running it is closed 
the App will stop running. There's a few deployment options listed in the 
[documentation](https://docs.streamlit.io/knowledge-base/tutorials/deploy); the EC2 instance blog post suggests tmux which is pretty simple.

The output data for the streamlit app can be downloaded [here](https://swift-yyc.cloud.cybera.ca:8080/v1/AUTH_233e84cd313945c992b4b585f7b9125d/ookla-statcan-analysis/LastFourQuartersOrBestEstimate_On_DissolvedSmallerCitiesHexes.gpkg) on RAC 
object storage. The binary geopackage file 
must be place in the folder indicated above in the data directory. 
