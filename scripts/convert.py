"""
This script processes movie files in a specified directory, converting them to MKV format.
"""

import os
import subprocess

# Constants
BASE_DIR = '/movies'
SUPPORTED_FORMATS = ['.m2ts', '.mp4']  # Add or remove formats as needed
NEW_EXTENSION = '.mkv'

def count_movies_to_process():
    """
    Counts the number of movies in the BASE_DIR that are in SUPPORTED_FORMATS.
    """
    count = 0
    for root_dir, _, files_list in os.walk(BASE_DIR):
        for file_name in files_list:
            if any(file_name.endswith(ext) for ext in SUPPORTED_FORMATS):
                count += 1
    return count

def print_processing_message(filepath, current_count, total_count):
    """
    Prints a processing message for the current movie being processed.
    """
    print(f"Processing movie {current_count + 1} out of {total_count}: {filepath}",
          flush=True)

MOVIE_COUNT = 0  # Initialize movie counter
TOTAL_MOVIES = count_movies_to_process()

for root_dir, _, files_list in os.walk(BASE_DIR):
    for file_name in files_list:
        if any(file_name.endswith(ext) for ext in SUPPORTED_FORMATS):
            file_path = os.path.join(root_dir, file_name)
            base_file_name = os.path.splitext(file_name)[0]
            temp_mkv_filepath = os.path.join(root_dir, "temp_" + base_file_name + NEW_EXTENSION)

            mkvmerge_command = ['mkvmerge', '-o', temp_mkv_filepath, file_path]

            print_processing_message(file_path, MOVIE_COUNT, TOTAL_MOVIES)

            with subprocess.Popen(mkvmerge_command, stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE, text=True) as process:
                for _ in process.stderr:
                    pass

                process.wait()

                if process.returncode == 0:
                    print(f"Successfully remuxed to: {temp_mkv_filepath}", flush=True)
                    os.remove(file_path)
                    final_mkv_filepath = os.path.join(root_dir, base_file_name + NEW_EXTENSION)
                    os.rename(temp_mkv_filepath, final_mkv_filepath)
                    print(f"Renamed {temp_mkv_filepath} to {final_mkv_filepath}", flush=True)
                else:
                    error_msg = process.stderr.read()
                    print(f"Error remuxing {file_path}. Error message: {error_msg}", flush=True)

            MOVIE_COUNT += 1
            if MOVIE_COUNT >= TOTAL_MOVIES:
                print("All movies processed!", flush=True)
                break
