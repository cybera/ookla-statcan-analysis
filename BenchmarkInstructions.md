# Benchmarking
Instructions for using this dataset as a timing benchmark. If the repository hasn't been cloned, 
do so using below commands:

```bash
git clone https://github.com/cybera/ookla-statcan-analysis.git
```

## Install Tools and Python Packages
Python and AWS CLI need to be setup:

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

conda env create -f environment.yml
conda activate ookla-statcan 
```


## Run Benchmark
Below pipes redirects terminal outputs to a file (overwriting if it exists) `benchmark.txt`.
The & at command end runs the the script in the background and disown prevents 
logging out from killing the process. The script may take 20 minutes to a couple hours to 
complete. 

```bash
bash data_init_benchmarking.sh &> benchmark.txt &
disown
```