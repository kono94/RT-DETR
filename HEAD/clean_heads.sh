#!/bin/bash

# Define the directory containing split files
SPLITS_DIR="./HollywoodHeads/Splits"

# Base name to remove
BASE_NAME="mov_013_113717"

# List of split files
SPLIT_FILES=("train.txt" "val.txt" "trainval.txt" "test.txt")

# Loop through each split file
for file in "${SPLIT_FILES[@]}"; do
    FILE_PATH="$SPLITS_DIR/$file"
    
    if [ -f "$FILE_PATH" ]; then
        # Check if the base name exists in the file
        if grep -Fx "$BASE_NAME" "$FILE_PATH" > /dev/null; then
            echo "Found '$BASE_NAME' in $FILE_PATH, removing it..."
            # Create a temporary file
            temp_file=$(mktemp)
            # Copy all lines except the one matching BASE_NAME
            grep -Fxv "$BASE_NAME" "$FILE_PATH" > "$temp_file"
            # Replace the original file with the updated one
            mv "$temp_file" "$FILE_PATH"
            echo "Updated $FILE_PATH"
        else
            echo "No match for '$BASE_NAME' in $FILE_PATH"
        fi
    else
        echo "File not found: $FILE_PATH"
    fi
done

echo "Cleanup complete."
