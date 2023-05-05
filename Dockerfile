

# Base image of your application
FROM jupyter/datascience-notebook

# Copy requirements.txt file into your image
COPY /requirements.txt /

# Install packages from requirements.txt file
#ENV GDAL_VERSION=1.8
RUN pip install -r /requirements.txt
# RUN mamba install --channel conda-forge --quiet --yes --file /requirements.txt

RUN pip install awscli

# COPY /data_init.sh /home/jovyan/data_init.sh
ENV PYTHONPATH="/home/jovyan:."