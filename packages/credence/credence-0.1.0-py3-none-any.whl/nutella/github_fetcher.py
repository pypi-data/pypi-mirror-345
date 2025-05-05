"""
GitHub Fetcher module for Nutella package
"""

import os
import requests
from pathlib import Path

# Target GitHub repository
GITHUB_REPO_OWNER = "Tanmay-24"
GITHUB_REPO_NAME = "CL3"

def fetch(number):
    """
    Fetch a file by number from the GitHub repository.
    
    Args:
        number (int): The file number to fetch
        
    Returns:
        str: Path to the downloaded file
    """
    # Convert number to string for filename
    file_name = f"{number}.txt"
    
    # Create a directory for saving files if it doesn't exist
    output_dir = Path.cwd()
    os.makedirs(output_dir, exist_ok=True)
    
    # Destination path for the downloaded file
    output_path = os.path.join(output_dir, file_name)
    
    try:
        # Build the raw content URL
        raw_url = f"https://raw.githubusercontent.com/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/main/{file_name}"
        
        # Download the file
        print(f"Fetching {file_name} from GitHub...")
        response = requests.get(raw_url)
        response.raise_for_status()  # Raise an error for bad status codes
        
        # Save the content to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"Successfully downloaded {file_name}")
        return output_path
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        return None 