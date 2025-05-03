import os
import re
from sentence_transformers import CrossEncoder
import urllib.parse

from forcolate.document_to_text import convert_documents_to_markdown
from forcolate.query_url_extractor import extract_query_and_folder


def search_folder(query, source_directory, save_directory, threshold=0.0, limit=-1):
    """
    Process documents in a directory to find relevant documents based on a query.

    Parameters:
    - source_directory (str): Directory containing the documents to process.
    - save_directory (str): Directory to save the processed document files.
    - query (str): The search query to match against document content.
    - threshold (float): Minimum score threshold for saving a document.
    - limit (int): Maximum number of documents to assess.

    Returns:
    - List[str]: List of file paths where the processed documents are saved.
    """
    query, folder_list = extract_query_and_folder(query)

    folder_list.append(source_directory)

    os.makedirs(save_directory, exist_ok=True)

    # Load a pre-trained CrossEncoder model from a local directory
    model_path = os.path.join(os.path.dirname(__file__), 'vendors', 'ms-marco-MiniLM-L6-v2')
    model = CrossEncoder(model_path)

    # List to store file paths
    file_paths = []

    # Convert documents to markdown and process them
    pairs = []
    document_names = []
    document_paths = []
    assess_limit = 0
    for directory in folder_list:
        if not os.path.exists(directory):
            print(f"Folder {directory} does not exist.")
            continue
        else:
            print(f"Processing folder {directory}")
        for filename, filepath,markdown_content in convert_documents_to_markdown(directory):
            if limit > 0 and assess_limit >= limit:
                break
            assess_limit += 1

            document_names.append(filename)
            document_paths.append(filepath)
            pairs.append((query, markdown_content))

            # Predict and save if the batch is large enough or limit is reached
            if len(pairs) >= 100 or (limit > 0 and assess_limit >= limit):
                scores = model.predict(pairs)
                ranked_documents = sorted(zip(scores, document_names, document_paths, pairs), reverse=True)

                filtered = [doc for doc in ranked_documents if doc[0] >= threshold]
                for index, document_triple in enumerate(filtered):
                    score, name, path, document = document_triple
                    # Generate a unique filename using a hash of the document content
                    file_name = f"{index}_{name}_{score}.md"
                    file_name = re.sub(r'[^\w_.)( -]', '', file_name)

                    file_path = os.path.join(save_directory, file_name)
                    absolute_path = os.path.abspath(file_path)
                    
                    with open(absolute_path, 'w', encoding='utf-8') as file:
                        file.write(document[1])
                        # original path for user message
                        file_url = urllib.parse.urljoin('file:', urllib.request.pathname2url(path))
                        file_paths.append(file_url)

                # Clear the lists to free up memory
                pairs.clear()
                document_names.clear()
                document_paths.clear()

        # Process any remaining documents
        if pairs:
            scores = model.predict(pairs)
            ranked_documents = sorted(zip(scores, document_names, document_paths, pairs), reverse=True)

            filtered = [doc for doc in ranked_documents if doc[0] >= threshold]
            for index, document_triple in enumerate(filtered):
                score, name, path, document = document_triple
                # Generate a unique filename using a hash of the document content
                file_name = f"{index}_{name}_{score}.md"
                file_name = re.sub(r'[^\w_.)( -]', '', file_name)

                file_path = os.path.join(save_directory, file_name)
                absolute_path = os.path.abspath(file_path)
                with open(absolute_path, 'w', encoding='utf-8') as file:
                    file.write(document[1])
                    file_url = urllib.parse.urljoin('file:', urllib.request.pathname2url(absolute_path))
                    file_paths.append(file_url)
            pairs.clear()
            document_names.clear()
            document_paths.clear()

    # Return the list of file paths
    return file_paths
