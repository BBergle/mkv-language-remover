import os
import subprocess
import time
import orjson

# Constants
BASE_DIR = "/movies"
EXCLUDED_LANGUAGES_ENV = os.getenv("LANGUAGES", "")
REMOVE_COMMENTARY_ENV = os.getenv("REMOVE_COMMENTARY", "False")
TEST_ENV = os.getenv("TEST") == "True"

# Process environment variables
excluded_languages = [lang.strip() for lang in EXCLUDED_LANGUAGES_ENV.split(",") if lang.strip()]
remove_commentary = REMOVE_COMMENTARY_ENV.lower() == "true"

# Output settings
print(f"Excluded languages: {', '.join(excluded_languages)}\n", flush=True)
print(f"Remove commentary tracks: {remove_commentary}\n", flush=True)

def get_exclusion_track_ids(data, languages, commentary):
    """
    Identify track IDs for exclusion based on language and commentary settings.

    :param data: MKV file metadata.
    :param languages: List of languages to exclude.
    :param commentary: Boolean indicating whether to remove commentary tracks.
    :return: Dict with audio and subtitle track IDs to exclude.
    """
    exclusion_ids = {"audio": [], "subtitles": []}
    for track in data.get("tracks", []):
        track_id, track_type = str(track["id"]), track["type"]
        track_language = track["properties"].get("language", "").lower()
        track_name = track["properties"].get("track_name", "").lower()

        if track_type == "audio" and (track_language in languages or (commentary and "commentary" in track_name)):
            exclusion_ids[track_type].append(track_id)
        elif track_type == "subtitles" and track_language in languages:
            exclusion_ids[track_type].append(track_id)

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
total_movies = count_movies(BASE_DIR)

# New structure to hold movie file paths for processing
movies_to_process = []

# First Pass: Scan and Collect Movies
print("\033[94mFirst pass:\033[0m Scanning for movies to process...\n", flush=True)
CURRENT_MOVIE = 0
for subdir, dirs, files in os.walk(BASE_DIR):
    for file in files:
        if file.endswith(".mkv"):
            CURRENT_MOVIE += 1
            filepath = os.path.join(subdir, file)
            print(
                f"\033[0;32mChecking:\033[0m ({CURRENT_MOVIE} of {total_movies}): {filepath}",
                flush=True,
            )

            try:
                result = subprocess.run(
                    ["mkvmerge", "-J", filepath], capture_output=True, text=True, check=True
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
                    movies_to_process.append(filepath)

            except Exception as e:
                print(f"Error occurred for {filepath}: {e}", flush=True)

print(f"Total movies scanned: {CURRENT_MOVIE}", flush=True)
print(f"Found {len(movies_to_process)} movies to process.", flush=True)

# Skip the second pass if TEST_ENV is True
if TEST_ENV:
    print("\033[93mSkipping the second pass due to the test vairable being true.\033[0m", flush=True)
else:
    # Second Pass: Process the Collected Movies
    print("Second pass:\033[94m Processing movies...\033[0m", flush=True)
    CURRENT_MOVIE = 0

    start_time = time.time()  # Start the timer

    for filepath in movies_to_process:
        CURRENT_MOVIE += 1
        temp_filepath = os.path.join(os.path.dirname(filepath), "temp_" + os.path.basename(filepath))

        print(
            f"\033[0;32mProcessing:\033[0m ({CURRENT_MOVIE} of {len(movies_to_process)}): {filepath}",
            flush=True,
        )

        try:
            result = subprocess.run(
                ["mkvmerge", "-J", filepath], capture_output=True, text=True, check=True
            )

            if result.returncode != 0:
                print(
                    f"Error running mkvmerge for {filepath}: {result.stderr}",
                    flush=True,
                )
                continue

            data = orjson.loads(result.stdout)

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
                    EXCLUDED_AUDIO = "!" + ",".join(exclusion_ids["audio"])
                    mkvmerge_command.extend(["-a", EXCLUDED_AUDIO])

                if exclusion_ids["subtitles"]:
                    EXCLUDED_SUBTITLES = "!" + ",".join(exclusion_ids["subtitles"])
                    mkvmerge_command.extend(["-s", EXCLUDED_SUBTITLES])

                mkvmerge_command.append(filepath)

                with open(os.devnull, "wb") as null:
                    result = subprocess.run(
                        mkvmerge_command, stdout=null, stderr=null, check=True
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
                f"KeyError {e} when processing {filepath}, "
                f"this file may have an unexpected structure.",
                flush=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Subprocess execution failed for {filepath}: {e}", flush=True)
        except OSError as e:
            print(f"OS error occurred for {filepath}: {e}", flush=True)
        except ValueError as e:
            print(f"Value error: {e}", flush=True)

    end_time = time.time()  # End the timer
    elapsed_time = end_time - start_time  # Calculate the elapsed time

    elapsed_minutes = int(elapsed_time // 60)
    elapsed_seconds = int(elapsed_time % 60)

    print(
        f"\\033[92mFinished processing all movies.\\033[0m Time taken: {elapsed_minutes} min and {elapsed_seconds} sec.",
        flush=True,
)