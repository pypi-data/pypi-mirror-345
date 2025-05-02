import os
import re

import urllib

from forcolate import select_tool

def handle(message, folder_in, folder_out):
    name,_,tool = select_tool(message)
    print(f"Using tool: {name}")

    return tool(message, folder_in, folder_out)


def run_bullet_point_workflow(text_message, memory_folder):
    # Define a regular expression pattern to match various bullet point characters
    bullet_pattern = r'[•\-*\u2022]\s+'  # Matches •, -, *, and • (Unicode bullet) with at least one space after

    # Split the text message into bullet points using the regular expression
    bullet_points = re.split(bullet_pattern, text_message)

    # Remove any leading/trailing whitespace from each bullet point
    bullet_points = [point.strip() for point in bullet_points if point.strip()]

    # Create the memory_folder if it doesn't exist
    if not os.path.exists(memory_folder):
        os.makedirs(memory_folder)

    folder_in= os.path.join(memory_folder, f"step_0")
    if not os.path.exists(folder_in):
        os.makedirs(folder_in)

    user_message = ""
    for index, message in enumerate(bullet_points, start=1):
        # Define the output folder name based on the iteration number
        folder_out= os.path.join(memory_folder, f"step_{index}")

        # Create the output folder if it doesn't exist
        if not os.path.exists(folder_out):
            os.makedirs(folder_out)

        # Call the handle function with the message and folders
        user_message = handle(message, folder_in, folder_out)

        # save user_message to the output folder
        output_file = os.path.join(folder_out, f"output_{index}.txt")
        with open(output_file, 'w') as f:
            f.write("\n".join(user_message))   

        folder_in = folder_out  # Update the input folder for the next iteration


    absolute_path = os.path.abspath(folder_out)
    file_url = urllib.parse.urljoin('file:', urllib.request.pathname2url(absolute_path))
    
    # Return the final output folder name
    return user_message, file_url
