"""
This script processes movie files in a specified directory, converting them to MKV format.
"""
# pylint: disable=redefined-outer-name

import os
import subprocess

# Set the base directory to the movies folder
base_dir = '/movies'

# Supported video formats for conversion
supported_formats = ['.m2ts', '.mp4']  # Add or remove formats as needed

def count_movies_to_process():
    count = 0
    for _, _, files in os.walk(base_dir):
        for file_name in files:
            if any(file_name.endswith(ext) for ext in supported_formats):
                count += 1
    return count

def print_processing_message(filepath, movie_count, total_movies):
    print(f"Processing movie {movie_count + 1} out of {total_movies}: {filepath}", flush=True)

movie_count = 0  # Initialize movie counter
total_movies = count_movies_to_process()

for path, _, file_list in os.walk(base_dir):
    for file_name in file_list:
        if any(file_name.endswith(ext) for ext in supported_formats):
            file_path = os.path.join(path, file_name)
            base_file_name = os.path.splitext(file_name)[0]
            new_extension = '.mkv'
            temp_mkv_filepath = os.path.join(path, "temp_" + base_file_name + new_extension)

            mkvmerge_command = ['mkvmerge', '-o', temp_mkv_filepath, file_path]

            print_processing_message(file_path, movie_count, total_movies)

            with subprocess.Popen(mkvmerge_command, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True) as process:
                for _ in process.stderr:
                    pass

                process.wait()

                if process.returncode == 0:
                    print(f"Successfully remuxed to: {temp_mkv_filepath}", flush=True)
                    os.remove(file_path)
                    final_mkv_filepath = os.path.join(path, base_file_name + new_extension)
                    os.rename(temp_mkv_filepath, final_mkv_filepath)
                    print(f"Renamed {temp_mkv_filepath} to {final_mkv_filepath}", flush=True)
                else:
                    error_msg = process.stderr.read()
                    print(f"Error remuxing {file_path}. Error message: {error_msg}", flush=True)

            movie_count += 1
            if movie_count >= total_movies:
                print("All movies processed!", flush=True)
                break
