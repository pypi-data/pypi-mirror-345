import shutil
import sys
import platform

# Check the operating system
is_windows = platform.system() == 'Windows'

if is_windows:
    try:
        import win32com.client
    except ImportError:
        win32com = None
        print("win32com not found. Some features may be unavailable.")


import os
import re
from sentence_transformers import CrossEncoder
import urllib.parse

from forcolate.common import copy_files_in_directory



def search_outlook_emails(query, in_directory="", save_directory="",  threshold=0.0, limit=-1):
    """
    Process Outlook emails to find relevant documents based on a query.

    Parameters:
    - query (str): The search query to match against email content.
    - in_directory (str): Directory used as input for the searc (not used in this function).
    - save_directory (str): Directory to save the processed email files.
    - threshold (float): Minimum score threshold for saving a document.
    - limit (int): Maximum number of emails to assess.

    Returns:
    - str : List of file paths where the processed emails are saved.
    """
    if not is_windows:
        return "This function is only available on Windows."
    
    # Initialize Outlook application
    outlook = win32com.client.Dispatch('Outlook.Application').GetNamespace('MAPI')

    os.makedirs(save_directory, exist_ok=True)

    # Load a pre-trained CrossEncoder model from a local directory
    model_path = os.path.join(os.path.dirname(__file__), 'vendors', 'ms-marco-MiniLM-L6-v2')
    model = CrossEncoder(model_path)

    # List to store file paths
    file_paths = []

    # Iterate through accounts and folders
    messageNames = []
    pairs = []

    assess_limit = 0
    for account in outlook.Folders:
        for folder in account.Folders:
            for message in folder.Items:
                if limit > 0 and assess_limit > limit:
                    break
                assess_limit += 1

                messageNames.append(message.Subject)
                pairs.append((query, message.Body))

    scores = model.predict(pairs)
    ranked_documents = sorted(zip(scores, messageNames, pairs), reverse=True)

    filtered = [doc for doc in ranked_documents if doc[0] >= threshold]
    for index, message_triple in enumerate(filtered):
        score, name, message = message_triple
        # Generate a unique filename using a hash of the email body
        file_name = f"{index}_{name}_{score}.txt"
        file_name = re.sub(r'[^\w_.)( -]', '', file_name)

        file_path = os.path.join(save_directory, file_name)
        absolute_path = os.path.abspath(file_path)
        with open(absolute_path, 'w', encoding='utf-8') as file:
            file.write(message[1])
            file_url = urllib.parse.urljoin('file:', urllib.request.pathname2url(absolute_path))
            file_paths.append(file_url)

    # Return the list of file paths as a string
    user_message = '\n'.join(file_paths)

    print(f"Found {len(file_paths)} emails matching the query.")
  
    # Copy in folder to out folder
    in_directory = os.path.abspath(in_directory)
    save_directory = os.path.abspath(save_directory)

    if os.path.isdir(in_directory) and not save_directory.startswith(in_directory):
        copy_files_in_directory(in_directory, save_directory)
        #shutil.copy(in_directory, save_directory)

    

    return user_message
