# Benchmarking
Instructions for using this dataset as a timing benchmark. If the repository hasn't been cloned, 
do so using below commands:

```bash
git clone https://github.com/cybera/ookla-statcan-analysis.git
cd ookla-statcan-analysis
```

## Install Tools and Python Packages
Python and AWS CLI need to be setup:

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
aws --version  # Check install

sudo apt update
mkdir ./temp
cd temp
curl --output anaconda.sh https://repo.anaconda.com/archive/Anaconda3-2022.05-Linux-x86_64.sh
bash anaconda.sh
cd ..
rm temp -rf
source ~/.bashrc
conda update conda 

conda env create -f environment.yml
conda activate ookla-statcan 
```


## Run Benchmark

```bash
bash data_init.sh &> benchmark.txt &
disown
```