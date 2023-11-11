#!/bin/bash

printf "\033[0;32mStarting Container...\033[0m\n"

# Update pip and install required packages from requirements.txt
printf "\033[0;32mUpgrading pip...\033[0m\n"
pip install --upgrade pip
printf "\033[0;32mInstalling dependencies from requirements.txt...\033[0m\n"
pip install -r requirements.txt

# Fetch the convert option from the environment variable
CONVERT_ENV=$(printenv CONVERT)
# Fetch the remove languages option from the environment variable
REMOVE_LANGUAGES_ENV=$(printenv REMOVE_LANGUAGES)

# Function to execute Python script and capture errors
run_python_script() {
    local script_name=$1
    error=$(python3 "$script_name" 2>&1)
    exit_code=$?

    if [ $exit_code -ne 0 ]; then
        printf "\033[0;31mPython script '$script_name' failed with the following error:\n$error\033[0m\n"
        return $exit_code
    fi
}

# Check if CONVERT_ENV is set to 'True' (case-insensitive)
if [[ "$CONVERT_ENV" =~ ^(True|true|TRUE)$ ]]; then
    printf "\033[1;33mINFO: Converting all m2ts and mp4 files to mkv\n\n\033[0m"
    run_python_script convert.py
else
    printf "\033[0;33mCONVERT environment variable is set to 'False', skipping Python script execution.\033[0m\n"
fi

# Check if REMOVE_LANGUAGES_ENV is set to 'True' (case-insensitive)
if [[ "$REMOVE_LANGUAGES_ENV" =~ ^(True|true|TRUE)$ ]]; then
    printf "\033[1;33mINFO: Removing Languages\n\n\033[0m"
    run_python_script remove_languages.py
else
    printf "\033[0;33mREMOVE_LANGUAGES environment variable is set to 'False', skipping Remove_Languages.py script execution.\033[0m\n"
fi

printf "\033[0;32mProcessing has finished, container is exiting\033[0m\n"
