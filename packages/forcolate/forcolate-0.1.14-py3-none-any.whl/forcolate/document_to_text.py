import re
from docling.document_converter import DocumentConverter
import os

from forcolate.query_url_extractor import extract_query_and_folder

import zipfile
import tarfile
import py7zr


def convert_documents_to_markdown(source):
    """
    Convert documents in the specified source directory to markdown.

    Args:
    - source (str): The local path or URL to the directory containing the documents.

    Yields:
    - str: The markdown content of each converted document.
    """
    converter = DocumentConverter()
    text_extensions = {'.txt', '.md', '.adoc'}
    compressed_extensions = {'.zip', '.7z', '.tar', '.gz', '.bz2'}

    for path, _, filenames in os.walk(source):
        for filename in filenames:
            file_path = os.path.join(path, filename)
            file_extension = os.path.splitext(filename)[1].lower()

            try:
                if file_extension in text_extensions:
                    # Directly read the content of text files
                    with open(file_path, 'r', encoding='utf-8') as file:
                        result = file.read()
                    yield filename, file_path, result
                elif file_extension in compressed_extensions:
                    # Create a subdirectory for extracted files
                    extract_path = os.path.join(path, f"{os.path.splitext(filename)[0]}_extracted")
                    os.makedirs(extract_path, exist_ok=True)

                    # Uncompress the file
                    if file_extension == '.zip':
                        with zipfile.ZipFile(file_path, 'r') as zip_ref:
                            zip_ref.extractall(extract_path)
                    elif file_extension == '.7z':
                        with py7zr.SevenZipFile(file_path, mode='r') as sz_ref:
                            sz_ref.extractall(path=extract_path)
                    elif file_extension in {'.tar', '.gz', '.bz2'}:
                        with tarfile.open(file_path, 'r:*') as tar_ref:
                            tar_ref.extractall(extract_path)

                    continue  # Skip further processing of the compressed file itself
                else:
                    # Convert other document types
                    converted = converter.convert(file_path)
                    result = converted.document.export_to_markdown()
                    yield filename, file_path, result
            except Exception as e:
                print(f"Error processing {filename}: {e}")

def convert_folders_to_markdown(query="",folder_in="",folder_out=""):
    """
    Convert documents in the specified source directory to markdown.

    Args:
    - query (str): Query containing some folder paths (optional)
    - folder_in (str): The local path or URL to the directory containing the documents.
    - folder_out (str): The local path or URL to the directory where the converted documents will be saved.

    Returns:
    - str: The file path of the converted document.
    """
    os.makedirs(folder_out, exist_ok=True)

    query, folder_list = extract_query_and_folder(query)

    folder_list.append(folder_in)

    converted_files_names = []

    for folder in folder_list:
        if not os.path.exists(folder):
            print(f"Folder {folder} does not exist.")
            continue
        else:
            print(f"Processing folder {folder}")

        for filename, filepath, markdown_content in convert_documents_to_markdown(folder):
            # Generate a unique filename using a hash of the email body
            file_name = f"{filename}.md"
            file_name = re.sub(r'[^\w_.)( -]', '', file_name)
            converted_files_names.append(filepath)

            file_path = os.path.join(folder_out, file_name)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
                f.write("\n") 

    # return the list of converted files names as string
    user_message = '\n '.join(converted_files_names)
    
    return user_message
