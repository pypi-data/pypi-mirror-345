# Syntax mappings from Bangla to Python
"""
BDLang Syntax Rules Module
--------------------------

This module defines the grammar and syntax rules for the BDLang programming language,
mapping Bangla programming constructs to their Python equivalents.

The module provides:
- Keyword mappings (control flow, functions, etc.)
- Operator mappings (mathematical, logical, etc.)
- Number mappings (Bangla words and numerals to Python numbers)
- Special character mappings
- Token translation utilities

Examples:
    - "যদি" → "if"
    - "প্রিন্ট" → "print"
    - "যোগ" → "+"
    - "এক" → "1"
    - "১" → "1"
"""

# Import custom error classes
from bdlang.errors import InvalidTokenError
from typing import Dict, Union

# Keyword mappings
KEYWORD_MAP: Dict[str, str] = {
    # Control flow
    "যদি": "if",
    "না_হলে": "else",
    "অথবা_যদি": "elif",
    "লুপ": "for",
    "মধ্যে": "in",      # Added for loop constructs: "for x in range"
    "যতক্ষণ": "while",
    "থেকে": "from",
    "ইমপোর্ট": "import",
    "রিটার্ন": "return",
    "পাস": "pass",
    "ব্রেক": "break",
    "কন্টিনিউ": "continue",
    "শেষ": "pass",     # End/termination indicator
    # Functions and classes
    "ডেফ": "def",
    "ক্লাস": "class",
    
    # Builtins
    "প্রিন্ট": "print",
    "ইনপুট": "input",
    "রেঞ্জ": "range",
    "লেন": "len",
    
    # Boolean operators
    "এবং": "and",
    "অথবা": "or",
    "না": "not",
    
    # Boolean values
    "সত্য": "True",
    "মিথ্যা": "False",
    "নান": "None",
}

# Number mappings
NUMBER_MAP: Dict[str, str] = {
    # Bangla words to numeric values
    "শূন্য": "0",
    "এক": "1",
    "দুই": "2",
    "তিন": "3",
    "চার": "4",
    "পাঁচ": "5",
    "ছয়": "6",
    "সাত": "7",
    "আট": "8",
    "নয়": "9",
    "দশ": "10",
    
    # Bangla numerals to English numerals
    "০": "0",
    "১": "1",
    "২": "2",
    "৩": "3",
    "৪": "4",
    "৫": "5",
    "৬": "6",
    "৭": "7",
    "৮": "8",
    "৯": "9",
}

# Operator mappings
OPERATOR_MAP: Dict[str, str] = {
    # Assignment and comparison
    "=": "=",
    "==": "==",
    "!=": "!=",
    "<": "<",
    ">": ">",
    "<=": "<=",
    ">=": ">=",
    
    # Basic arithmetic (symbol form)
    "+": "+",
    "-": "-",
    "*": "*",
    "/": "/",
    "%": "%",
    "**": "**",
    "//": "//",
    
    # Bangla word operators
    "যোগ": "+",        # Addition
    "বিয়োগ": "-",      # Subtraction
    "গুণ": "*",        # Multiplication
    "ভাগ": "/",        # Division
    "মডুলাস": "%",     # Modulus
    "পাওয়ার": "**",    # Exponentiation
    "পূর্ণভাগ": "//",   # Integer division
}

# Special characters
SPECIAL_CHARS: Dict[str, str] = {
    ":": ":",
    "(": "(",
    ")": ")",
    "[": "[",
    "]": "]",
    "{": "{",
    "}": "}",
    ",": ",",
    ".": ".",
}

# Combine all rules for ease of access
RULES: Dict[str, str] = {**KEYWORD_MAP, **NUMBER_MAP}

def translate_token(token: str) -> str:
    """
    Translate a single token from Bangla to Python
    
    This function maps Bangla language tokens to their Python equivalents
    based on the defined mapping dictionaries.
    
    Examples:
        - translate_token("যদি") -> "if"
        - translate_token("এক") -> "1"
        - translate_token("১") -> "1"
        - translate_token("যোগ") -> "+"
    
    Args:
        token (str): The Bangla token to translate
        
    Returns:
        str: The Python equivalent of the token, or the original token if no mapping found
        
    Raises:
        InvalidTokenError: If strict mode is enabled and no mapping is found
    """
    # Check if it's a keyword or number (highest priority)
    if token in RULES:
        return RULES[token]
    
    # Check if it's an operator
    if token in OPERATOR_MAP:
        return OPERATOR_MAP[token]
    
    # Check if it's a special character
    if token in SPECIAL_CHARS:
        return SPECIAL_CHARS[token]
    
    # If no match found, return the original token
    # In the future, this could raise an exception in strict mode
    return token


def is_bangla_number(token: str) -> bool:
    """
    Check if the token is a Bangla number (either a word or numeral)
    
    Args:
        token (str): The token to check
        
    Returns:
        bool: True if the token is a Bangla number, False otherwise
    """
    return token in NUMBER_MAP
