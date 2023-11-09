import os
import subprocess
import orjson
import time

# Set the base directory to the movies folder
base_dir = "/movies"

# Fetch the excluded languages from the environment variable
excluded_languages_env = os.getenv("LANGUAGES", "")
# Split the string by commas and remove any surrounding whitespace
excluded_languages = [
    lang.strip() for lang in excluded_languages_env.split(",") if lang.strip()
]

# Fetch the remove commentary tracks option from the environment variable
remove_commentary_env = os.getenv("REMOVE_COMMENTARY", "False")
# Convert the string to a Python boolean
remove_commentary = remove_commentary_env.lower() == "true"

# Print out the settings
print(f"Excluded languages: {', '.join(excluded_languages)}\n", flush=True)
print(f"Remove commentary tracks: {remove_commentary}\n", flush=True)


def get_exclusion_track_ids(data, excluded_languages, remove_commentary):
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
            if remove_commentary and "commentary" in track_name:
                exclusion_ids[track_type].append(track_id)
            elif track_language in excluded_languages:
                exclusion_ids[track_type].append(track_id)

        elif track_type == "subtitles":
            subtitle_track_languages[track_id] = track_language
            if track_language in excluded_languages:
                exclusion_ids[track_type].append(track_id)

    # Do not exclude subtitles if their corresponding audio track doesn't exist
    for sub_id, sub_lang in subtitle_track_languages.items():
        if sub_lang in excluded_languages:
            # If there is no audio track in the same language, remove from exclusion list
            if sub_lang not in audio_track_languages.values():
                exclusion_ids["subtitles"].remove(sub_id)

    # Check if the only audio language is in the exclusion list
    unique_audio_languages = set(audio_track_languages.values())
    if len(unique_audio_languages) == 1:
        # Get the only language
        only_language = next(iter(unique_audio_languages))
        if only_language in excluded_languages:
            # If the only audio language is in the exclusion list, do not exclude it
            for track_id, language in audio_track_languages.items():
                if language == only_language:
                    exclusion_ids["audio"].remove(track_id)

    return exclusion_ids


def count_movies(directory, extension=".mkv"):
    """Count the number of movies with a particular extension in a directory."""
    return sum(
        1
        for subdir, dirs, files in os.walk(directory)
        for file in files
        if file.endswith(extension)
    )


# Count the total number of movies
total_movies = count_movies(base_dir)
current_movie = 0

start_time = time.time()  # Start the timer

print("Script started, looking for MKV files...", flush=True)

for subdir, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith(".mkv"):
            current_movie += 1
            filepath = os.path.join(subdir, file)
            temp_filepath = os.path.join(subdir, "temp_" + file)

            print(
                f"\033[0;32mChecking\033[0m ({current_movie} of {total_movies}): {filepath}",
                flush=True,
            )

            try:
                result = subprocess.run(
                    ["mkvmerge", "-J", filepath], capture_output=True, text=True
                )

                if result.returncode != 0:
                    print(
                        f"Error running mkvmerge for {filepath}: {result.stderr}",
                        flush=True,
                    )
                    continue

                data = orjson.loads(result.stdout)

                if "tracks" not in data:
                    print(f"No track information found in {filepath}.", flush=True)
                    continue

                exclusion_ids = get_exclusion_track_ids(
                    data, excluded_languages, remove_commentary
                )

                if exclusion_ids["audio"] or exclusion_ids["subtitles"]:
                    print(f"Processing file: {filepath}", flush=True)

                    for track_id in exclusion_ids["audio"]:
                        print(f"Removing audio track number {track_id}...", flush=True)

                    for track_id in exclusion_ids["subtitles"]:
                        print(
                            f"Removing subtitle track number {track_id}...", flush=True
                        )

                    mkvmerge_command = ["mkvmerge", "-o", temp_filepath]
                    if exclusion_ids["audio"]:
                        excluded_audio = "!" + ",".join(exclusion_ids["audio"])
                        mkvmerge_command.extend(["-a", excluded_audio])

                    if exclusion_ids["subtitles"]:
                        excluded_subtitles = "!" + ",".join(exclusion_ids["subtitles"])
                        mkvmerge_command.extend(["-s", excluded_subtitles])

                    mkvmerge_command.append(filepath)

                    with open(os.devnull, "wb") as null:
                        result = subprocess.run(
                            mkvmerge_command, stdout=null, stderr=null
                        )

                    if result.returncode == 0:
                        os.remove(filepath)
                        os.rename(temp_filepath, filepath)
                        print(
                            f"Processing of {filepath} completed successfully.",
                            flush=True,
                        )
                    else:
                        print(
                            f"Error processing {filepath}. Keeping the original file.",
                            flush=True,
                        )

            except orjson.JSONDecodeError as e:
                print(f"Failed to decode JSON output for {filepath}: {e}", flush=True)
            except KeyError as e:
                print(
                    f"KeyError {e} when processing {filepath}, this file may have an unexpected structure.",
                    flush=True,
                )
            except Exception as e:
                print(f"An unexpected error occurred for {filepath}: {e}", flush=True)

end_time = time.time()  # End the timer
elapsed_time = end_time - start_time  # Calculate the elapsed time

elapsed_minutes = int(elapsed_time // 60)
elapsed_seconds = int(elapsed_time % 60)

print(
    f"Finished checking all movies. Time taken: {elapsed_minutes} min and {elapsed_seconds} sec.",
    flush=True,
)
