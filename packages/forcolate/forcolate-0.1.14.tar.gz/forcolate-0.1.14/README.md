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

- **Semantic Search Utilities wrapper**: Utilize advanced semantic search algorithms to retrieve relevant information based on context and meaning, rather than simple keyword matching.
- **Outlook Email Search**: Integrate semantic search with Microsoft Outlook using the Win32 API to search through emails intelligently.


## Installation

To install the Forcolate library, use the following command:

```bash
pip install forcolate
```

## Usage

### Semantic Search for Outlook Emails

The Forcolate library includes a tool for performing semantic search on Outlook emails using the Win32 API. Below is an example of how to use this tool:

```python
from forcolate import search_outlook_emails

save_directory = "path/to/save/directory"
query = "your search query"

file_paths = search_outlook_emails(save_directory, query)
print(file_paths)

```

### Semantic Search for Documents

This tool converts documents to markdown format using the `docling` library and uses a semantic search model to identify and save relevant documents based on a query. Below is an example of how to use this tool:

```python
from forcolate import search_folder

source_directory = "path/to/source/directory"
save_directory = "path/to/save/directory"
query = "your search query"

file_paths = search_folder(source_directory, save_directory, query)
print(file_paths)
```

## Contributing

Contributions to the Forcolate library are welcome! If you have ideas for new features, improvements, or bug fixes, please open an issue or submit a pull request.

## Acknowledgement

This project received funding from the French ”IA Cluster” program within the Artificial and Natural Intelligence Toulouse Institute (ANITI) and from the "France 2030" program within IRT Saint Exupery. The authors gratefully acknowledge the support of the FOR projects.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
