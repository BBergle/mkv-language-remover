# Use a base image with mkvtoolnix and jq pre-installed
FROM jlesage/mkvtoolnix:latest

# Install mediainfo, Python, pip, and other required tools
RUN apk --no-cache add mediainfo python3 py3-pip git build-base bash

# Define environment variable for the input and scripts folder
ENV MOVIES_FOLDER=/movies
ENV SCRIPTS_FOLDER=/scripts
ENV PYTHONUNBUFFERED=1

#User Defined Vairables
ENV CONVERT=
ENV REMOVE_LANGUAGES=
ENV LANGUAGES=
ENV REMOVE_COMMENTARY=
ENV TEST= 

# Create a directory for the input folder and scripts
RUN mkdir -p ${MOVIES_FOLDER}
RUN mkdir -p ${SCRIPTS_FOLDER}

# Set the working directory to the scripts folder
WORKDIR ${SCRIPTS_FOLDER}

# Copy the scripts directory contents to the container's scripts directory
COPY ./scripts/* ${SCRIPTS_FOLDER}/

# Make the scripts executable if necessary
RUN chmod +x ${SCRIPTS_FOLDER}/*

# Make the movies folder a mountable volume
VOLUME ["/movies"]

# Copy the entry.sh script into the container
COPY entry.sh /entry.sh

# Ensure the script is executable
RUN chmod +x /entry.sh

# Set the script as the default way to run the container
ENTRYPOINT ["/entry.sh"]
