# Credence

A simple Python package to fetch files by number from a GitHub repository.

## Installation

```bash
pip install credence
```

## Usage

The package provides a very simple interface to fetch files by number from a predefined GitHub repository:

```python
from credence import fetch

# Fetch file number 1 (1.txt from the repository)
fetch(1)
```

This will download the file named "1.txt" from the GitHub repository to your current working directory.

## How it Works

The package automatically connects to the GitHub repository at https://github.com/Tanmay-24/CL3 and fetches the file with the corresponding number. 

No configuration or setup is needed on the client side. Just import and use!

## Requirements

- Python 3.6+
- requests library