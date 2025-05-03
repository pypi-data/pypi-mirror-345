import re
from docling.document_converter import DocumentConverter
import os


from forcolate.query_url_extractor import extract_query_and_url
from forcolate.common import copy_files_in_directory

def convert_url_to_markdown(source):
    """
    Convert internet URL content to markdown.

    Args:
    - source (str): The online URL to convert

    Yields:
    - str: The markdown content of URL.
    """

    converter = DocumentConverter()
    result = converter.convert(source)
    return result.document.export_to_markdown()


def convert_URLS_to_markdown(query="",folder_in="",folder_out=""):
    """
    Convert URLS in the query to markdown.

    Args:
    - query (str): Query containing some URLs
    - folder_in (str): The local path or URL to the directory containing the documents.
    - folder_out (str): The local path or URL to the directory where the converted documents will be saved.

    Returns:
    - str: The file path of the converted document.
    """
    os.makedirs(folder_out, exist_ok=True)

    query, url_list = extract_query_and_url(query)


    converted_files_names = []

    for url in url_list:

        print(f"Processing URL {url}")

        markdown_content = convert_url_to_markdown(url)
        name_from_url= url.split("/")[-1]
        # Generate a unique filename using a 
        file_name = f"{name_from_url}.md"
        file_name = re.sub(r'[^\w_.)( -]', '', file_name)
        filepath = os.path.join(folder_out, file_name)
        converted_files_names.append(filepath)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
            f.write("\n") 

    # return the list of converted files names as string
    user_message = '\n '.join(converted_files_names)
    
    # Copy in folder to out folder
    in_directory = os.path.abspath(folder_in)
    save_directory = os.path.abspath(folder_out)

    if os.path.isdir(in_directory) and not save_directory.startswith(in_directory):
        copy_files_in_directory(in_directory, save_directory)
        #shutil.copy(in_directory, save_directory)


    return user_message
