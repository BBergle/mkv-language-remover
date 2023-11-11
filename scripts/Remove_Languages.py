"""
This script removes specified language tracks from MKV files based on the given
environment variables. It uses mkvmerge from the MKVToolNix suite to
analyze and modify MKV containers.
"""

import os
import subprocess
import time

try:
    import orjson
except ImportError:
    print("The required module 'orjson' is not installed.")
    exit(1)

# Constants
BASE_DIR = "/movies"
EXCLUDED_LANGUAGES = [
    lang.strip().lower() for lang in os.getenv("LANGUAGES", "").split(",") if lang.strip()
]
REMOVE_COMMENTARY = os.getenv("REMOVE_COMMENTARY", "False").lower() == "true"

def print_settings():
    """Prints the exclusion settings for the script."""
    print(f"Excluded languages: {', '.join(EXCLUDED_LANGUAGES)}")
    print(f"Remove commentary tracks: {REMOVE_COMMENTARY}\n", flush=True)

def get_exclusion_track_ids(data, excluded_langs, commentary_flag):
    """
    Identifies track IDs to exclude based on language and commentary preferences.

    Args:
        data (dict): The data parsed from mkvmerge.
        excluded_langs (list): Languages to exclude.
        commentary_flag (bool): Flag to remove commentary tracks.

    Returns:
        dict: A dictionary with audio and subtitle track IDs to exclude.
    """
    exclusion_ids = {"audio": [], "subtitles": []}
    audio_track_languages = {}
    subtitle_track_languages = {}

    # Collect all audio and subtitle track languages
    for track in data.get("tracks", []):
        track_type = track["type"]
        track_id = str(track["id"])
        track_language = track["properties"].get("language", "").lower()
        track_name = track["properties"].get("track_name", "").lower()

        if track_type == "audio":
            audio_track_languages[track_id] = track_language
            if commentary_flag and "commentary" in track_name:
                exclusion_ids[track_type].append(track_id)
            elif track_language in excluded_langs:
                exclusion_ids[track_type].append(track_id)

        elif track_type == "subtitles":
            subtitle_track_languages[track_id] = track_language
            if track_language in excluded_langs:
                exclusion_ids[track_type].append(track_id)

    # Do not exclude subtitles if their corresponding audio track doesn't exist
    for sub_id, sub_lang in subtitle_track_languages.items():
        if sub_lang in excluded_langs:
            if sub_lang not in audio_track_languages.values():
                exclusion_ids["subtitles"].remove(sub_id)

    # Check if the only audio language is in the exclusion list
    if len(set(audio_track_languages.values())) == 1:
        only_language = next(iter(audio_track_languages.values()))
        if only_language in excluded_langs:
            for track_id, language in audio_track_languages.items():
                if language == only_language:
                    exclusion_ids["audio"].remove(track_id)

    return exclusion_ids

def process_movie(filepath, excluded_langs, commentary_flag):
    """
    Processes a single movie file to remove specified language tracks.

    Args:
        filepath (str): The path to the movie file.
        excluded_langs (list): Languages to exclude.
        commentary_flag (bool): Flag to remove commentary tracks.
    """
    temp_filepath = os.path.join(os.path.dirname(filepath), "temp_" + os.path.basename(filepath))
    print(f"\033[0;32mChecking\033[0m: {filepath}", flush=True)

    try:
        result = subprocess.run(
            ["mkvmerge", "-J", filepath], capture_output=True, text=True, check=True
        )
        data = orjson.loads(result.stdout)

        if "tracks" not in data:
            print(f"No track information found in {filepath}.", flush=True)
            return

        exclusion_ids = get_exclusion_track_ids(data, excluded_langs, commentary_flag)

        if exclusion_ids["audio"] or exclusion_ids["subtitles"]:
            print(f"Processing file: {filepath}", flush=True)

            mkvmerge_command = ["mkvmerge", "-o", temp_filepath]
            if exclusion_ids["audio"]:
                excluded_audio = ",".join(exclusion_ids["audio"])
                mkvmerge_command.extend(["-a", f"!{excluded_audio}"])
            if exclusion_ids["subtitles"]:
                excluded_subtitles = ",".join(exclusion_ids["subtitles"])
                mkvmerge_command.extend(["-s", f"!{excluded_subtitles}"])

            mkvmerge_command.append(filepath)
            subprocess.run(mkvmerge_command, check=True)

            os.remove(filepath)
            os.rename(temp_filepath, filepath)
            print(f"Processing of {filepath} completed successfully.", flush=True)

    except orjson.JSONDecodeError as json_error:
        print(f"JSON decode error for {filepath}: {json_error}", flush=True)
    except subprocess.CalledProcessError as cp_error:
        print(f"mkvmerge command failed for {filepath}: {cp_error}", flush=True)
    except Exception as ex:
        print(f"An unexpected error occurred for {filepath}: {ex}", flush=True)

def main():
    """Main function to execute the script logic."""
    print_settings()
    start_time = time.time()  # Start the timer
    print("Script started, looking for MKV files...", flush=True)

    for subdir, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith(".mkv"):
                filepath = os.path.join(subdir, file)
                process_movie(filepath, EXCLUDED_LANGUAGES, REMOVE_COMMENTARY)

    end_time = time.time()  # End the timer
    elapsed_time = end_time - start_time  # Calculate the elapsed time
    elapsed_minutes = int(elapsed_time // 60)
    elapsed_seconds = int(elapsed_time % 60)
    print(f"Finished processing. Time taken: {elapsed_minutes} min and {elapsed_seconds} sec.", flush=True)

if __name__ == "__main__":
    main()
