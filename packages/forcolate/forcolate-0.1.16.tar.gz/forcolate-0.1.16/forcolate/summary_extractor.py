import os
from transformers import pipeline

from forcolate.query_url_extractor import extract_query_and_folder

# Global variable to store the summarizer instance
summarizer = None

def get_summarizer():
    """
    Lazy initialization of the summarizer model.

    Returns:
    - The initialized summarizer model.
    """
    global summarizer
    if summarizer is None:
        summarizer = pipeline("summarization", model="pszemraj/led-large-book-summary")
    return summarizer

def summarize_long_document(text, max_chunk_size=2000):
    """
    Summarize a long document by splitting it into chunks and summarizing each chunk.

    Args:
    - text (str): The text to summarize.
    - max_chunk_size (int): The maximum size of each chunk.

    Returns:
    - str: The combined summary of the text.
    """
    # Split the text into words
    words = text.split()

    # Create chunks of max_chunk_size words each
    chunks = [' '.join(words[i:i + max_chunk_size]) for i in range(0, len(words), max_chunk_size)]
    print(f"Number of chunks: {len(chunks)}, Total words: {len(words)}")

    summaries = []
    summarizer = get_summarizer()
    for num, chunk in enumerate(chunks):
        summary = summarizer(chunk, max_length=200, min_length=30, do_sample=False)
        print(num, summary)
        summaries.append(summary[0]['summary_text'])

    # Combine the summaries into a single summary
    combined_summary = " ".join(summaries)
    return combined_summary

def summarize_documents(query="", folder_in="", folder_out=""):
    """
    Summarize documents in the specified source directory and save the summaries.

    Args:
    - query (str): Query containing some folder paths (optional)
    - folder_in (str): The local path to the directory containing the documents.
    - folder_out (str): The local path to the directory where the summaries will be saved.

    Returns:
    - str: The file paths of the summarized documents.
    """
    os.makedirs(folder_out, exist_ok=True)

    summarized_files_names = []

    for path, _, filenames in os.walk(folder_in):
        for filename in filenames:
            file_path = os.path.join(path, filename)

            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    result = file.read()
                    summary = summarize_long_document(result)

                    # Save the summary to the output folder
                    summary_filename = f"{os.path.splitext(filename)[0]}_summary.txt"
                    summary_file_path = os.path.join(folder_out, summary_filename)
                    with open(summary_file_path, 'w', encoding='utf-8') as summary_file:
                        summary_file.write(summary)

                    summarized_files_names.append(summary_file_path)

            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    # Return the list of summarized files names as string
    user_message = '\n '.join(summarized_files_names)
    return user_message

def summarize_folder(query="", folder_in="", folder_out=""):
    """
    Summarize all documents in the specified folder into a single summary.

    Args:
    - query (str): Query containing some folder paths to add to the summary (optional)
    - folder_in (str): The local path to the directory containing the documents.
    - folder_out (str): The local path to the directory where the summary will be saved.

    Returns:
    - str: A single summary generated from all documents in the folder.
    """
    
    query, folder_list = extract_query_and_folder(query)

    folder_list.append(folder_in)
    all_texts = []
    for directory in folder_list:
        if not os.path.exists(directory):
            print(f"Folder {directory} does not exist.")
            continue
        else:
            print(f"Processing folder {directory}")
        for path, _, filenames in os.walk(directory):
            for filename in filenames:
                # check if the file is a text or markdown file
                if not filename.endswith('.txt') and not filename.endswith('.md'):
                    continue
                file_path = os.path.join(path, filename)

                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        result = file.read()
                        all_texts.append(result)

                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    # Combine all texts into one large text
    combined_text = " ".join(all_texts)

    # Summarize the combined text
    final_summary = summarize_long_document(combined_text)

    # Save the final summary to the output folder
    os.makedirs(folder_out, exist_ok=True)  
    
    # Save the summary to the output folder
    summary_filename = f"summary.md"
    summary_file_path = os.path.join(folder_out, summary_filename)
    with open(summary_file_path, 'w', encoding='utf-8') as summary_file:
        summary_file.write(final_summary)

    return final_summary
