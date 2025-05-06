"""
File utilities for InertiaSSRPrepper
"""
import os
from pathlib import Path
import mimetypes

# Initialize mimetypes
mimetypes.init()

# Text file extensions to consider
TEXT_EXTENSIONS = {
    '.js', '.jsx', '.ts', '.tsx', '.vue', '.php', '.blade.php', '.html', '.htm',
    '.css', '.scss', '.sass', '.less', '.json', '.md', '.txt', '.env', '.config',
}

# File types for categorization
FILE_TYPES = {
    'frontend': {'.js', '.jsx', '.ts', '.tsx', '.vue', '.css', '.scss', '.sass', '.less'},
    'backend': {'.php', '.blade.php'},
    'config': {'.json', '.env', '.yml', '.yaml', '.xml', '.config'},
    'markup': {'.html', '.htm', '.md', '.markdown'},
    'other': set(),  # Fallback
}

def is_text_file(file_path: Path) -> bool:
    """
    Check if a file is a text file
    """
    # Check by extension first
    ext = ''.join(file_path.suffixes)  # Handle multiple extensions like .blade.php
    if ext.lower() in TEXT_EXTENSIONS:
        return True
    
    # Check by mime type
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if mime_type and mime_type.startswith('text/'):
        return True
    
    # Try to open and read a bit of the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(512)  # Try to read some of the file
        return True
    except (UnicodeDecodeError, IOError):
        return False
        
def get_file_type(file_path: Path) -> str:
    """
    Get the type of file for categorization
    """
    # Get the file extension
    ext = ''.join(file_path.suffixes).lower()  # Handle multiple extensions like .blade.php
    
    # Specific Laravel/Inertia file detection
    filename = file_path.name.lower()
    
    # Laravel specific files
    if 'controller' in filename and ext == '.php':
        return 'controller'
    if 'model' in filename and ext == '.php':
        return 'model'
    if ext == '.blade.php':
        return 'blade'
    
    # Inertia/Vue specific files
    if ext == '.vue':
        return 'vue'
    
    # Check file type categories
    for category, extensions in FILE_TYPES.items():
        if ext in extensions:
            return category
    
    # Return the extension if no category match
    if ext:
        return ext.lstrip('.')
    else:
        return 'other'

def get_relative_path(root_path: Path, file_path: Path) -> str:
    """
    Get a clean relative path from root to file path
    """
    try:
        return str(file_path.relative_to(root_path))
    except ValueError:
        return str(file_path)