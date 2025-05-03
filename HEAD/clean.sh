#!/bin/bash

# Define paths
HOLLYWOOD_IMAGES_DIR="./HollywoodHeads/JPEGImages"
HOLLYWOOD_ANNOTATIONS_DIR="./HollywoodHeads/Annotations"
COMBINED_IMAGES_DIR="./COMBINED_HEAD/JPEGImages"
COMBINED_ANNOTATIONS_DIR="./COMBINED_HEAD/Annotations"
SPLITS_DIR="./COMBINED_HEAD/Splits"

# List of split files
SPLIT_FILES=("train.txt" "val.txt" "trainval.txt" "test.txt")

# Find all zero-byte .jpeg files in HollywoodHeads/JPEGImages
zero_byte_files=$(find "$HOLLYWOOD_IMAGES_DIR" -type f -name "*.jpeg" -size 0)

# Check if any zero-byte files were found
if [ -z "$zero_byte_files" ]; then
    echo "No zero-byte .jpeg files found in $HOLLYWOOD_IMAGES_DIR"
    exit 0
fi

# Process each zero-byte file
echo "Processing zero-byte .jpeg files..."
while IFS= read -r file; do
    # Extract base name (without path and extension)
    base_name=$(basename "$file" .jpeg)
    echo "Found zero-byte file: $file (base name: $base_name)"

    # Delete the .jpeg file in HollywoodHeads/JPEGImages
    if [ -f "$file" ]; then
        rm "$file"
        echo "Removed: $file"
    else
        echo "File already removed: $file"
    fi

    # Delete the corresponding .xml file in HollywoodHeads/Annotations
    hollywood_anno_file="$HOLLYWOOD_ANNOTATIONS_DIR/$base_name.xml"
    if [ -f "$hollywood_anno_file" ]; then
        rm "$hollywood_anno_file"
        echo "Removed: $hollywood_anno_file"
    else
        echo "File not found: $hollywood_anno_file"
    fi

    # Delete the corresponding .jpg file in COMBINED_HEAD/JPEGImages
    combined_img_file="$COMBINED_IMAGES_DIR/$base_name.jpg"
    if [ -f "$combined_img_file" ]; then
        rm "$combined_img_file"
        echo "Removed: $combined_img_file"
    else
        echo "File not found: $combined_img_file"
    fi

    # Delete the corresponding .xml file in COMBINED_HEAD/Annotations
    combined_anno_file="$COMBINED_ANNOTATIONS_DIR/$base_name.xml"
    if [ -f "$combined_anno_file" ]; then
        rm "$combined_anno_file"
        echo "Removed: $combined_anno_file"
    else
        echo "File not found: $combined_anno_file"
    fi

    # Remove the base name from split files
    for split_file in "${SPLIT_FILES[@]}"; do
        FILE_PATH="$SPLITS_DIR/$split_file"
        if [ -f "$FILE_PATH" ]; then
            # Check if the base name exists in the file
            if grep -Fx "$base_name" "$FILE_PATH" > /dev/null; then
                echo "Found '$base_name' in $FILE_PATH, removing it..."
                # Create a temporary file
                temp_file=$(mktemp)
                # Copy all lines except the one matching base_name
                grep -Fxv "$base_name" "$FILE_PATH" > "$temp_file"
                # Replace the original file with the updated one
                mv "$temp_file" "$FILE_PATH"
                echo "Updated: $FILE_PATH"
            else
                echo "No match for '$base_name' in $FILE_PATH"
            fi
        else
            echo "Split file not found: $FILE_PATH"
        fi
    done

done <<< "$zero_byte_files"

echo "Cleanup complete."
