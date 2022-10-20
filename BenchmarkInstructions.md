# Benchmarking
Instructions for using this dataset as a timing benchmark. These instructions
may only work on Ubuntu. See the README file for additional 
install resource instructinos. 

The python modules incorporate a caching-like behaviour, so rerunning the scripts 
without removing all created data files will appear to have faster execution.
Delete all files in the data directory EXCEPT the git tracked `data/boundaries/statcan_links.json` 
file. 

If the repository hasn't been cloned, 
do so using below commands:

```bash
git clone https://github.com/cybera/ookla-statcan-analysis.git
```

## Install Tools and Python Packages
Python and AWS CLI need to be setup (these can be run from the home directory):

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
aws --version  # Check install
rm awscliv2.zip

sudo apt update
mkdir ./temp
cd temp
curl --output anaconda.sh https://repo.anaconda.com/archive/Anaconda3-2022.05-Linux-x86_64.sh
bash anaconda.sh # will require terminal input during installation: type yes; hit enter to confirm location; type yes
cd ..
rm temp -rf
source ~/.bashrc
conda update conda -y

conda env create -f environment.yml #this may also take a while
conda activate ookla-statcan 
```


## Run Benchmark
Below pipes redirects terminal outputs to a file (overwriting if it exists) `benchmark.txt`.
The & at command end runs the the script in the background and disown prevents 
logging out from killing the process. The script may take 20 minutes to a couple hours to 
complete. 

The outputs from the script have timing information both at the end (total) and 
interleaved between sections of code output. 

```bash
bash data_init_benchmark.sh &> benchmark.txt &
disown
```

A longer benchmarking activity is possible using the normal `default_init.sh` script instead 
of the modified script listed above. (Which limits shapfeles downloaded from AWS and 
runs fewer overlay calculations.)