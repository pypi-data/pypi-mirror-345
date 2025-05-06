from typing import List, Optional, Union
from .tokenizer import Tokenizer, Token
from .syntax_rules import translate_token, KEYWORD_MAP, NUMBER_MAP, OPERATOR_MAP, SPECIAL_CHARS
from .errors import ParserError

class Node:
    """Base class for all AST nodes"""
    
    def generate_python(self) -> str:
        """Generate Python code from this node"""
        raise NotImplementedError("Subclasses must implement generate_python()")


class ProgramNode(Node):
    """Represents a full program"""
    
    def __init__(self, statements: Optional[List[Node]] = None) -> None:
        self.statements = statements or []
    
    def generate_python(self) -> str:
        return "\n".join(stmt.generate_python() for stmt in self.statements)


class PrintNode(Node):
    """Represents a print statement"""
    
    def __init__(self, expression: Node) -> None:
        self.expression = expression
    
    def generate_python(self) -> str:
        return f"print({self.expression.generate_python()})"


class StringLiteralNode(Node):
    """Represents a string literal"""
    
    def __init__(self, value: str) -> None:
        # Strip the quotes from the tokenized string
        self.value = value[1:-1] if value.startswith('"') and value.endswith('"') else value
    
    def generate_python(self) -> str:
        return f'"{self.value}"'


class IdentifierNode(Node):
    """Represents an identifier or a keyword"""
    
    def __init__(self, name: str) -> None:
        self.name = name
    
    def generate_python(self) -> str:
        # Translate the identifier to Python
        return translate_token(self.name)


class BinaryOperationNode(Node):
    """Represents a binary operation (like comparison)"""
    
    def __init__(self, left: Node, operator: str, right: Node) -> None:
        self.left = left
        self.operator = operator
        self.right = right
    
    def generate_python(self) -> str:
        left_code = self.left.generate_python()
        right_code = self.right.generate_python()
        op_code = translate_token(self.operator)
        return f"{left_code} {op_code} {right_code}"


class IfNode(Node):
    """Represents an if statement"""
    
    def __init__(self, condition: Node, body: Optional[List[Node]] = None) -> None:
        self.condition = condition
        self.body = body or []
    
    def generate_python(self) -> str:
        condition_code = self.condition.generate_python()
        body_code = "\n    ".join(stmt.generate_python() for stmt in self.body) if self.body else "pass"
        return f"if {condition_code}:\n    {body_code}"


