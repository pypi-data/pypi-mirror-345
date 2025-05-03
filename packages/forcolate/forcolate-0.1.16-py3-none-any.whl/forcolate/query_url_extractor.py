   
import re


def extract_query_and_folder(query):
    """
    Extracts the query and folder path from the input string. "
    """

    # extract any folder path from the query
    path_pattern = r'[a-zA-Z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*|(?:/[^\\/:*?"<>|\r\n]+)+'
    folder_list = re.findall(path_pattern, query)

    # replace all folder paths in the query with empty string
    query = re.sub(path_pattern, '', query)
        

    # remove any duplicates from the list
    folder_list = list(set(folder_list))
    # remove any empty strings from the list
    folder_list = [folder for folder in folder_list if folder]
    # remove any leading/trailing whitespace from each folder path
    folder_list = [folder.strip() for folder in folder_list]
    
    return query, folder_list

def extract_query_and_url(query):
    """
    Extracts the query and URL from the input string. "
    """

    # extract any URL from the query
    url_pattern = r'(https?://[^\s]+)'
    url_list = re.findall(url_pattern, query)

    # replace all URLs in the query with empty string
    query = re.sub(url_pattern, '', query)
        

    # remove any duplicates from the list
    url_list = list(set(url_list))
    # remove any empty strings from the list
    url_list = [url for url in url_list if url]
    # remove any leading/trailing whitespace from each folder path
    url_list = [url.strip() for url in url_list]
    
    return query, url_list
