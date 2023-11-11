import os
import subprocess
import re

# Set the base directory to the movies folder
base_dir = '/movies'

movie_count = 0  # Initialize movie counter

# Supported video formats for conversion
supported_formats = ['.m2ts', '.mp4']  # Add or remove formats as needed

def count_movies_to_process():
    count = 0
    for subdir, dirs, files in os.walk(base_dir):
        for file in files:
            if any(file.endswith(extension) for extension in supported_formats):
                count += 1
    return count

def print_processing_message(filepath, movie_count, total_movies):
    print(f"Processing movie {movie_count + 1} out of {total_movies}: {filepath}", flush=True)

total_movies = count_movies_to_process()

for subdir, dirs, files in os.walk(base_dir):
    for file in files:
        if any(file.endswith(extension) for extension in supported_formats):
            filepath = os.path.join(subdir, file)
            new_extension = '.mkv'
            base_file_name = os.path.splitext(file)[0]
            temp_mkv_filepath = os.path.join(subdir, "temp_" + base_file_name + new_extension)

            mkvmerge_command = ['mkvmerge', '-o', temp_mkv_filepath, filepath]

            print_processing_message(filepath, movie_count, total_movies)

            process = subprocess.Popen(mkvmerge_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            while True:
                line = process.stderr.readline()
                if not line:
                    break
            process.wait()

            if process.returncode == 0:
                print(f"Successfully remuxed to: {temp_mkv_filepath}", flush=True)
                os.remove(filepath)
                final_mkv_filepath = os.path.join(subdir, base_file_name + new_extension)
                os.rename(temp_mkv_filepath, final_mkv_filepath)
                print(f"Renamed {temp_mkv_filepath} to {final_mkv_filepath}", flush=True)
            else:
                print(f"Error remuxing {filepath}. Error message: {process.stderr.read()}", flush=True)

            movie_count += 1
            if movie_count >= total_movies:
                print("All movies processed!", flush=True)
                break
