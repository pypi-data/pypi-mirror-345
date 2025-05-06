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
    '.js', '.jsx', '.ts', '.tsx', '.vue', '.blade.php', '.html', '.htm',
    '.css', '.scss', '.sass', '.less',
}

# Text file extensions to explicitly ignore
IGNORED_EXTENSIONS = {
    '.txt', '.json', '.sql', '.md', '.csv', '.xml', '.yaml', '.yml', '.toml', 
    '.config', '.lock', '.env', '.example', '.gitignore', '.prettierrc', '.eslintrc',
    '.babelrc', '.editorconfig', '.htaccess', '.log', '.sh', '.bat', '.ps1', '.py',
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
    Check if a file is a text file we should scan for SSR issues
    """
    # Skip files that start with a dot (e.g. .gitignore, .env)
    if file_path.name.startswith('.'):
        return False
        
    # Handle multiple extensions like .blade.php
    ext = ''.join(file_path.suffixes).lower()
    
    # First check if it's a file type we explicitly want to include
    if ext in TEXT_EXTENSIONS:
        return True
    
    # Special handling for PHP files:
    # - Include .blade.php (which should be in TEXT_EXTENSIONS)
    # - Exclude regular .php files
    if ext == '.php':
        return False
        
    # Skip explicitly ignored extensions
    if ext in IGNORED_EXTENSIONS:
        return False
    
    # Skip files that don't have explicit extension approval
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