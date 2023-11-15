# Renames all file with the specified extension recursively, using numbers.
# Examples:
#   $ rename_by_number path/to/video avi mp4
#   $ rename_by_number folder/with/images png jpg
rename_by_numbers() {
    if [ "$#" -ge 2 ]; then
        local target_directory="$1"
        shift 1
        local file_extensions=("$@")

        if [ ! -d "$target_directory" ]; then
            echo "Error: The given path is not a directory."
            return 1
        fi

        for extension in "${file_extensions[@]}"; do
            count=1
            while IFS= read -r -d $'\0' file; do
                containing_directory=$(dirname "$file")
                mv -- "$file" "$containing_directory/$(printf "%03d" $count).$extension"
            done < <(find "$target_directory" -type f -name "*.$extension" -print0)
        done
    else
        echo "Usage: rename_by_numbers <folder> <extenstio1> [<extension2>]"
    fi
}


# Extract frames from the specidied video file at the given fps and in the given
# image format (png or jpg)
# Examples:
#   $ extract_frames video.avi 5 png
#   $ extract_fraems another_video.mp4 .2 jpg
extract_frames() {
    if [ "$#" -ge 3 ]; then
        local path=$(readlink -f "$1")
        local fps="$2"
        local image_format="$3"

        # Input validation
        if [ ! -f "$path" ]; then
            echo "Error: Video file does not exist."
            return 1
        fi

        local directory=$(dirname "$path")
        local video_name=$(basename "$path")
        local video_stem="${video_name%.*}"

        local frames_directory="$directory/$video_stem"
        if [ -e "$frames_directory" ]; then
            echo "Error: $frames_directory already exists."
            return 2
        fi
        
        # Use 'mkdir -p' to create the directory if it doesn't exist
        mkdir "$frames_directory"

        # Use '&&' for command sequencing
        ffmpeg -i "$path" -vf "fps=$fps" "$frames_directory/%06d.$image_format" && \
        echo "Frames extracted to: $frames_directory"
    else
        echo "Usage: extract_frames <video_file> <frame_rate> <image_format>"
    fi
}


# Encode separate images into a video using libx264
# Examples:
#   Encoding 1.jpg, 2.jpg, ... into exp.mp4 at fps=5
#   $ encode_frames experiment/%d.jpg 5 exp.mp4
#   Encoding 001.png, 002.png, ... into video.mp4 at fps=.5
#   $ encode_frames frames/%03d.png .5 video.mp4
encode_frames() {
    ffmpeg -y -framerate "$2" -i "$1" -c:v libx264 -crf 24 "$3"
}


# Extract frames for each video file in the specified directory recursively.
# Frames are being put next to the video in a folder named ater the video's
# stem.
extract_frames_recursively() {
    if [ "$#" -ge 4 ]; then
        local path=$(readlink -f "$1")
        local fps="$2"
        local image_format="$3"
        shift 3
        local extensions=("$@")

        local directory=$(dirname "$path")
        rm tmp.sh  # a stupid workaround to deal with ffmpeg misunderstanding
        touch tmp.sh
        for extension in "${extensions[@]}"; do
            echo "Processing *.$extension ..."
            find "$directory" -type f -name "*.$extension" | while read -r file; do
                echo extract_frames "$file" "$fps" "$image_format" >> tmp.sh
            done
        done
        source tmp.sh
        rm tmp.sh
    else
        echo "Not enough arguments."
    fi
}

# Extract frames from the specidied video file from the n-th to the k-th frame
# at the specified fps.
# Examples:
#   $ extract_frames_from_interval video.mp4 200 600
#   $ extract_frames_from_interval video.mp4 600 1600 png
extract_frames_from_interval() {
    if [ "$#" -eq 3 ] || [ "$#" -eq 4 ]; then
        local path=$(readlink -f "$1")
        local first_frame="$2"
        local last_frame="$3"
        local frame_extension="${4:-jpg}"  # jpg by default
        
        local directory=$(dirname "$path")
        local video_name=$(basename "$path")
        local video_stem="${video_name%.*}"
        local frames_directory="${directory}/${video_stem}"

        if [ -e "$frames_directory" ]; then
            echo "Error: $frames_directory already exists."
            return 1
        fi

        mkdir "$frames_directory"

        ffmpeg \
            -i "$path" \
            -vf "select=between(n\,${first_frame}\,${last_frame})" \
            "${frames_directory}/%06d.${frame_extension}"
    else
        echo "Usage: extract_frames_from_interval video.mp4 100 400"
    fi
}

# ffmpeg -i input.mp4 -c copy -map 0 -segment_time 00:20:00 -f segment -reset_timestamps 1 output%03d.mp4
