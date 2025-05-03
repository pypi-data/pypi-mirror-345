"""
Bullet Point Workflow Module

This module provides functionality to process a text message containing bullet points.
Each bullet point is processed sequentially using a selected tool, and the results are saved in a structured folder hierarchy.
"""

import os
import re
import urllib
from forcolate import select_tool

def run_bullet_point_workflow(text_message: str, memory_folder: str, additional_tools: list = None):
    """
    Process a text message containing bullet points using a workflow.

    Args:
        text_message (str): The input text message containing bullet points.
        memory_folder (str): The base folder to store intermediate and final results.
        additional_tools (list, optional): A list of additional tools to include in the tool selection process.

    Yields:
        dict: A dictionary containing the current step, total steps, and the message processed at each step.

    Returns:
        tuple: The final user message and the URL of the output folder.
    """
    # Define a regular expression pattern to match various bullet point characters
    bullet_pattern = r'[•\-*\u2022]\s+'  # Matches •, -, *, and • (Unicode bullet) with at least one space after

    # Split the text message into bullet points using the regular expression
    bullet_points = re.split(bullet_pattern, text_message)

    # Remove any leading/trailing whitespace from each bullet point
    bullet_points = [point.strip() for point in bullet_points if point.strip()]

    # Create the memory_folder if it doesn't exist
    if not os.path.exists(memory_folder):
        os.makedirs(memory_folder)

    folder_in = os.path.join(memory_folder, f"step_0")
    if not os.path.exists(folder_in):
        os.makedirs(folder_in)

    user_message = ""
    total_steps = len(bullet_points)  # Calculate total steps
    for index, message in enumerate(bullet_points, start=1):
        # Define the output folder name based on the iteration number
        folder_out = os.path.join(memory_folder, f"step_{index}")

        # Create the output folder if it doesn't exist
        if not os.path.exists(folder_out):
            os.makedirs(folder_out)

        # Call the handle function with the message and folders
        name, _, tool = select_tool(message, additional_tools=additional_tools)
        print(f"Using tool: {name}")
        user_message = tool(message, folder_in, folder_out)

        # Send back advancement at each step
        yield {"step": index, "total_steps": total_steps, "message": user_message}

        # Save user_message to the output folder
        output_file = os.path.join(folder_out, f"output_{index}.txt")
        with open(output_file, 'w') as f:
            f.write(user_message)

        folder_in = folder_out  # Update the input folder for the next iteration

    absolute_path = os.path.abspath(folder_out)
    file_url = urllib.parse.urljoin('file:', urllib.request.pathname2url(absolute_path))
    
    # Return the final output folder name
    return user_message, file_url
