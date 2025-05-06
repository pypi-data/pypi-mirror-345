import re
from .syntax_rules import KEYWORD_MAP, NUMBER_MAP, OPERATOR_MAP, SPECIAL_CHARS

class Token:
    """Represents a token in the BDLang language"""
    
    def __init__(self, type, value, line=None, column=None):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"Token({self.type}, {self.value})"


class Tokenizer:
    """Tokenizer for BDLang that converts Bangla code into tokens"""
    
    def __init__(self):
        # Build a regex pattern for operators - sorted by length to match longest first
        operator_pattern = '|'.join(
            re.escape(op) for op in sorted(OPERATOR_MAP.keys(), key=len, reverse=True)
        )
        
        # Build pattern for special characters
        special_char_pattern = '|'.join(re.escape(char) for char in SPECIAL_CHARS.keys())
        
        # Token patterns
        self.token_patterns = [
            ('STRING', r'"[^"]*"'),  # String literals
            ('OPERATOR', operator_pattern),  # Operators like ==, +, etc.
            ('SPECIAL_CHAR', special_char_pattern),  # Special characters like :, (, ), etc.
            ('KEYWORD', r'[^\s\d"\'(){}\[\]:;,.<>=!+\-*/&|^%]+'),  # Keywords and identifiers
            ('WHITESPACE', r'\s+'),  # Whitespace
        ]
        
        # Compile regex patterns
        self.patterns = []
        for token_type, pattern in self.token_patterns:
            if pattern:  # Ensure pattern is not empty
                self.patterns.append((token_type, re.compile(pattern)))
    
    def tokenize(self, code):
        """
        Convert BDLang code into a list of tokens
        
        Args:
            code (str): The BDLang code to tokenize
            
        Returns:
            list: A list of Token objects
        """
        tokens = []
        line_num = 1
        column = 1
        position = 0
        
        while position < len(code):
            matched = False
            
            for token_type, pattern in self.patterns:
                match = pattern.match(code, position)
                if match:
                    value = match.group(0)
                    
                    # Skip whitespace tokens but update line/column counters
                    if token_type == 'WHITESPACE':
                        newlines = value.count('\n')
                        if newlines > 0:
                            line_num += newlines
                            column = len(value) - value.rfind('\n')
                        else:
                            column += len(value)
                    else:
                        # Create token for non-whitespace matches
                        tokens.append(Token(token_type, value, line_num, column))
                        column += len(value)
                    
                    position = match.end()
                    matched = True
                    break
            
            if not matched:
                # Handle unrecognized character
                char = code[position]
                tokens.append(Token('UNKNOWN', char, line_num, column))
                position += 1
                column += 1
        
        return tokens

    def tokenize_file(self, file_path):
        """
        Tokenize a BDLang file
        
        Args:
            file_path (str): Path to the BDLang file
            
        Returns:
            list: A list of Token objects
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            code = file.read()
        
        return self.tokenize(code)

    def get_token_values(self, tokens):
        """
        Extract just the values from a list of tokens
        
        Args:
            tokens (list): List of Token objects
            
        Returns:
            list: A list of token values
        """
        return [token.value for token in tokens]


def tokenize(code):
    """
    Convenience function to tokenize BDLang code
    
    Args:
        code (str): The BDLang code to tokenize
        
    Returns:
        list: A list of token values
    """
    tokenizer = Tokenizer()
    tokens = tokenizer.tokenize(code)
    return tokenizer.get_token_values(tokens)


def tokenize_file(file_path):
    """
    Convenience function to tokenize a BDLang file
    
    Args:
        file_path (str): Path to the BDLang file
        
    Returns:
        list: A list of token values
    """
    tokenizer = Tokenizer()
    tokens = tokenizer.tokenize_file(file_path)
    return tokenizer.get_token_values(tokens)

