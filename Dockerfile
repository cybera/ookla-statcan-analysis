

# Base image of your application
FROM jupyter/datascience-notebook

# Copy requirements.txt file into your image
COPY --chown=${NB_UID}:${NB_GID} requirements.txt /tmp/
RUN mamba install --yes --file /tmp/requirements.txt && \
    mamba clean --all -f -y && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

# Install packages from requirements.txt file
# ENV GDAL_VERSION=1.8
# RUN pip install -r /requirements.txt
# RUN mamba install --channel conda-forge --quiet --yes --file /requirements.txt

RUN pip install awscli

COPY /data_init.sh /home/jovyan/data_init.sh
ENV PYTHONPATH="/home/jovyan:."
