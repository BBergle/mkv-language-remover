# pylint: disable=redefined-outer-name

import os
import subprocess

# Constants
BASE_DIR = '/movies'
SUPPORTED_FORMATS = ['.m2ts', '.mp4']  # Add or remove formats as needed
NEW_EXTENSION = '.mkv'

# New boolean variable
TEST_ENV = os.getenv("TEST") == "True" # Set to True to only count movies without processing

def count_movies_to_process():
    """
    Counts the number of movies in the BASE_DIR that are in SUPPORTED_FORMATS.
    """
    count = 0
    for _, _, files in os.walk(BASE_DIR):
        for file_name in files:
            if any(file_name.endswith(ext) for ext in SUPPORTED_FORMATS):
                count += 1
    return count

def print_processing_message(filepath, current_count, total_count):
    """
    Prints a processing message for the current movie being processed.
    """
    print(f"\033[94mProcessing movie\033[0m {current_count + 1} out of {total_count}: {filepath}\n", flush=True)

TOTAL_MOVIES = count_movies_to_process()

# Check if test is True, if so, print the count and exit
if TEST_ENV:
    print(f"The test variable is true, movies will not process.\n"
        f"\033[93mTotal movies to be processed:\033[0m {TOTAL_MOVIES}", flush=True)

else:
    MOVIE_COUNT = 0  # Initialize movie counter
    for path, _, file_list in os.walk(BASE_DIR):
        for file_name in file_list:
            if any(file_name.endswith(ext) for ext in SUPPORTED_FORMATS):
                file_path = os.path.join(path, file_name)
                base_file_name = os.path.splitext(file_name)[0]
                temp_mkv_filepath = os.path.join(path, "temp_" + base_file_name + NEW_EXTENSION)

                mkvmerge_command = ['mkvmerge', '-o', temp_mkv_filepath, file_path]

                print_processing_message(file_path, MOVIE_COUNT, TOTAL_MOVIES)

                with subprocess.Popen(mkvmerge_command, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, text=True) as process:
                    for _ in process.stderr:
                        pass

                    process.wait()

                    if process.returncode == 0:
                        print(f"\033[92mSuccessfully remuxed to:\033[0m {temp_mkv_filepath}", flush=True)
                        os.remove(file_path)
                        final_mkv_filepath = os.path.join(path, base_file_name + NEW_EXTENSION)
                        os.rename(temp_mkv_filepath, final_mkv_filepath)
                        print(f"Renamed {temp_mkv_filepath} to {final_mkv_filepath}", flush=True)
                    else:
                        error_msg = process.stderr.read()
                        print(f"\033[91mError remuxing\033[0m {file_path}. Error message: {error_msg}", flush=True)


                MOVIE_COUNT += 1
                if MOVIE_COUNT >= TOTAL_MOVIES:
                    print("\033[92mAll movies processed!\033[0m", flush=True)
                    break