class Parser:
    """Parser for BDLang that converts tokens into an AST"""
    
    def __init__(self, tokens: Optional[List[Token]] = None) -> None:
        self.tokens = tokens or []
        self.current_pos = 0
    
    def parse(self, tokens: Optional[List[Token]] = None) -> ProgramNode:
        """
        Parse a list of tokens into an AST
        
        Args:
            tokens (list): List of Token objects to parse
            
        Returns:
            ProgramNode: The root node of the AST
        """
        if tokens is not None:
            self.tokens = tokens
            self.current_pos = 0
        
        program = ProgramNode()
        
        while self.current_pos < len(self.tokens):
            statement = self.parse_statement()
            if statement:
                program.statements.append(statement)
            else:
                token = self.current_token()
                if token:
                    raise ParserError(f"Unexpected token: {token.value}", token)
        
        return program

    def current_token(self) -> Optional[Token]:
        """Get the current token"""
        if self.current_pos < len(self.tokens):
            return self.tokens[self.current_pos]
        return None
    
    def peek_token(self, offset: int = 1) -> Optional[Token]:
        """Look ahead at upcoming tokens without consuming them"""
        pos = self.current_pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None
    
    def consume_token(self) -> Optional[Token]:
        """Consume the current token and advance position"""
        token = self.current_token()
        self.current_pos += 1
        return token
    
    def match_token_value(self, value: str) -> bool:
        """Check if the current token matches the expected value"""
        token = self.current_token()
        if token and token.value == value:
            self.consume_token()
            return True
        return False
    
    def match_token_type(self, type: str) -> Optional[Token]:
        """Check if the current token matches the expected type"""
        token = self.current_token()
        if token and token.type == type:
            return self.consume_token()
        return None

    def parse_statement(self) -> Optional[Node]:
        """Parse a single statement"""
        token = self.current_token()
        
        if not token:
            return None
        
        # Print statement: প্রিন্ট ...
        if token.value == 'প্রিন্ট':
            return self.parse_print_statement()
        
        # If statement: যদি ...
        elif token.value == 'যদি':
            return self.parse_if_statement()
        
        # Unknown statement type
        raise ParserError(f"Unknown statement type: {token.value}", token)
    
    def parse_print_statement(self) -> PrintNode:
        """Parse a print statement"""
        self.consume_token()  # Consume 'প্রিন্ট'
        
        # Check for opening parenthesis
        if self.match_token_value('('):
            # Parse the expression to print
            expression = self.parse_expression()
            if not expression:
                raise ParserError("Expected expression after print", self.current_token())
            
            # Expect closing parenthesis
            if not self.match_token_value(')'):
                raise ParserError("Expected closing parenthesis", self.current_token())
            return PrintNode(expression)
        
        # Handle print without parentheses (just a single expression)
        expression = self.parse_expression()
        if not expression:
            raise ParserError("Expected expression after print", self.current_token())
        return PrintNode(expression)
    
    def parse_if_statement(self) -> IfNode:
        """Parse an if statement"""
        self.consume_token()  # Consume 'যদি'
        
        # Parse the condition
        condition = self.parse_expression()
        if not condition:
            raise ParserError("Expected condition after if", self.current_token())
        
        # Check for colon
        if not self.match_token_value(':'):
            raise ParserError("Expected colon after if condition", self.current_token())
        
        # Create an if node with the condition
        if_node = IfNode(condition)
        
        # Parse the body statements
        # TODO: Add proper indentation handling
        while self.current_pos < len(self.tokens):
            token = self.current_token()
            if token and token.value not in ['না_হলে', 'অথবা_যদি']:
                statement = self.parse_statement()
                if statement:
                    if_node.body.append(statement)
                else:
                    break
            else:
                break
        
        return if_node
    
    def parse_expression(self) -> Optional[Node]:
        """Parse an expression"""
        left = self.parse_primary_expression()
        
        # No left expression found
        if left is None:
            return None
        
        # Check for binary operators
        token = self.current_token()
        if token and (token.type == 'OPERATOR' or token.value in OPERATOR_MAP):
            operator = self.consume_token().value
            right = self.parse_primary_expression()
            if not right:
                raise ParserError("Expected right operand after operator", self.current_token())
            return BinaryOperationNode(left, operator, right)
        
        return left
    
    def parse_primary_expression(self) -> Optional[Node]:
        """Parse a primary expression (identifier, literal, etc.)"""
        token = self.current_token()
        
        if not token:
            return None
        
        if token.type == 'STRING':
            return StringLiteralNode(self.consume_token().value)
        
        if token.type == 'KEYWORD':
            return IdentifierNode(self.consume_token().value)
        
        if token.type == 'OPERATOR' and token.value in ['+', '-']:
            # TODO: Implement proper unary operator handling
            operator = self.consume_token().value
            expr = self.parse_primary_expression()
            if not expr:
                raise ParserError("Expected expression after unary operator", self.current_token())
            # TODO: Create a UnaryOperationNode
            return expr
        
        if token.type == 'SPECIAL_CHAR' and token.value == '(':
            # Handle parenthesized expressions
            self.consume_token()  # Consume '('
            expr = self.parse_expression()
            if not expr:
                raise ParserError("Expected expression after opening parenthesis", self.current_token())
            if not self.match_token_value(')'):
                raise ParserError("Expected closing parenthesis", self.current_token())
            return expr
        
        if token.type == 'UNKNOWN' and token.value in NUMBER_MAP:
            # Handle Bangla numerals
            return IdentifierNode(self.consume_token().value)
        
        # Skip unknown tokens
        self.consume_token()
        return None


def parse(tokens):
    """
    Parse a list of tokens into an AST
    
    Args:
        tokens (list): List of Token objects to parse
        
    Returns:
        ProgramNode: The root node of the AST
    """
    parser = Parser()
    return parser.parse(tokens)


def parse_file(file_path):
    """
    Parse a BDLang file into an AST
    
    Args:
        file_path (str): Path to the BDLang file
        
    Returns:
        ProgramNode: The root node of the AST
    """
    tokenizer = Tokenizer()
    tokens = tokenizer.tokenize_file(file_path)
    parser = Parser()
    return parser.parse(tokens)


def generate_python(file_path):
    """
    Parse a BDLang file and generate Python code
    
    Args:
        file_path (str): Path to the BDLang file
        
    Returns:
        str: Generated Python code
    """
    ast = parse_file(file_path)
    return ast.generate_python()
