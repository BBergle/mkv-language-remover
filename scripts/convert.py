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
    for root, _, files in os.walk(BASE_DIR):
        for file in files:
            if any(file.endswith(extension) for extension in SUPPORTED_FORMATS):
                count += 1
    return count

def print_processing_message(filepath, current_count, total_count):
    """
    Prints a processing message for the current movie being processed.
    """
    print(f"Processing movie {current_count + 1} out of {total_count}: {filepath}", flush=True)

movie_count = 0  # Initialize movie counter
total_movies = count_movies_to_process()

for root, _, files in os.walk(BASE_DIR):
    for file in files:
        if any(file.endswith(extension) for extension in SUPPORTED_FORMATS):
            filepath = os.path.join(root, file)
            base_file_name = os.path.splitext(file)[0]
            temp_mkv_filepath = os.path.join(root, "temp_" + base_file_name + NEW_EXTENSION)

            mkvmerge_command = ['mkvmerge', '-o', temp_mkv_filepath, filepath]

            print_processing_message(filepath, movie_count, total_movies)

            with subprocess.Popen(mkvmerge_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
                for line in process.stderr:
                    pass

                process.wait()

                if process.returncode == 0:
                    print(f"Successfully remuxed to: {temp_mkv_filepath}", flush=True)
                    os.remove(filepath)
                    final_mkv_filepath = os.path.join(root, base_file_name + NEW_EXTENSION)
                    os.rename(temp_mkv_filepath, final_mkv_filepath)
                    print(f"Renamed {temp_mkv_filepath} to {final_mkv_filepath}", flush=True)
                else:
                    print(f"Error remuxing {filepath}. Error message: {process.stderr.read()}", flush=True)

            movie_count += 1
            if movie_count >= total_movies:
                print("All movies processed!", flush=True)
                break
