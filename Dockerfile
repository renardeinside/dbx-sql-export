FROM continuumio/miniconda3:4.9.2

ARG DRIVER_MAJOR_VERSION="2.6.19"
ARG DRIVER_MINOR_VERSION=1033
ARG BUCKET_URI="https://databricks-bi-artifacts.s3.us-east-2.amazonaws.com/simbaspark-drivers/odbc"

ENV DRIVER_FULL_VERSION=${DRIVER_MAJOR_VERSION}.${DRIVER_MINOR_VERSION}
ENV FOLDER_NAME=SimbaSparkODBC-${DRIVER_FULL_VERSION}-Debian-64bit
ENV ZIP_FILE_NAME=${FOLDER_NAME}.zip

RUN mkdir /opt/drivers
WORKDIR /opt/drivers


RUN apt-get update --allow-releaseinfo-change -y && apt-get install -y unzip unixodbc-dev unixodbc-bin unixodbc make procps

RUN wget \
    ${BUCKET_URI}/${DRIVER_MAJOR_VERSION}/${ZIP_FILE_NAME}

RUN unzip ${ZIP_FILE_NAME} && rm -f ${ZIP_FILE_NAME}

RUN apt-get install -y ./simbaspark_*

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app



ADD environment.yml environment.yml

RUN conda env create -f environment.yml
ENV PATH /opt/conda/envs/dbx-sql-cli/bin:$PATH
RUN /bin/bash -c "source activate dbx-sql-cli"

ADD entrypoint.py entrypoint.py

ENTRYPOINT ["python"]

