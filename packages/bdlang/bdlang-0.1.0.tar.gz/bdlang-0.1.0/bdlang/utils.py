"""
Utility functions for BDLang transpiler
"""

import os
import re
from pathlib import Path

def ensure_file_exists(file_path):
    """
    Check if a file exists
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        bool: True if the file exists, False otherwise
    """
    return os.path.isfile(file_path)

def ensure_bdl_extension(file_path):
    """
    Check if a file has the .bdl extension
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        bool: True if the file has the .bdl extension, False otherwise
    """
    return file_path.lower().endswith('.bdl')

def get_py_file_path(bdl_file_path, output_dir=None):
    """
    Generate a Python file path from a BDLang file path
    
    Args:
        bdl_file_path (str): Path to the BDLang file
        output_dir (str, optional): Output directory. Defaults to None.
        
    Returns:
        str: Path to the Python file
    """
    path = Path(bdl_file_path)
    py_filename = path.stem + '.py'
    
    if output_dir:
        output_path = Path(output_dir)
        return str(output_path / py_filename)
    else:
        return str(path.with_suffix('.py'))

def count_leading_spaces(line):
    """
    Count the number of leading spaces in a line
    
    Args:
        line (str): The line to count spaces in
        
    Returns:
        int: Number of leading spaces
    """
    count = 0
    for char in line:
        if char == ' ':
            count += 1
        else:
            break
    return count

def get_indentation_level(line):
    """
    Get the indentation level of a line
    
    Args:
        line (str): The line to check
        
    Returns:
        int: The indentation level (number of leading spaces / 4)
    """
    spaces = count_leading_spaces(line)
    return spaces // 4

def format_python_code(code):
    """
    Format Python code with proper indentation
    
    Args:
        code (str): Unformatted Python code
        
    Returns:
        str: Formatted Python code
    """
    # This is a simple formatter - for production use, 
    # consider using a proper code formatter like Black
    lines = code.split('\n')
    formatted_lines = []
    
    indentation = 0
    for line in lines:
        stripped = line.strip()
        
        # Decrease indentation for lines ending a block
        if stripped.startswith(('elif', 'else:', 'except:', 'finally:', 'except ', 'except(')) or \
           (stripped.startswith(')') and not stripped.endswith(':')):
            indentation -= 1
        
        # Add the line with proper indentation
        if stripped:  # Skip empty lines for indentation
            formatted_lines.append(' ' * (4 * indentation) + stripped)
        else:
            formatted_lines.append('')
        
        # Increase indentation for lines starting a new block
        if stripped.endswith(':') and not stripped.startswith(('#', '"""', "'''")):
            indentation += 1
    
    return '\n'.join(formatted_lines)
