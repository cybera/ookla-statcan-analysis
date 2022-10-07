Ookla Open Data and Statistics Canada Internet Analysis(CBS)
==============================

Comparative analysis of the 
[Statistics Canada National Broadband Internet Service Availability Map](https://www.ic.gc.ca/app/sitt/bbmap/hm.html?lang=eng) 
and the speed test data made available through 
[Ookla’s Open Data Initiative ](https://www.ookla.com/ookla-for-good/open-data).

Project Organization
------------
Folder structure or organziation for this project:
```
├── README.md                       <- The top-level README for developers using this project.
├── .gitignore                      <- Ignores files that shouldn't go into git (e.g. ./data/).
│
├── report                          <- The final report, figures, and any reference materials.
│
├── docker-compose.yml              <- Container instructions used when running docker-compose.
├── docker
│   ├── Dockerfile                  <- Dockerfile for building container.
│   └── requirements.txt            <- Specifies additional python packages to install in container.
│
├── data
│   ├── processed                   <- The final, canonical data sets for modeling.
│   └── raw                         <- The original, immutable data dump. (make changes to copies only.)
│
├── models                          <- Trained and serialized models, model predictions, or model summaries.
│
├── notebooks                       <- Jupyter notebooks. Naming convention is a number (for ordering),
│   │                                  the creator's initials, and a short `-` delimited description.
│   └── 0.1-zs-basic-intro-nb.ipynb <- An example notebook.
│
└── scripts                   
     ├── data                       <- Scripts to download or generate data.
     ├── features                   <- Scripts to turn raw data into features for modeling.
     ├── models                     <- Scripts to train models and then use trained models to make.
     └── visualization              <- Scripts to create exploratory and results oriented visualizations.
```


You can regenerate similar on *nix systems using:
     ```$tree -a -I '.git|.gitkeep|__init__.py'```

<p><small>Project layout based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>


Getting Started Instructions 
==============================

Instructions for setting up a python environment and downloading the AWS CLI are listed below.

Python Environment
------------------

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

Install AWS CLI
---------------
Install the AWS CLI as shown below. 
```
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
aws --version  # Check install
```
These commands are from [here](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html). 

Run Handy Script
----------------
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

Data Download/Processing
------------------------
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



Docker Setup
--------------------
To be completed...
<!-- 
### Installation
Before proceeding further, please install [Docker](https://www.docker.com/) following the instructions provided in the [link here](https://docs.docker.com/get-docker/) for your choice of operating system. 

### Setup 

From this project folder run the following command in your terminal to build and deploy the JupyterLab container:
```
docker-compose up --build
```
Use `CTRL + C` to stop JupyterLab and exit the docker container. 

To run the container in detached mode add `-d` as follows:
```
docker-compose up --build -d
```

If you have successfully built and deployed the JupyterLab image container using either of the above commands, you can access the web interface of the JupyterLab at 
```
http://localhost:8888
```

You might be prompted to enter the token while accessing the `http://localhost:8888`. The token can be obtained from the logs of the running JupyterLab container as follows. 

```
docker logs <container-id>
```

To view the list of all the containers and get the container id of the JupyterLab, run 
```
docker ps -a
``` -->

