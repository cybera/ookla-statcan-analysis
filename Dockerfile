# Base image of your application
FROM jupyter/datascience-notebook
ARG NB_USER="jovyan"

USER root
ENV HOME="/home/${NB_USER}"

COPY --chown=${NB_UID}:${NB_GID} requirements.txt /tmp/
RUN mamba install --yes --file /tmp/requirements.txt && \
    mamba clean --all -f -y
    
RUN pip install awscli

RUN chown -R ${NB_USER} /home/jovyan

RUN wget https://repo.anaconda.com/archive/Anaconda3-2022.10-Linux-x86_64.sh -O /root/anaconda.sh
RUN bash /root/anaconda.sh -b -p /root/anaconda
RUN eval "$(/root/anaconda/bin/conda shell.bash hook)"
RUN source /root/anaconda/etc/profile.d/conda.sh && \
    export PATH=/root/anaconda/bin:$PATH >> /root/.bashrc && \
    source /root/.bashrc

   #conda init bash

RUN chown -R ${NB_USER} /home/jovyan

ENV PYTHONPATH="/home/jovyan:."
