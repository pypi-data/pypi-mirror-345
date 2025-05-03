

import shutil
import os

def copy_files_in_directory(src_directory, dest_directory):
    try:
        # Ensure the destination directory exists
        os.makedirs(dest_directory, exist_ok=True)

        # Iterate over all files in the source directory
        for root, _, files in os.walk(src_directory):
            for file in files:
                src_file_path = os.path.join(root, file)
                dest_file_path = os.path.join(dest_directory, os.path.relpath(src_file_path, src_directory))

                # Ensure the destination subdirectory exists
                os.makedirs(os.path.dirname(dest_file_path), exist_ok=True)

                # Copy the file
                shutil.copy2(src_file_path, dest_file_path)
                print(f"File copied successfully from {src_file_path} to {dest_file_path}")

    except PermissionError:
        print(f"PermissionError: Check your read/write permissions for {src_directory} and {dest_directory}")
    except FileNotFoundError:
        print(f"FileNotFoundError: The directory {src_directory} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")
        
