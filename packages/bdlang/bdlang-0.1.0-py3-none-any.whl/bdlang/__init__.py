"""
BDLang Transpiler
----------------

A Bangla-to-Python transpiler that allows writing Python code in Bangla.

This package provides:
- Tokenization of Bangla code
- Parsing of Bangla code into an AST
- Transpilation of Bangla code to Python code
- CLI for transpiling Bangla files to Python files
"""

__version__ = "0.1.0"
__author__ = "BDLang Team"

# Public API
from .tokenizer import tokenize, tokenize_file
from .parser import parse, parse_file
from .transpiler import transpile, transpile_file
