###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

"""
This script creates a subset of images from a larger dataset directory.
The script randomly selects a subset of images and copies them to a new directory while preserving the original directory structure.
The new subset can be used when creating an ImageFolder where the larger dataset is too unwieldy.
"""

import os
import shutil
import numpy as np

# Define the data paths
DATAPATH = "../../test_data/resnet_infer"
NEW_DATAPATH = "../../test_data/resnet_infer_416"
SUBSET_SIZE = 416  # Make this divisible by BATCH_SIZE (e.g. 32)

# Ensure the new data directory exists
if not os.path.exists(NEW_DATAPATH):
    os.makedirs(NEW_DATAPATH)

# Print the absolute path to verify it's correct
print(f"Absolute DATAPATH: {os.path.abspath(DATAPATH)}")

# List all image files in the dataset directory, keeping category subdirectories
all_files = []
for root, dirs, files in os.walk(DATAPATH):
    abs_root = os.path.abspath(root)
    print(f"Walking through: {abs_root}")
    print(f"Directories: {dirs}")
    print(f"Files: {files}")
    for file in files:
        if file.endswith(('jpg', 'jpeg', 'png', 'JPEG', 'JPG', 'PNG')):  # Add other image extensions if necessary
            file_path = os.path.join(root, file)
            print(f"Found file: {file_path}")  # Debug print to show the file path
            all_files.append(file_path)

print(f"Total files found: {len(all_files)}")  # Debug print

# Check if all_files is empty
if not all_files:
    raise ValueError("No image files found in the specified DATAPATH.")

# Select a random subset of the files
subset_files = np.random.choice(all_files, size=SUBSET_SIZE, replace=False)

# Copy the selected files to the new directory, preserving subdirectory structure
for file_path in subset_files:
    # Determine the relative path to preserve the directory structure
    relative_path = os.path.relpath(file_path, DATAPATH)
    new_file_path = os.path.join(NEW_DATAPATH, relative_path)

    # Ensure the target directory exists
    new_file_dir = os.path.dirname(new_file_path)
    if not os.path.exists(new_file_dir):
        os.makedirs(new_file_dir)

    # Copy the file
    shutil.copy(file_path, new_file_path)

print(f"Copied {SUBSET_SIZE} files to {NEW_DATAPATH}")
