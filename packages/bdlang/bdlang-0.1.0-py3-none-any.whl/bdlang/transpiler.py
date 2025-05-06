# Transpiler: Converts Bangla code to Python code
def transpile(bangla_code: str) -> str:
    """
    Transpile Bangla code to Python code
    
    Args:
        bangla_code (str): Bangla code to transpile
        
    Returns:
        str: Transpiled Python code
        
    Raises:
        TranspilerError: If there is an error during transpilation
    """
    # Import here to avoid circular imports
    from .tokenizer import Tokenizer
    from .parser import parse
    
    try:
        # Step 1: Tokenize the input
        tokenizer = Tokenizer()
        tokens = tokenizer.tokenize(bangla_code)
        
        # Step 2: Parse the tokens into an AST
        ast = parse(tokens)
        
        # Step 3: Generate Python code from the AST
        python_code = ast.generate_python()
        
        return python_code
    except Exception as e:
        raise TranspilerError(f"Error transpiling code: {e}")

from typing import Optional

def transpile_file(file_path: str) -> str:
    """
    Transpile a BDLang file to Python code
    
    Args:
        file_path (str): Path to the BDLang file
        
    Returns:
        str: Transpiled Python code
        
    Raises:
        TranspilerError: If file is not found or there is an error reading/transpiling the file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            bangla_code = file.read()
        return transpile(bangla_code)
    except FileNotFoundError:
        raise TranspilerError(f"File not found: {file_path}")
    except Exception as e:
        raise TranspilerError(f"Error reading file {file_path}: {e}")
