"""
Error classes for BDLang transpiler
"""

from typing import Optional, Any

class BDLangError(Exception):
    """Base class for all BDLang-specific errors"""
    pass

class TokenizerError(BDLangError):
    """Error during tokenization phase"""
    
    def __init__(self, message: str, line: Optional[int] = None, column: Optional[int] = None) -> None:
        self.line = line
        self.column = column
        self.message = message
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        """Format the error message with line and column information if available"""
        if self.line is not None and self.column is not None:
            return f"Tokenizer error at line {self.line}, column {self.column}: {self.message}"
        return f"Tokenizer error: {self.message}"

class ParserError(BDLangError):
    """Error during parsing phase"""
    
    def __init__(self, message: str, token: Optional[Any] = None) -> None:
        self.token = token
        self.message = message
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        """Format the error message with token information if available"""
        if self.token:
            return f"Parser error at line {self.token.line}, column {self.token.column}: {self.message}"
        return f"Parser error: {self.message}"

class TranspilerError(BDLangError):
    """Error during transpilation phase"""
    pass

class InvalidTokenError(TokenizerError):
    """Invalid token encountered during tokenization or translation"""
    pass

class SyntaxError(ParserError):
    """Syntax error in the BDLang code"""
    pass

class UnsupportedFeatureError(TranspilerError):
    """Feature not supported by the transpiler"""
    pass
