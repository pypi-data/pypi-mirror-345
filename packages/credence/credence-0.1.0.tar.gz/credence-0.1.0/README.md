# Nutella

A simple Python package to fetch files by number from a GitHub repository.

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/nutella.git
cd nutella

# Install in development mode
pip install -e .
```

## Usage

The package provides a very simple interface to fetch files by number from a predefined GitHub repository:

```python
from nutella import fetch

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