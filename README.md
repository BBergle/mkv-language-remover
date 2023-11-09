# mkv-language-remover

The purpose of this container is to go through you movies directory and convert all mp4 and m2ts file to mkv and then remove a specific language from those movies.

It will first convert all m2ts and mp4 files to mkv if convert is set to true then it will remove the langauges set in the ENV LANGUAGES vairable.

It will also remove all commentary tracks if set to true

The container can be found here: https://hub.docker.com/r/bbergle/mkv-language-remover/tags
