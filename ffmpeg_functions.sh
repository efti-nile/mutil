# Renames all file with the specified extension recursively, using numbers.
# Examples:
#   rename_by_number path/to/video avi mp4
#   rename_by_number folder/with/images png jpg
rename_by_numbers() {
    if [ "$#" -ge 2 ]; then
        directory="$1"
        shift 1
        extensions=("$@")  # mp4, txt, ...

        if [ ! -d "$directory" ]; then
            echo "The given path not a directory."
            return 1
        fi

        count=1
        for extension in "${extensions[@]}"; do
            extension_count=1
            find "$directory" -type f -name "*.$extension" | while read -r file; do
                containing_directory=$(dirname "$file")
                mv -- "$file" "$containing_directory/$count.$extension"
                ((count++))
                ((extension_count++))
            done
            echo "Renamed $extension_count *.$extension files"
        done
    else
        echo "Not enough arguments."
    fi
}


# Extract frames from the specidied video file at the given fps and in the given
# image format (png or jpg)
extract_frames() {
    if [ "$#" -ge 3 ]; then
        path=$(readlink -f "$1")
        fps="$2"  # the fps can be: 10, .02, 5, ...
        image_format="$3"

        directory=$(dirname "$path")
        video_name=$(basename "$path")
        video_stem="${video_name%.*}"

        frames_directory="$directory/$video_stem"
        if [ -d "$frames_directory" ]; then
            rm -rf -- "$frames_directory"
        fi
        mkdir -- "$frames_directory"

        ffmpeg -i "$path" "$frames_directory/%06d.$image_format"
    else
        echo "Not enough arguments."
    fi
}


# Extract frames for each video file in the specified directory recursively.
# Frames are being put next to the video in a folder named ater the video's
# stem.
extract_frames_recursively() {
    if [ "$#" -ge 4 ]; then
        path=$(readlink -f "$1")
        fps="$2"
        image_format="$3"  # jpg is the default
        shift 3
        extensions=("$@")

        directory=$(dirname "$path")
        if [ -f tmp.sh ]; then
            rm tmp.sh
        fi
        for extension in "${extensions[@]}"; do
            echo "Processing *.$extension ..."
            find "$directory" -type f -name "*.$extension" | while read -r file; do
                echo extract_frames "'""$file""'" "'""$fps""'" "$image_format" >> tmp.sh
            done
        done
    else
        echo "Not enough arguments."
    fi
}

# Extract frames from the specidied video file from the n-th frame to the k-th 
# frame at the specified fps.
extract_frames_from_interval() {
    if [ "$#" -e 5 ]; then
        path=$(readlink -f "$1")
        first_frame="$2"
        last_frame="$3"
        fps="$4"
        frame_extension="${5:-jpg}"
        
        directory=$(dirname "$path")
        video_name=$(basename "$path")
        video_stem="${file_name:%.*}"
        frames_directory="${directory}/${video_name}"
        mkdir "$frames_directory"
        ffmpeg \
            -i "$path" \
            -vf "select=between(n,${first_frame},${last_frame}" \
            -vf "fps=$fps" \
            "${frames_directory}/%06d.${frame_extension}"
    else
        print "Must be 5 arguments."
    fi
}

# ffmpeg -i input.mp4 -c copy -map 0 -segment_time 00:20:00 -f segment -reset_timestamps 1 output%03d.mp4
