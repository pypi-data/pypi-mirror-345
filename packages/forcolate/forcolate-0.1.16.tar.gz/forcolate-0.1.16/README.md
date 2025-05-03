# Forcolate Library


[![Build status](https://github.com/FOR-sight-ai/FORcolate/actions/workflows/publish.yml/badge.svg?branch=main)](https://github.com/FOR-sight-ai/forcolate/actions)
[![Docs status](https://img.shields.io/readthedocs/FORcolate)](TODO)
[![Version](https://img.shields.io/pypi/v/forcolate?color=blue)](https://pypi.org/project/forcolate/)
[![Python Version](https://img.shields.io/pypi/pyversions/forcolate.svg?color=blue)](https://pypi.org/project/forcolate/)
[![Downloads](https://static.pepy.tech/badge/forcolate)](https://pepy.tech/project/forcolate)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/FOR-sight-ai/forcolate/blob/main/LICENSE)

  <!-- Link to the documentation -->
  <a href="TODO"><strong>Explore FORcolate docs »</strong></a>
  <br>

</div>

_AI search is like a box of FORcolates. You never know what you're gonna get._



Forcolate is a versatile library designed to enhance semantic search capabilities, in particular in a setting where it is deployed locally (and not in a cloud environment). It offers a suite of tools that facilitate efficient and intelligent search functionalities, making it easier to find relevant information within large datasets.

## Features

- **Bullet Point Workflow**: Process text messages containing bullet points, where each bullet point is handled using a selected tool.
- **Semantic Search for Documents**: Search for files and documents within local directories using advanced semantic search algorithms.
- **Semantic Search for Outlook Emails**: Perform semantic search on Microsoft Outlook emails using the Win32 API.
- **Convert Documents to Text**: Convert documents from various formats (e.g., PDF, Word) into plain text for easier processing.
- **Summarize Documents**: Generate summaries for individual documents within a specified directory.
- **Summarize Folder**: Create a single cohesive summary from the contents of all files in a folder.
- **Download URL to Text**: Fetch and convert web pages or documents from URLs into plain text.

## Installation

To install the Forcolate library, use the following command:

```bash
pip install forcolate
```

## Usage

Most of the functions are constructed around a key principle : *sequence of working folders*
Each function take as parameters a query, an input folder and an output folder. 

* For search function, the search adds new files to the output and copy all (relevant) files from the input folder
* For transformation function (such as summary), the transformation is applied on all files of the input and produce different files in the output

The query in itseld can contain rich informations such as other folders path to take as input.


### Bullet Point Workflow

The Forcolate library includes a workflow for processing text messages containing bullet points. Each bullet point is processed using a selected tool. Below is an example of how to use this workflow:

```python
from forcolate.bullet_point_workflow import run_bullet_point_workflow

text_message = """
- Search for documents in the folder
- Summarize the documents
- Convert URLs to text
"""
memory_folder = "path/to/memory/folder" # This folder will contain one folder per step

# Run the workflow
for progress in run_bullet_point_workflow(text_message, memory_folder):
    print(f"Step {progress['step']} of {progress['total_steps']}: {progress['message']}")
```

### Semantic Search for Outlook Emails

This tool performs semantic search on Outlook emails using the Win32 API. Below is an example of how to use this tool:

```python
from forcolate import search_outlook_emails

query = "Search emails for 'project updates' "
folder_in = "path/to/input/folder" # all the content will be copied in output
folder_out = "path/to/output/folder"

file_paths = search_outlook_emails(query, folder_in, folder_out)
print(file_paths)
```

### Semantic Search for Documents

This tool searches for documents in a folder (and recursively in subfolder and compressed files) using a semantic search model. Below is an example of how to use this tool:

```python
from forcolate import search_folder

query = "Search for 'financial reports' in path/to/source/directory"
folder_in = "path/to/input/folder" # this folder will also be search in
folder_out = "path/to/output/folder"

file_paths = search_folder(query, folder_in, folder_out)
print(file_paths)
```

### Convert Documents to Text

This tool converts documents from various formats into plain text. Below is an example of how to use this tool:

```python
from forcolate import convert_folders_to_markdown

query = "Convert documents in path/to/source/directory to text"
folder_in = "path/to/input/folder"
folder_out = "path/to/output/folder"

convert_folders_to_markdown(query, folder_in, folder_out)
```

### Summarize Documents

This tool summarizes the content of each individual document within a specified directory. Below is an example of how to use this tool:

```python
from forcolate import summarize_documents

query = "" # Not used at the moment
folder_in = "path/to/input/folder"
folder_out = "path/to/output/folder"

summarize_documents(query, folder_in, folder_out)
```

### Summarize Folder

This tool generates a single summary from all the information in a folder. Below is an example of how to use this tool:

```python
from forcolate import summarize_folder

query = "Summarize all files in path/to/source/directory"
folder_in = "path/to/input/folder"
folder_out = "path/to/output/folder"

summarize_folder(query, folder_in, folder_out)
```

### Download URL to Text

This tool downloads a document or web page from the internet and converts the content into plain text. Below is an example of how to use this tool:

```python
from forcolate import convert_URLS_to_markdown

query = "Download and convert https://example.com/document1 and https://example.com/document2"
folder_in = "path/to/input/folder" # This folder will be copied
folder_out = "path/to/output/folder"

convert_URLS_to_markdown(query, folder_in, folder_out)
```

## Contributing

Contributions to the Forcolate library are welcome! If you have ideas for new features, improvements, or bug fixes, please open an issue or submit a pull request.

## Acknowledgement

This project received funding from the French ”IA Cluster” program within the Artificial and Natural Intelligence Toulouse Institute (ANITI) and from the "France 2030" program within IRT Saint Exupery. The authors gratefully acknowledge the support of the FOR projects.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
