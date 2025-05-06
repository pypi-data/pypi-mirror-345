#!/usr/bin/env python3
import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

from .tokenizer import Tokenizer
from .parser import Parser
from .transpiler import transpile_file
from .utils import ensure_file_exists, ensure_bdl_extension, get_py_file_path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

def parse_args() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="BDLang - Transpile Bangla-written code to Python!",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "input_file",
        help="The BDLang (.bdl) file to transpile"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output Python file path (default: same name as input file with .py extension)"
    )
    
    parser.add_argument(
        "--show",
        action="store_true",
        help="Display generated Python code without saving to file"
    )
    
    parser.add_argument(
        "--tokens",
        action="store_true",
        help="Display tokens (for debugging)"
    )
    
    parser.add_argument(
        "--run",
        action="store_true",
        help="Run the transpiled Python code after generating it"
    )
    
    return parser.parse_args()

def validate_input_file(file_path: str) -> bool:
    """Validate the input file exists and has the correct extension"""
    try:
        if not ensure_file_exists(file_path):
            logger.error(f"Input file '{file_path}' does not exist")
            return False
            
        if not ensure_bdl_extension(file_path):
            logger.warning(f"Input file '{file_path}' does not have .bdl extension")
        
        return True
    except Exception as e:
        logger.error(f"Error validating input file: {e}")
        return False

def get_output_file_path(input_file: str, output_file: Optional[str] = None) -> str:
    """Generate output file path if not specified"""
    try:
        if output_file:
            return output_file
        return get_py_file_path(input_file)
    except Exception as e:
        logger.error(f"Error generating output file path: {e}")
        raise

def process_file(input_file: str, show_tokens: bool = False) -> Optional[str]:
    """Process a BDLang file, showing tokens if requested"""
    try:
        # Tokenize the input file
        tokenizer = Tokenizer()
        tokens = tokenizer.tokenize_file(input_file)
        
        if show_tokens:
            logger.info("Tokens:")
            for token in tokens:
                logger.info(f"  {token}")
            logger.info("")
        
        # Transpile the file using the transpile_file function
        python_code = transpile_file(input_file)
        return python_code
    
    except Exception as e:
        logger.error(f"Error during transpilation: {e}")
        return None

def main() -> None:
    """Main entry point for the CLI"""
    args = parse_args()
    
    # Validate input file
    if not validate_input_file(args.input_file):
        sys.exit(1)
    
    # Process the file
    python_code = process_file(args.input_file, args.tokens)
    if python_code is None:
        sys.exit(1)
    
    # Display or save the output
    if args.show:
        logger.info("Generated Python code:")
        logger.info("-" * 40)
        logger.info(python_code)
        logger.info("-" * 40)
    else:
        output_file = get_output_file_path(args.input_file, args.output)
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(python_code)
            logger.info(f"✅ Successfully transpiled to: {output_file}")
        except Exception as e:
            logger.error(f"Error writing output file: {e}")
            sys.exit(1)
    
    # Run the Python code if requested
    if args.run:
        try:
            output_file = get_output_file_path(args.input_file, args.output)
            logger.info(f"🚀 Running the transpiled code: {output_file}")
            
            # Create a restricted namespace for execution
            restricted_globals: Dict[str, Any] = {
                '__builtins__': {
                    name: getattr(__builtins__, name)
                    for name in ['print', 'len', 'range', 'str', 'int', 'float', 'bool']
                }
            }
            restricted_locals: Dict[str, Any] = {}
            
            exec(python_code, restricted_globals, restricted_locals)
        except Exception as e:
            logger.error(f"Error running Python code: {e}")
            sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()
