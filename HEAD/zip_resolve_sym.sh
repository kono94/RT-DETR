#!/bin/bash

# Define input directory and output zip file
INPUT_DIR="./COMBINED_HEAD"
OUTPUT_ZIP="./COMBINED_HEAD.zip"
TEMP_DIR="/tmp/COMBINED_HEAD_resolved"

# Check if input directory exists
if [ ! -d "$INPUT_DIR" ]; then
    echo "Error: Directory $INPUT_DIR does not exist."
    exit 1
fi

# Remove any existing temporary directory
if [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
fi

# Create temporary directory
mkdir -p "$TEMP_DIR"

# Copy files to temporary directory, resolving symlinks
echo "Copying files to $TEMP_DIR, resolving symlinks..."
rsync -a --copy-links "$INPUT_DIR/" "$TEMP_DIR/"

# Check if rsync succeeded
if [ $? -ne 0 ]; then
    echo "Error: rsync failed."
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Create zip file from temporary directory
echo "Creating zip file $OUTPUT_ZIP..."
cd "$TEMP_DIR"
zip -r "$OUTPUT_ZIP" ./*
if [ $? -ne 0 ]; then
    echo "Error: zip failed."
    cd -
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Move zip file to desired location
mv "$OUTPUT_ZIP" "$(dirname "$OUTPUT_ZIP")"
cd -

# Clean up temporary directory
# rm -rf "$TEMP_DIR"

echo "Successfully created $OUTPUT_ZIP with resolved symlinks."
