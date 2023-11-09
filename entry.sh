#!/bin/bash

printf "\033[0;32mStarting Container...\033[0m\n"

# Update pip and install required package
printf "\033[0;32mUpgrading pip...\033[0m\n"
pip install --upgrade pip
printf "\033[0;32mInstalling dependencies...\033[0m\n"
pip install orjson
# Fetch the convert option from the environment variable
CONVERT_ENV=$(printenv CONVERT)
# Fetch the remove languages option from the environment variable
REMOVE_LANGUAGES_ENV=$(printenv REMOVE_LANGUAGES)

# Check if CONVERT_ENV is set to 'True' (case-insensitive)
if [[ "$CONVERT_ENV" =~ ^(True|true|TRUE)$ ]]; then
    # Run the Python script
    printf "\033[1;33mINFO: Converting all m2ts and mp4 files to mkv\n\n\033[0m"
    python3 convert.py || printf "\033[0;32mPython script failed with exit code $?\033[0m\n"
else
    # If CONVERT is not 'True', skip running the script and print a message
    printf "\033[0;33mCONVERT environment variable is set to 'False', skipping Python script execution.\033[0m\n"
fi

 # Check if REMOVE_LANGUAGES_ENV is set to 'True' (case-insensitive)
if [[ "$REMOVE_LANGUAGES_ENV" =~ ^(True|true|TRUE)$ ]]; then
    # Run the Remove_Languages Python script
    printf "\033[1;33mINFO: Removing Languages\n\n\033[0m"
    python3 Remove_Languages.py || printf "\033[0;32mPython script failed with exit code $?\033[0m\n"
else
    # If REMOVE_LANGUAGES is not 'True', skip running the script and print a message
    printf "\033[0;33mREMOVE_LANGUAGES environment variable is set to 'False', skipping Remove_Languages.py script execution.\033[0m\n"
fi

printf "\033[0;32mProcessing has finished, container is exiting\033[0m\n"
