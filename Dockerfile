

# Base image of your application
FROM jupyter/datascience-notebook
ARG NB_USER="jovyan"
ARG NB_UID="1000"
ARG NB_GID="1000"
RUN mkdir /home/jovyan/.local

ENV JUPYTER_ALLOW_INSECURE_WRITES=0
# USER root
ENV HOME="/home/${NB_USER}"
# RUN chown 1000:100 /home/jovyan/.local
# RUN chmod 775 /home/jovyan/.local
# RUN whoami
# RUN ls -ld ~/.local
# RUN sudo chown -R ${NB_USER}:root /home/jovyan
# RUN sudo chmod -R 777 /home/jovyan/.local
# USER ${NB_USER}
# Copy requirements.txt file into your image
# COPY /requirements.txt /
# USER ${NB_UID}:100
COPY --chown=${NB_UID}:${NB_GID} requirements.txt /tmp/
#RUN mamba install --yes --file /tmp/requirements.txt && \
#    mamba clean --all -f -y && \
#    fix-permissions "${CONDA_DIR}" && \
#    fix-permissions "/home/${NB_USER}"

# Install packages from requirements.txt file
#ENV GDAL_VERSION=1.8
#RUN pip install -r /requirements.txt
# RUN mamba install --channel conda-forge --quiet --yes --file /requirements.txt

# USER root
# RUN sudo chown -R ${NB_USER}:${NB_USER} /home/jovyan/.local
# RUN sudo chmod -R 777 /home/jovyan
# USER ${NB_USER}

# RUN pip install awscli

#?
COPY /data_init.sh /home/jovyan/data_init.sh
ENV PYTHONPATH="/home/jovyan:."

# RUN sudo chmod -R 777 .local
